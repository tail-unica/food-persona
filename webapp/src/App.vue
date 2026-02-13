<template>
  <div id="app">
    <div class="header">
      <h1>{{ t.title }}</h1>
      <div class="header-right">
        <div class="user-id-display" v-if="userId">
          <span class="user-id-label">User ID:</span>
          <span class="user-id-value">{{ userId }}</span>
        </div>
      </div>
    </div>

    <div class="progress-bar" v-if="!showMobileBanner && !maintenanceMode">
      <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
    </div>

    <!-- Maintenance Mode Banner -->
    <div v-if="maintenanceMode" class="maintenance-banner">
      <div class="maintenance-banner-content">
        <h2>{{ maintenanceBannerText[language].title }}</h2>
        <p>{{ maintenanceBannerText[language].message }}</p>
      </div>
    </div>

    <!-- Mobile device banner (shown only for non-Prolific users on mobile) -->
    <div v-if="showMobileBanner" class="mobile-banner">
      <div class="mobile-banner-content">
        <h2>{{ mobileBannerText[language].title }}</h2>
        <p>{{ mobileBannerText[language].message }}</p>
        <button @click="showMobileBanner = false" class="btn-proceed-anyway">
          {{ mobileBannerText[language].proceedButton }}
        </button>
      </div>
    </div>

    <div class="container" v-if="!showMobileBanner && !maintenanceMode">
      <!-- Phase 0: Informed Consent -->
      <informed-consent
        v-if="currentPhase === 'informed-consent'"
        :language="language"
        @submit="handleInformedConsentSubmit"
      />

      <!-- Phase 1.1: Static Context Input -->
      <static-context-input
        v-if="currentPhase === 'static-context'"
        :language="language"
        :beta-testing="betaPasskey === 'beta-testing-passkey-study'"
        @submit="handleStaticContextSubmit"
        @skip="handleStaticContextSubmit({ text: '' })"
      />

      <!-- Phase 1.2: Questionnaires (FCQ and JC) -->
      <questionnaire-selector
        v-if="currentPhase === 'questionnaires'"
        :language="language"
        :static-context="studyData.staticContext"
        :llm-fcq="studyData.llmFCQ"
        :llm-jc="studyData.llmJC"
        :from-prolific="fromProlific"
        :beta-testing="betaPasskey === 'beta-testing-passkey-study'"
        @submit="handleQuestionnaireSubmit"
        @skip="handleQuestionnaireSubmit({ contextType: 'both', fcq: {}, jc: {} })"
      />

      <!-- Phase 1.2.3: Manual Review of LLM-generated context - REMOVED -->
      <!--
      <context-review
        v-if="currentPhase === 'context-review'"
        :language="language"
        :original-text="studyData.staticContext"
        :fcq-data="studyData.llmFCQ"
        :jc-data="studyData.llmJC"
        :user-fcq-data="studyData.userFCQ"
        :user-jc-data="studyData.userJC"
        @submit="handleReviewSubmit"
      />
      -->

      <!-- Phase 1.3.1: Recipe Rating (Static Context) -->
      <div v-if="currentPhase === 'recipe-rating-static'">
        <!-- Recipe rating -->
        <recipe-rating
          :language="language"
          :context-type="studyData.selectedContextType"
          :recipes="studyData.recipesStatic"
          :phase="'static'"
          @submit="handleRecipeRatingSubmit"
          @directions-toggle="handleDirectionsToggle"
        />

        <!-- Reference information section -->
        <div class="reference-section">
          <h3>{{ referenceText[language].title }}</h3>
          <p>{{ referenceText[language].description }}</p>

          <!-- Show biography (disabled) -->
          <static-context-input
            :language="language"
            :disabled="true"
            :initial-value="studyData.staticContext"
          />

          <!-- Show questionnaires (disabled) -->
          <questionnaire-selector
            :language="language"
            :static-context="studyData.staticContext"
            :disabled="true"
            :initial-fcq="studyData.userFCQ"
            :initial-jc="studyData.userJC"
            :from-prolific="fromProlific"
          />
        </div>
      </div>

      <!-- Phase 1.3.3: Compare Human vs LLM ratings - COMMENTED OUT -->
      <!--
      <rating-comparison
        v-if="currentPhase === 'rating-comparison-static'"
        :language="language"
        :human-ratings="studyData.humanRatingsStatic"
        :llm-ratings="studyData.llmRatingsStatic"
        @submit="handleComparisonSubmit"
      />
      -->

      <!-- Phase 1.4.1: Recipe Rating (Dynamic Context) - COMMENTED OUT -->
      <!--
      <recipe-rating-dynamic
        v-if="currentPhase === 'recipe-rating-dynamic'"
        :language="language"
        :context-type="studyData.selectedContextType"
        :recipes="studyData.recipesDynamic"
        :dynamic-contexts="studyData.dynamicContexts"
        @submit="handleDynamicRatingSubmit"
      />
      -->

      <!-- Phase 1.4.3: Compare Human vs LLM ratings (Dynamic) - COMMENTED OUT -->
      <!--
      <rating-comparison
        v-if="currentPhase === 'rating-comparison-dynamic'"
        :language="language"
        :human-ratings="studyData.humanRatingsDynamic"
        :llm-ratings="studyData.llmRatingsDynamic"
        :is-dynamic="true"
        @submit="handleDynamicComparisonSubmit"
      />
      -->

      <!-- Completion -->
      <completion-screen
        v-if="currentPhase === 'completed'"
        :language="language"
        :data-uploaded="dataUploaded"
        :from-prolific="fromProlific"
      />
    </div>

    <!-- Toast Notifications -->
    <toast-container />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FocusMonitor from '../FocusMonitor.js'
