<template>
  <div class="recipe-rating">
    <h2>{{ t.title }}</h2>
    <p class="description">{{ t.description }}</p>

    <div class="disclaimer">
      <strong>{{ t.disclaimerTitle }}</strong>
      <p>{{ t.disclaimerText }}</p>
    </div>

    <div class="progress-indicator">
      {{ t.recipe }} {{ currentRecipeIndex + 1 }} {{ t.of }} {{ recipesWithCheck.length }}
    </div>

    <div v-if="currentRecipe" class="recipe-card">
      <div class="recipe-header">
        <h3>{{ currentRecipe.name }}</h3>
        <img
          v-if="currentRecipe.image"
          :src="currentRecipe.image"
          :alt="currentRecipe.name"
          class="recipe-image"
          @error="handleImageError"
        />
      </div>

      <div class="recipe-details">
        <div class="detail-item" v-if="currentRecipe.ingredients_list && currentRecipe.ingredients_list.length > 0">
          <strong>{{ t.ingredientsLabel }}:</strong>
          <ul class="ingredients-list">
            <li v-for="(ingredient, idx) in getCleanedIngredients(currentRecipe.ingredients_list)" :key="idx">{{ ingredient }}</li>
          </ul>
        </div>

        <div class="detail-item directions-section" v-if="currentRecipe.directions && currentRecipe.directions.length > 0">
          <strong>{{ t.directionsLabel }}:</strong>
          <ol class="directions-list" :class="{ collapsed: !directionsExpanded }" ref="directionsList">
            <li v-for="(step, idx) in currentRecipe.directions" :key="idx">{{ step }}</li>
          </ol>
          <div class="read-more-container">
            <button
              @click="toggleDirections"
              class="read-more-btn"
            >
              {{ directionsExpanded ? '↑ ' + t.readLess : '↓ ' + t.readMore }}
            </button>
          </div>
        </div>

        <div class="detail-item" v-if="currentRecipe.tags && currentRecipe.tags.length > 0">
          <strong>{{ t.tagsLabel }}:</strong>
          <div class="tags-container">
            <span v-for="(tag, idx) in currentRecipe.tags" :key="idx" class="tag">{{ tag }}</span>
          </div>
        </div>

        <!-- Attention Check Instruction (below description, no box) -->
        <div v-if="currentRecipe.isAttentionCheck" class="detail-item attention-check-instruction">
          {{ t.attentionCheckInstruction }}
        </div>
      </div>

      <!-- Scroll indicator arrow -->
      <div v-if="!isTextareaVisible" class="scroll-indicator">
        <div class="arrow-down">↓</div>
      </div>

      <div class="rating-section">
        <div class="rating-input">
          <label>{{ t.ratingLabel }}</label>
          <div class="star-rating">
            <span
              v-for="star in 5"
              :key="star"
              @click="setRating(star)"
              class="star"
              :class="{ filled: star <= ratings[currentRecipe.id]?.score }"
            >
              ★
            </span>
          </div>
          <span class="rating-value">{{ ratings[currentRecipe.id]?.score || 0 }} / 5</span>
        </div>

        <div class="review-input">
          <label>{{ t.reviewLabel }} <span class="required">*</span></label>
          <p class="review-hint">{{ t.reviewHint }}</p>
          <textarea
            ref="reviewTextarea"
            v-model="ratings[currentRecipe.id].review"
            :placeholder="t.reviewPlaceholder"
            rows="4"
            maxlength="500"
          ></textarea>
          <div class="review-stats">
            <span>{{ t.words }}: {{ getReviewWordCount(currentRecipe.id) }}</span>
            <span v-if="getReviewWordCount(currentRecipe.id) < MIN_REVIEW_WORDS" class="warning">
              {{ t.minWordsWarning.replace('{0}', MIN_REVIEW_WORDS) }}
            </span>
          </div>
        </div>
      </div>

      <div class="navigation-buttons">
        <button
          v-if="currentRecipeIndex > 0"
          @click="previousRecipe"
          class="btn-secondary"
        >
          {{ t.previous }}
        </button>

        <button
          v-if="currentRecipeIndex < recipesWithCheck.length - 1"
          @click="nextRecipe"
          class="btn-primary"
          :disabled="!isCurrentRated"
        >
          {{ t.next }}
        </button>

        <button
          v-if="currentRecipeIndex === recipesWithCheck.length - 1"
          @click="submitRatings"
          class="btn-primary"
          :disabled="!allRated"
        >
          {{ t.submit }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  language: {
    type: String,
    required: true
  },
  contextType: {
    type: String,
    required: true
  },
  recipes: {
    type: Array,
    required: true
  },
  phase: {
    type: String,
    default: 'static'
  }
})

const emit = defineEmits(['submit', 'directionsToggle'])

const currentRecipeIndex = ref(0)
const ratings = reactive({})
const reviewTextarea = ref(null)
const directionsList = ref(null)
const isTextareaVisible = ref(false)
const directionsExpanded = ref(false)

