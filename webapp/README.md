# Food Preferences Study Application

A web application for conducting research on food preferences.

## Overview

This application consists of:
- **Frontend**: Vue.js 3 single-page application for user interaction
- **Backend**: Flask Python API server for data processing and storage
- **Database**: MySQL for storing user responses and activity logs

## Technology Stack

### Frontend
- Vue.js 3
- Vite (build tool)
- Axios (HTTP client)

### Backend
- Flask (Python web framework)
- MySQL Connector
- Waitress (WSGI server for production)
- python-dotenv (environment management)

## Prerequisites

Before running this application, ensure you have the following installed:

- **Node.js** (v16 or higher) and npm
- **Python** (v3.8 or higher) and pip
- **MySQL** (v8.0 or higher)

## Installation

### 1. Clone the Repository

### 2. Install Frontend Dependencies

```bash
cd webapp
npm install
```

### 3. Install Backend Dependencies

```bash
# From the webapp directory
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create or update the `.env` file in the `webapp` directory with the following configuration:

```env
# Database configuration
DB_HOST=localhost              # MySQL host (default: localhost)
DB_USER=root                   # MySQL username (default: root)
DB_PWD=your_mysql_password     # MySQL password (required)

# API Base URL for development
VITE_API_URL=http://localhost:3000/api

# reCAPTCHA keys (optional, for production)
VITE_RECAPTCHA_V3_SITE_KEY=your_recaptcha_v3_key
VITE_RECAPTCHA_V2_SITE_KEY=your_recaptcha_v2_key
VITE_MAX_RECAPTCHA_CHECKS=2
VITE_RECAPTCHA_TARGET_EVENTS=static-context-submitted,questionnaires-submitted,recipe-ratings-static-submitted

# Prolific integration URLs (optional)
VITE_PROLIFIC_COMPLETED_URL=https://app.prolific.com/submissions/complete?cc=XYZ
VITE_PROLIFIC_TIMEDOUT_URL=https://app.prolific.com/submissions/complete?cc=XYZ
VITE_PROLIFIC_INCOMPATIBLE_URL=https://app.prolific.com/submissions/complete?cc=XYZ
```

**Important:** Replace placeholder values with your actual credentials.

### Database Configuration

The application uses the following environment variables for database connection:
- `DB_HOST` - MySQL server host (defaults to `localhost` if not set)
- `DB_USER` - MySQL username (defaults to `root` if not set)
- `DB_PWD` - MySQL password (required, no default)

## Running the Application

### Development Mode

#### 1. Start the Backend Server

```bash
cd webapp
python server/production_server.py
```

The backend server will start on `http://localhost:3050`

#### 2. Start the Frontend Development Server

In a new terminal window:

```bash
cd webapp
npm run dev
```

The frontend will start on `http://localhost:5173`

#### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

The Vite development server will automatically proxy API requests to the backend server.

### Quick Start (Both Servers)

You can run both servers in separate terminal windows:

**Terminal 1 (Backend):**
```bash
cd webapp
python server/production_server.py
```

**Terminal 2 (Frontend):**
```bash
cd webapp
npm run dev
```

## Project Structure

```
food-persona/
├── webapp/
│   ├── src/
│   │   ├── components/        # Vue components
│   │   │   ├── InformedConsent.vue
│   │   │   ├── StaticContextInput.vue
│   │   │   ├── QuestionnaireSelector.vue
│   │   │   ├── NutritionistQuestionnaire.vue
│   │   │   ├── RecipeRating.vue
│   │   │   └── CompletionScreen.vue
│   │   ├── composables/       # Vue composables
│   │   ├── App.vue            # Main application component
│   │   ├── main.js            # Application entry point
│   │   └── api.js             # API service layer
│   ├── server/
│   │   ├── production_server.py   # Flask backend server
│   │   └── new-recipes.csv        # Recipe database
│   ├── public/                # Static assets
│   ├── .env                   # Environment variables
│   ├── index.html             # HTML entry point
│   ├── package.json           # Node.js dependencies
│   ├── requirements.txt       # Python dependencies
│   └── vite.config.js         # Vite configuration
└── README.md
```

## Database Setup

### 1. Create the Database

Connect to MySQL and create the required database:

```sql
CREATE DATABASE food_preferences_study;
USE food_preferences_study;
```

### 2. Create Required Tables

Create the activity logs table:

```sql
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    data JSON,
    timestamp DATETIME NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_activity_type (activity_type),
    INDEX idx_timestamp (timestamp)
);
```

### 3. Update Database Credentials

Make sure your `.env` file contains the correct MySQL connection settings:

```env
DB_HOST=localhost              # Change if MySQL is on a different host
DB_USER=root                   # Change if using a different MySQL user
DB_PWD=your_mysql_password     # Your MySQL password
```

## Development

### Frontend Development

The frontend uses Vite's hot module replacement (HMR) for fast development:

```bash
npm run dev
```

### Backend Development

For backend changes, restart the Python server after modifications:

```bash
python server/production_server.py
```

### Building for Production

To build the frontend for production:

```bash
npm run build
```

This creates optimized static files in the `dist/` directory.

### Preview Production Build

To preview the production build locally:

```bash
npm run preview
```

## Production Deployment

### Backend Configuration

The production server uses Waitress and runs on port 3050:

```python
serve(app, host='0.0.0.0', port=3050)
```

## API Endpoints

The backend provides the following main endpoints:

- `POST /server/api/logs` - Log user activity
- `POST /server/api/recipes` - Get recipes for rating
- `POST /server/api/study/complete` - Mark study as complete