import { useActivityLogger } from '../exampleLogger.js'
import * as api from './api.js'
import InformedConsent from './components/InformedConsent.vue'
import StaticContextInput from './components/StaticContextInput.vue'
import QuestionnaireSelector from './components/QuestionnaireSelector.vue'
import RecipeRating from './components/RecipeRating.vue'
import CompletionScreen from './components/CompletionScreen.vue'
import ToastContainer from './components/ToastContainer.vue'
import { useToast } from './composables/useToast.js'

const urlParams = new URLSearchParams(window.location.search)
const language = ref('en')
// Randomize order of biography and questionnaire (to prevent confounding variables)
const bioFirst = ref(Math.random() < 0.5)
// Always start with informed consent
const currentPhase = ref('informed-consent')
const dataUploaded = ref(false)
const fromProlific = ref(false) // Track if user came from Prolific
const userId = ref('') // Store user ID for display
const showMobileBanner = ref(false) // Show banner for mobile non-Prolific users
// Check if beta passkey is provided to bypass maintenance mode
const betaPasskey = urlParams.get('beta_testing_passkey')
const maintenanceMode = false // Maintenance mode flag - set to false to disable for everyone

const studyData = ref({
  staticContext: '',
  llmFCQ: null,
  llmJC: null,
  userFCQ: null,
  userJC: null,
  selectedContextType: null, // 'unstructured', 'fcq', or 'jc'
  reviewedFCQ: null,
  reviewedJC: null,
  recipesStatic: [],
  humanRatingsStatic: [],
  llmRatingsStatic: [],
  recipesDynamic: [],
  dynamicContexts: [],
  humanRatingsDynamic: [],
  llmRatingsDynamic: []
})

const translations = {
  en: {
    title: 'Food Preferences Study'
  }
}

const maintenanceBannerText = {
  en: {
    title: 'System Under Maintenance',
    message: 'The study is currently unavailable for maintenance. Please check back later. We apologize for any inconvenience.'
  }
}

const mobileBannerText = {
  en: {
    title: 'Desktop Device Required',
    message: 'This study requires a desktop or laptop computer with a keyboard and mouse. Mobile devices and tablets are not supported. Please switch to a desktop device to participate.',
    proceedButton: 'Proceed Anyway'
  }
}

const referenceText = {
  en: {
    title: 'Your Profile Information (For Reference)',
    description: 'Below you can review your biography and questionnaire responses while rating recipes. Feel free to scroll down to reference this information when writing your reviews.'
  }
}

const t = computed(() => translations[language.value])

// Only include active phases (removed: context-review, rating-comparison-static, recipe-rating-dynamic, rating-comparison-dynamic)
const phases = [
  'informed-consent',
  'static-context',
  'questionnaires',
  'recipe-rating-static',
  'completed'
]

const progressPercentage = computed(() => {
  const currentIndex = phases.indexOf(currentPhase.value)
  // Start at 0% and progress through phases
  return (currentIndex / (phases.length - 1)) * 100
})

// Initialize Focus Monitor and Activity Logger
let focusMonitor = null
let logger = null

const { info: showInfoToast, error: showErrorToast } = useToast()