// Minimum word count for reviews (can be easily modified)
const MIN_REVIEW_WORDS = 10

/* COMMENTED OUT: Recipe attention check
// Add attention check recipe
const attentionCheckRecipe = {
  id: 'attention-check-recipe',
  name: 'Mediterranean Grilled Chicken',
  image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400',
  description: 'A healthy grilled chicken dish with Mediterranean herbs and lemon.',
  recipe_url: '',
  interactions: '',
  isAttentionCheck: true,
  correctRating: 3
}

// Insert attention check at random position (never first)
const recipesWithCheck = [...props.recipes]
// Random index from 1 to recipesWithCheck.length (never 0)
const attentionCheckIndex = Math.floor(Math.random() * recipesWithCheck.length) + 1
recipesWithCheck.splice(attentionCheckIndex, 0, attentionCheckRecipe)
*/

// No attention check - just use regular recipes
const recipesWithCheck = [...props.recipes]

// Initialize ratings for all recipes
recipesWithCheck.forEach(recipe => {
  ratings[recipe.id] = {
    score: 0,
    review: ''
  }
})

// Check if textarea (review input) is visible in viewport
function checkTextareaVisibility() {
  if (!reviewTextarea.value) return

  const rect = reviewTextarea.value.getBoundingClientRect()
  const windowHeight = window.innerHeight || document.documentElement.clientHeight

  // Consider visible if the textarea starts entering the viewport (with some threshold)
  isTextareaVisible.value = rect.top < windowHeight - 50
}

// Scroll to top when component mounts (first recipe loads)
onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'smooth' })

  // Set up scroll listener
  window.addEventListener('scroll', checkTextareaVisibility)
  // Initial check
  setTimeout(checkTextareaVisibility, 100)
})

onUnmounted(() => {
  window.removeEventListener('scroll', checkTextareaVisibility)
})

const translations = {
  en: {
    title: 'Rate Recipes',
    description: 'Please rate each recipe based on your preferences. Consider how much you would like to try this recipe.',
    disclaimerTitle: 'Important Note:',
    disclaimerText: 'The recipes you will see are chosen at random. The ratings you provide help us understand how your personal preferences and background influence your food choices. Your honest feedback is valuable for our research.',
    attentionCheckInstruction: 'Please rate this recipe 3 / 5',
    recipe: 'Recipe',
    of: 'of',
    ingredientsLabel: 'Ingredients',
    directionsLabel: 'Directions',
    tagsLabel: 'Tags',
    ratingLabel: 'Your Rating (1-5 stars)',
    reviewLabel: 'Review (Required)',
    reviewPlaceholder: 'Why is this recipe suitable/unsuitable for you? Consider referencing your personal background, dietary preferences, or lifestyle from your questionnaire answers.',
    reviewHint: 'Tip: Support your review with references to your biography or questionnaire responses (e.g., dietary restrictions, health goals, taste preferences, lifestyle habits).',
    words: 'Words',
    minWordsWarning: 'Please write at least {0} words',
    readMore: 'Read more',
    readLess: 'Read less',
    previous: 'Previous',
    next: 'Next',
    submit: 'Submit All Ratings'
  }
}

const t = computed(() => translations[props.language])

const currentRecipe = computed(() => recipesWithCheck[currentRecipeIndex.value])

function countWords(text) {
  if (!text) return 0
  return text.trim().split(/\s+/).filter(w => w.length > 0).length
}

function getReviewWordCount(recipeId) {
  const review = ratings[recipeId]?.review || ''
  return countWords(review)
}

const isCurrentRated = computed(() => {
  const rating = ratings[currentRecipe.value?.id]
  return rating && rating.score > 0 && getReviewWordCount(currentRecipe.value?.id) >= MIN_REVIEW_WORDS
})

const allRated = computed(() => {
  return recipesWithCheck.every(recipe =>
    ratings[recipe.id]?.score > 0 && getReviewWordCount(recipe.id) >= MIN_REVIEW_WORDS
  )
})

function setRating(score) {
  ratings[currentRecipe.value.id].score = score
}

function toggleDirections() {
  const action = directionsExpanded.value ? 'collapse' : 'expand'

  // Emit event for logging
  emit('directionsToggle', {
    action,
    recipeId: currentRecipe.value?.id,
    recipeName: currentRecipe.value?.name
  })

  if (directionsExpanded.value) {
    // COLLAPSING: First scroll up, then collapse
    if (directionsList.value) {
      const directionsSection = directionsList.value.closest('.directions-section')
      if (directionsSection) {
        const rect = directionsSection.getBoundingClientRect()
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop
        const targetPosition = scrollTop + rect.top - 20 // Small offset from top

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        })
      }
    }

    // Wait for scroll to complete, then trigger collapse animation
    setTimeout(() => {
      directionsExpanded.value = false
    }, 500) // Wait for smooth scroll to mostly complete
  } else {
    // EXPANDING: First expand, then scroll
    directionsExpanded.value = true

    // Wait for the animation to complete (600ms transition) before scrolling
    setTimeout(() => {
      if (directionsList.value) {
        const directionsSection = directionsList.value.closest('.directions-section')
        if (directionsSection) {
          const rect = directionsSection.getBoundingClientRect()
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop
          const targetPosition = scrollTop + rect.top - 100 // Offset from top

          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          })
        }
      }
    }, 650) // Wait for the 600ms animation to complete, plus small buffer
  }
}

