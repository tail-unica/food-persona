import logging
import os
import random
import sys
import threading
import time
from collections import Counter
from functools import wraps
from random import shuffle
from datetime import datetime
import string
import csv

import mysql.connector
import requests
import simplejson as json
from dotenv import load_dotenv
from flask import Flask, request, Response, stream_with_context
from flask import jsonify
from pydantic import ValidationError
from waitress import serve

def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Changed from WARNING to INFO
    if not logger.handlers:  # Prevent duplicate handlers
        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s",
            datefmt="%Y.%m.%d %H:%M:%S"
        )
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


load_dotenv()

app = Flask(__name__)
lock = threading.Lock()
logger = init_logger()


# Food study configuration
MAX_RECIPE_PROPOSALS = 3  # Maximum times a recipe can be proposed


def get_remote_address():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(",")[0]


def create_db_connection(db=""):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PWD"),
        database=db
    )


def log_to_activity_logs(user_id, activity_type, data, cnx=None):
    """Log activity to the activity_logs table in food_preferences_study database"""
    close_connection = False
    if cnx is None:
        cnx = create_db_connection("food_preferences_study")
        close_connection = True

    cursor = cnx.cursor()
    try:
        query = "INSERT INTO activity_logs (user_id, activity_type, data, timestamp) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query, (user_id, activity_type, json.dumps(data)))
        cnx.commit()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
        cnx.rollback()
    finally:
        cursor.close()
        if close_connection:
            cnx.close()

def should_skip_checks():
    """Determine if captcha and focus checks should be skipped"""
    return request.args.get('beta_testing_passkey') == 'beta-testing-passkey-study'


def handle_cors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            return Response(status=204, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS, GET, POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            })
        return f(*args, **kwargs)

    return wrapper


def verify_recaptcha(token, version='v3'):
    V3_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_V3')
    V2_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_V2')

    secret_key = V3_SECRET_KEY if version == 'v3' else V2_SECRET_KEY
    verification_url = 'https://www.google.com/recaptcha/api/siteverify'

    response = requests.post(verification_url, data={
        'secret': secret_key,
        'response': token
    })

    result = response.json()

    if version == 'v3':
        score = result.get('score', 0)
        return {
            'success': result.get('success', False),
            'score': score,
            'requireV2': score < 0.5  # Threshold for requiring v2 verification
        }
    else:
        return {
            'success': result.get('success', False),
            'requireV2': False
        }



def validate_recaptcha_if_needed(data):
    """Validate reCAPTCHA unless beta passkey is provided"""
    if should_skip_checks():
        return True

    token = data.get('recaptcha_token')
    version = data.get('recaptcha_version', 'v3')

    if not token:
        return {'error': 'reCAPTCHA token required', 'requireV2Verification': False}

    verification = verify_recaptcha(token, version)

    if version == 'v3' and verification['requireV2']:
        return {'requireV2Verification': True}

    if not verification['success']:
        return {'error': 'reCAPTCHA verification failed', 'requireV2Verification': False}

    return True


def generate_user_id():
    """Generate a unique user ID"""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f'user_{timestamp}_{random_str}'


def get_recipe_proposal_counts(cnx=None):
    """
    Get count of how many times each recipe has been proposed.
    Counts both completed users and recent incomplete users (within 10 minutes).

    Returns:
        dict: Dictionary mapping recipe_id to proposal count
    """
    close_connection = False
    if cnx is None:
        cnx = create_db_connection("food_preferences_study")
        close_connection = True

    cursor = cnx.cursor()
    proposal_counts = {}

    try:
        # Get all users who completed the study
        cursor.execute("""
            SELECT user_id
            FROM activity_logs
            WHERE activity_type = 'study_completed'
        """)
        completed_users = set(row[0] for row in cursor.fetchall())

        # Get users who fetched recipes recently (within 10 minutes) but haven't completed
        cursor.execute("""
            SELECT DISTINCT user_id, MAX(timestamp) as last_fetch
            FROM activity_logs
            WHERE activity_type = 'recipes_fetched'
            AND timestamp >= NOW() - INTERVAL 10 MINUTE
            GROUP BY user_id
        """)
        recent_incomplete_users = set(
            row[0] for row in cursor.fetchall()
            if row[0] not in completed_users
        )

        # Combine both sets of users
        all_users = completed_users | recent_incomplete_users

        if all_users:
            # Get recipe proposals for all relevant users
            placeholders = ','.join(['%s'] * len(all_users))
            query = f"""
                SELECT data
                FROM activity_logs
                WHERE activity_type = 'recipes_fetched'
                AND user_id IN ({placeholders})
            """
            cursor.execute(query, tuple(all_users))

            for (data_json,) in cursor.fetchall():
                try:
                    data = json.loads(data_json)
                    recipe_ids = data.get('recipe_ids', [])
                    for recipe_id in recipe_ids:
                        proposal_counts[str(recipe_id)] = proposal_counts.get(str(recipe_id), 0) + 1
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error parsing recipe data: {e}")
                    continue

        logger.info(f"Counted proposals from {len(completed_users)} completed users "
                   f"+ {len(recent_incomplete_users)} recent incomplete users")

    except Exception as e:
        logger.error(f"Error getting recipe proposal counts: {e}")
    finally:
        cursor.close()
        if close_connection:
            cnx.close()

    return proposal_counts