onMounted(async () => {
  // Check if user came from Prolific via URL parameter (check this first)
  const prolificId = urlParams.get('PROLIFIC_ID')
  fromProlific.value = !!prolificId // true if PROLIFIC_ID exists, false otherwise

  // Check for mobile/tablet device (incompatible for this study)
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  const isTouchOnly = navigator.maxTouchPoints > 0 && !window.matchMedia('(pointer: fine)').matches

  if (isMobile || isTouchOnly) {
    // Initialize logger first to log the incompatible device
    logger = useActivityLogger(null)
    logger.logActivity('incompatible-device', {
      userAgent: navigator.userAgent,
      touchPoints: navigator.maxTouchPoints,
      screenSize: `${window.screen.width}x${window.screen.height}`,
      fromProlific: fromProlific.value
    })

    // If from Prolific, redirect to incompatible device URL
    // If NOT from Prolific, show banner and continue
    if (fromProlific.value) {
      logger.endStudy('incompatible_device')
      return // Stop initialization
    } else {
      // Show banner for non-Prolific mobile users
      showMobileBanner.value = true
      // Don't return - allow them to continue if they want
    }
  }

  // Initialize UUID for user session
  // Use PROLIFIC_ID if provided, otherwise generate a UUID with "generated-" prefix
  if (!sessionStorage.getItem('uuid')) {
    if (prolificId) {
      sessionStorage.setItem('uuid', prolificId)
    } else {
      sessionStorage.setItem('uuid', 'generated-' + crypto.randomUUID())
    }
  }

  // Set userId for display in header
  userId.value = sessionStorage.getItem('uuid')

  // Initialize Focus Monitor ONLY for Prolific users (and UNLESS beta_testing_passkey is provided)
  // External participants (no PROLIFIC_ID) don't need focus monitoring
  const shouldEnableFocusMonitor = prolificId && betaPasskey !== 'beta-testing-passkey-study'

  if (shouldEnableFocusMonitor) {
    focusMonitor = new FocusMonitor(
      () => logger?.logActivity('focus-lost', {}),
      () => logger?.logActivity('focus-regained', {}),
      () => {
        // When focus monitor times out, log and immediately redirect to Prolific timeout URL
        logger?.logActivity('focus-timeout', { reason: 'User lost focus for too long or was inactive' })
        logger?.endStudy('timedout') // This will redirect immediately
      }
    )
  }

  // Initialize Activity Logger (with or without focus monitor)
  // Pass fromProlific flag to determine if captcha should be enabled
  logger = useActivityLogger(focusMonitor, fromProlific.value)

  // Log study start
  logger.logActivity('study-started', {
    language: language.value,
    fromProlific: fromProlific.value,
    userId: sessionStorage.getItem('uuid'),
    bioFirst: bioFirst.value
  })
})

async function handleInformedConsentSubmit(consentData) {
  await logger.logActivity('informed-consent-submitted', {
    isAdult: consentData.isAdult,
    agreedToStudy: consentData.agreedToStudy
  })

  // After consent, proceed to randomized first phase (bio or questionnaires)
  currentPhase.value = bioFirst.value ? 'static-context' : 'questionnaires'
}

async function handleStaticContextSubmit(contextData) {
  studyData.value.staticContext = contextData.text
  await logger.logActivity('static-context-submitted', {
    text: contextData.text,
    charCount: contextData.text.length,
    wordCount: contextData.text.split(/\s+/).length
  })

  // If bio was first, go to questionnaires; otherwise we're done with both
  if (bioFirst.value) {
    currentPhase.value = 'questionnaires'
  } else {
    // Questionnaires already done, proceed to recipes
    await fetchRecipesAndProceed()
  }
}

async function handleQuestionnaireSubmit(questionnaireData) {
  studyData.value.selectedContextType = questionnaireData.contextType
  studyData.value.userFCQ = questionnaireData.fcq
  studyData.value.userJC = questionnaireData.jc

  await logger.logActivity('questionnaires-submitted', {
    contextType: questionnaireData.contextType,
    fcq: questionnaireData.fcq,
    jc: questionnaireData.jc
  })

  // If questionnaires were first, go to bio; otherwise we're done with both
  if (bioFirst.value) {
    // Bio already done, proceed to recipes
    await fetchRecipesAndProceed()
  } else {
    // Need to collect bio next
    currentPhase.value = 'static-context'
  }
}