function nextRecipe() {
  if (currentRecipeIndex.value < recipesWithCheck.length - 1 && isCurrentRated.value) {
    currentRecipeIndex.value++
    directionsExpanded.value = false
    // Smooth scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function previousRecipe() {
  if (currentRecipeIndex.value > 0) {
    currentRecipeIndex.value--
    directionsExpanded.value = false
    // Smooth scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function submitRatings() {
  if (allRated.value) {
    // No attention check - submit all recipes
    const ratingsData = recipesWithCheck.map(recipe => ({
      recipeId: recipe.id,
      recipeName: recipe.name,
      score: ratings[recipe.id].score,
      review: ratings[recipe.id].review
    }))

    emit('submit', ratingsData)
  }
}

function handleImageError(event) {
  // Hide broken images to prevent 404 errors
  event.target.style.display = 'none'
  console.warn('Failed to load recipe image:', event.target.src)
}

function getCleanedIngredients(ingredients) {
  // Filter out ingredients containing $template2$ and trim whitespace
  return ingredients
    .filter(ing => !ing.includes('$template2$'))
    .map(ing => ing.trim())
    .filter(ing => ing.length > 0)
}
</script>

<style scoped>
.recipe-rating {
  padding: 1rem;
}

h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

.description {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.disclaimer {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
}

.disclaimer strong {
  display: block;
  color: #1976d2;
  margin-bottom: 0.5rem;
  font-size: 1.05rem;
}

.disclaimer p {
  color: #555;
  line-height: 1.6;
  margin: 0;
}

.progress-indicator {
  background: #667eea;
  color: white;
  padding: 0.75rem;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
  margin-bottom: 2rem;
}

.recipe-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 2rem;
  background: #fafafa;
}

.recipe-header {
  margin-bottom: 2rem;
}

.recipe-header h3 {
  color: #333;
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.recipe-image {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.recipe-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.detail-item strong {
  color: #667eea;
  display: block;
  margin-bottom: 0.5rem;
}

.rating-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.rating-input {
  margin-bottom: 2rem;
}

.rating-input label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.75rem;
}

.star-rating {
  display: inline-flex;
  gap: 0.5rem;
  font-size: 2.5rem;
  margin-right: 1rem;
}

.star {
  cursor: pointer;
  color: #ddd;
  transition: color 0.2s ease;
  user-select: none;
}

.star:hover,
.star.filled {
  color: #ffd700;
}

.rating-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #667eea;
}

.review-input label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.review-hint {
  background: #fff9e6;
  border-left: 3px solid #ffa726;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  color: #555;
  line-height: 1.5;
  border-radius: 4px;
}

.review-input textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
}

.review-input textarea:focus {
  outline: none;
  border-color: #667eea;
}

.review-stats {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.review-stats .warning {
  color: #ff6b6b;
  font-weight: 600;
}

.required {
  color: #e74c3c;
  font-weight: bold;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.25rem;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.attention-check-instruction {
  color: #667eea;
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.ingredients-list {
  margin: 0.5rem 0 0 1.5rem;
  padding: 0;
  line-height: 1.4;
  column-count: 2;
  column-gap: 2rem;
}

.ingredients-list li {
  margin-bottom: 0.3rem;
  color: #444;
  break-inside: avoid;
}

.directions-list {
  margin: 0.5rem 0 0 1.5rem;
  padding: 0;
  line-height: 1.6;
  max-height: 5000px; /* Large enough to fit any content */
  overflow: hidden;
  transition: max-height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.directions-list.collapsed {
  max-height: 150px;
}

.directions-list.collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to bottom, transparent, #fafafa);
  pointer-events: none;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.directions-list:not(.collapsed)::after {
  opacity: 0;
}

.directions-list li {
  margin-bottom: 0.5rem;
  color: #444;
}

.read-more-container {
  display: flex;
  justify-content: center;
  margin-top: 0.75rem;
}

.read-more-btn {
  background: transparent;
  border: 1px solid #667eea;
  color: #667eea;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
}

.read-more-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.read-more-btn:active {
  transform: translateY(0);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  background: #e8eaf6;
  color: #5c6bc0;
  padding: 0.4rem 0.8rem;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

.scroll-indicator {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  animation: bounce 2s infinite;
}

.arrow-down {
  font-size: 3rem;
  color: #667eea;
  background: white;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  cursor: pointer;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
</style>