def load_recipes_from_csv():
    """
    Load recipes from CSV file
    """
    recipes = []
    csv_path = os.path.join(os.path.dirname(__file__), 'new-recipes.csv')

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:

                # Parse ingredients_list, directions, and tags (separated by |)
                ingredients_list = row.get('ingredients_list', '').split('|') if row.get('ingredients_list') else []
                directions = row.get('directions', '').split('|') if row.get('directions') else []
                tags = row.get('tags', '').split('|') if row.get('tags') else []

                recipe = {
                    'id': row['recipe_id'],
                    'name': row['title'],
                    'recipe_url': row['recipe_url'],
                    'image': row['image_url'],
                    'ingredients_list': ingredients_list,
                    'directions': directions,
                    'tags': tags,
                    'interactions': row['# Interactions']
                }
                recipes.append(recipe)
    except FileNotFoundError:
        logger.error(f"Warning: new-recipes.csv not found at {csv_path}")
        recipes = []
    except Exception as e:
        logger.error(f"Error loading recipes from CSV: {e}")
        recipes = []

    logger.info(f"Loaded {len(recipes)} recipes")
    return recipes


# ===== FOOD PREFERENCES STUDY ENDPOINTS =====

@app.route('/server/api/logs', methods=['POST', 'OPTIONS'], strict_slashes=False)
@handle_cors
def food_log_activity():
    """Log user activity throughout the study"""
    if request.method == 'OPTIONS':
        return Response(status=204)

    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        activity_type = data.get('type')

        # Validate reCAPTCHA only if token is provided (optional like /llm-log)
        token = data.get('recaptcha_token')
        version = data.get('recaptcha_version', 'v3')

        if token:
            verification = verify_recaptcha(token, version)

            if version == 'v3' and verification['requireV2']:
                return jsonify({'success': False, 'requireV2Verification': True}), 200

            if not verification['success']:
                return jsonify({'success': False, 'error': 'reCAPTCHA verification failed'}), 403

        # Remove recaptcha tokens before storing
        data.pop('recaptcha_token', None)
        data.pop('recaptcha_version', None)

        # Log to activity_logs
        log_to_activity_logs(user_id, activity_type, data)

        # For this study, when recipe ratings are submitted, the study is completed
        # Automatically log study completion
        if activity_type == 'recipe-ratings-static-submitted':
            completion_data = {'status': 'completed'}
            log_to_activity_logs(user_id, 'study_completed', completion_data)
            logger.info(f"User {user_id} completed the study (recipe ratings submitted)")

        return jsonify({'success': True, 'message': 'Log recorded successfully'}), 200

    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/server/api/recipes', methods=['GET', 'OPTIONS'], strict_slashes=False)
@handle_cors
def food_get_recipes():
    """Get recipes for rating (static context phase)"""
    if request.method == 'OPTIONS':
        return Response(status=204)

    try:
        user_id = request.args.get('user_id')

        all_recipes = load_recipes_from_csv()
        proposal_counts = get_recipe_proposal_counts()
        available_recipes = [
            r for r in all_recipes
            if proposal_counts.get(r['id'], 0) < MAX_RECIPE_PROPOSALS
        ]

        recipes_with_2 = [r for r in available_recipes if proposal_counts.get(r['id'], 0) == 2]
        recipes_with_1 = [r for r in available_recipes if proposal_counts.get(r['id'], 0) == 1]
        recipes_with_0 = [r for r in available_recipes if proposal_counts.get(r['id'], 0) == 0]

        logger.info(f"Total recipes: {len(all_recipes)}, "
                   f"Available recipes (not maxed out): {len(available_recipes)}, "
                   f"2-rating: {len(recipes_with_2)}, 1-rating: {len(recipes_with_1)}, 0-rating: {len(recipes_with_0)}")

        selected_recipes = []

        if recipes_with_2:
            selected_recipes.extend(random.sample(recipes_with_2, min(10, len(recipes_with_2))))

        if len(selected_recipes) < 10 and recipes_with_1:
            num_needed = 10 - len(selected_recipes)
            selected_recipes.extend(random.sample(recipes_with_1, min(num_needed, len(recipes_with_1))))

        if len(selected_recipes) < 10 and recipes_with_0:
            num_needed = 10 - len(selected_recipes)
            selected_recipes.extend(random.sample(recipes_with_0, min(num_needed, len(recipes_with_0))))

        random_recipes = selected_recipes

        log_data = {
            'recipe_ids': [r['id'] for r in random_recipes]
        }
        log_to_activity_logs(user_id, 'recipes_fetched', log_data)

        return jsonify({
            'success': True,
            'recipes': random_recipes
        }), 200

    except Exception as e:
        logger.error(f"Error getting recipes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/server/api/study/complete', methods=['POST', 'OPTIONS'], strict_slashes=False)
@handle_cors
def food_complete_study():
    """Mark study as complete"""
    if request.method == 'OPTIONS':
        return Response(status=204)

    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')

        log_data = {
            'status': 'completed'
        }
        log_to_activity_logs(user_id, 'study_completed', log_data)

        return jsonify({
            'success': True,
            'message': 'Study completed successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error completing study: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    # waitress_logger = logging.getLogger('waitress')
    # waitress_logger.setLevel(logging.INFO)
    serve(app, host='0.0.0.0', port=3050)