async function fetchRecipesAndProceed() {
  // Fetch recipes for static rating phase
  try {
    const userId = sessionStorage.getItem('uuid')
    const recipesResponse = await api.getRecipes(userId)
    if (recipesResponse.success) {
      studyData.value.recipesStatic = recipesResponse.recipes
    }
  } catch (error) {
    console.error('Failed to fetch recipes:', error)
    // Continue anyway with empty array - will show error to user
  }

  currentPhase.value = 'recipe-rating-static'
}

async function handleReviewSubmit(reviewData) {
  studyData.value.reviewedFCQ = reviewData.fcq
  studyData.value.reviewedJC = reviewData.jc

  await logger.logActivity('context-review-submitted', reviewData)

  await fetchRecipesAndProceed()
}

async function handleDirectionsToggle(toggleData) {
  await logger.logActivity('directions-toggle', {
    action: toggleData.action,
    recipeId: toggleData.recipeId,
    recipeName: toggleData.recipeName
  })
}

async function handleRecipeRatingSubmit(ratingsData) {
  studyData.value.humanRatingsStatic = ratingsData

  await logger.logActivity('recipe-ratings-static-submitted', {
    ratings: ratingsData
  })

  currentPhase.value = 'completed'

  // Mark data as uploaded after the log queue is cleared
  // The endStudy function will no longer auto-redirect
  await logger.endStudy('completed')
  dataUploaded.value = true
}

async function handleComparisonSubmit(comparisonData) {
  await logger.logActivity('rating-comparison-static-submitted', comparisonData)

  // Skip dynamic rating phases - go directly to completion
  currentPhase.value = 'completed'
  await logger.endStudy('completed')

  /* COMMENTED OUT: Dynamic rating phase
  // Fetch dynamic contexts and recipes for dynamic rating phase
  try {
    const userId = sessionStorage.getItem('uuid')
    const [contextsResponse, recipesResponse] = await Promise.all([
      api.getDynamicContexts(userId, language.value),
      api.getRecipes(userId)
    ])

    if (contextsResponse.success) {
      studyData.value.dynamicContexts = contextsResponse.contexts
    }
    if (recipesResponse.success) {
      studyData.value.recipesDynamic = recipesResponse.recipes
    }
  } catch (error) {
    console.error('Failed to fetch dynamic data:', error)
  }

  currentPhase.value = 'recipe-rating-dynamic'
  */
}

async function handleDynamicRatingSubmit(ratingsData) {
  studyData.value.humanRatingsDynamic = ratingsData

  await logger.logActivity('recipe-ratings-dynamic-submitted', ratingsData)

  currentPhase.value = 'rating-comparison-dynamic'
}

async function handleDynamicComparisonSubmit(comparisonData) {
  await logger.logActivity('rating-comparison-dynamic-submitted', comparisonData)

  currentPhase.value = 'completed'
  await logger.endStudy('completed')
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  color: #667eea;
  font-size: 1.8rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-id-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f0f3ff;
  border-radius: 6px;
  border: 1px solid #667eea;
}

.user-id-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.user-id-value {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  position: relative;
}

.progress-fill {
  height: 100%;
  background: #4caf50;
  transition: width 0.5s ease;
}

.maintenance-banner {
  background: #d32f2f;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-bottom: 4px solid #b71c1c;
  text-align: center;
}

.maintenance-banner-content h2 {
  color: white;
  font-size: 1.8rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.maintenance-banner-content p {
  color: white;
  font-size: 1.2rem;
  line-height: 1.6;
  margin: 0;
}

.mobile-banner {
  background: #ff9800;
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-bottom: 4px solid #f57c00;
}

.mobile-banner-content h2 {
  color: white;
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 700;
}

.mobile-banner-content p {
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.btn-proceed-anyway {
  background: white;
  color: #ff9800;
  padding: 0.75rem 2rem;
  border: 2px solid white;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.btn-proceed-anyway:hover {
  background: #fff3e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.reference-section {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 3px solid #e0e0e0;
}

.reference-section h3 {
  color: #667eea;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.reference-section > p {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
  font-style: italic;
}

.btn-primary {
  background: #667eea;
  color: white;
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #667eea;
  padding: 0.75rem 2rem;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 0.5rem;
}

.btn-secondary:hover {
  background: #f0f3ff;
}

/* Ensure reCAPTCHA badge is visible */
.grecaptcha-badge {
  visibility: visible !important;
  opacity: 1 !important;
  z-index: 999 !important;
}
</style>
