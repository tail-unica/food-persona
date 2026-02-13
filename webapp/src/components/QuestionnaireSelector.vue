<template>
  <div class="questionnaire-selector">
    <h2 v-if="!disabled">{{ t.title }}</h2>
    <p v-if="!disabled" class="description">{{ t.description }}</p>

    <!-- Context selection hidden - always using both questionnaires -->

    <div class="questionnaire-display">
      <!-- Always show both questionnaires -->
      <h3>{{ t.fcqQuestionnaire }}</h3>
      <p v-if="!disabled" class="info">{{ t.fcqInfo }}</p>
      <grid-questionnaire
        :key="'fcq-both-' + language"
        @answered-questions="handleBothFCQAnswered"
        :description="disabled ? '' : t.fcqInstructions"
        :options="fcqOptionsEn"
        :disabled="disabled"
        :initial-answers="initialFcq"
      >
        <div v-for="(question, index) in fcqQuestions" :key="index" v-html="question"></div>
      </grid-questionnaire>

      <!-- Beta testing skip button -->
      <button
        v-if="betaTesting"
        class="btn-skip"
        @click="emit('skip')"
        type="button"
      >
        {{ t.skip }}
      </button>

      <div v-if="fcqAnswers || disabled" class="both-separator">
        <h3>{{ t.jcQuestionnaire }}</h3>
        <p v-if="!disabled" class="info">{{ t.jcInfo }}</p>
        <div class="jc-form">
          <nutritionist-questionnaire
            :language="language"
            :from-prolific="fromProlific"
            :disabled="disabled"
            :initial-data="initialJc"
            @submit="handleBothJCSubmit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import GridQuestionnaire from '../../GridQuestionnaire.vue'
import NutritionistQuestionnaire from './NutritionistQuestionnaire.vue'

const props = defineProps({
  language: {
    type: String,
    required: true
  },
  staticContext: {
    type: String,
    required: true
  },
  llmFcq: {
    type: Object,
    default: null
  },
  llmJc: {
    type: Object,
    default: null
  },
  fromProlific: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  initialFcq: {
    type: Object,
    default: null
  },
  initialJc: {
    type: Object,
    default: null
  },
  betaTesting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'skip'])

const selectedContextType = ref('both') // Always use both questionnaires
const fcqAnswers = ref(props.initialFcq || null)
const jcAnswers = ref(props.initialJc || null)

const translations = {
  en: {
    title: 'Food Preferences Questionnaires',
    description: 'Please complete the following questionnaires about your food preferences and dietary habits.',
    selectContextType: 'Select how you want to provide your preferences:',
    unstructured: 'Keep Original Text',
    unstructuredDesc: 'Use your original text description without any changes',
    fcq: 'Food Choice Questionnaire (FCQ)',
    fcqDesc: 'Answer questions about factors that influence your food choices',
    jc: 'Nutritionist Questionnaire',
    jcDesc: 'Provide detailed information about your dietary habits and health',
    both: 'Use Both FCQ and Nutritionist Questionnaire',
    bothDesc: 'Complete both questionnaires for more comprehensive preference information',
    yourContext: 'Your Original Context:',
    fcqQuestionnaire: 'Food Choice Questionnaire',
    fcqInfo: 'Please indicate how important each factor is when choosing food.',
    fcqInstructions: 'How important are the following factors when you choose food?',
    jcQuestionnaire: 'Nutritionist Questionnaire',
    jcInfo: 'Please provide information about your dietary habits, health conditions, and lifestyle.',
    continueButton: 'Continue',
    skip: 'Next (and skip)'
  }
}

const t = computed(() => translations[props.language])

const fcqOptionsEn = ['Not important at all', 'Slightly important', 'Very important', 'Extremely important']

const fcqQuestions = computed(() => {
  return [
    'I choose foods because they keep me healthy',
    'I choose foods that help me control my weight',
    'I choose foods that are convenient to prepare',
    'I choose foods for their taste',
    'I choose foods for ecological/sustainability reasons',
    'I choose foods for ethical or religious reasons',
    'I choose foods that are familiar/traditional',
    'I choose foods based on price',
    'I choose foods that improve my mood'
  ]
})

function handleFCQAnswered([questions, attentionCheckPassed]) {
  fcqAnswers.value = {
    questions,
    attentionCheckPassed
  }
  submitData()
}

function handleJCSubmit(answers) {
  jcAnswers.value = answers
  submitData()
}

function handleBothFCQAnswered([questions, attentionCheckPassed]) {
  fcqAnswers.value = {
    questions,
    attentionCheckPassed
  }
  // Don't submit yet, wait for JC questionnaire
}

function handleBothJCSubmit(answers) {
  jcAnswers.value = answers
  submitData()
}

function submitData() {
  if (selectedContextType.value === 'unstructured') {
    emit('submit', {
      contextType: 'unstructured',
      fcq: null,
      jc: null
    })
  } else if (selectedContextType.value === 'fcq' && fcqAnswers.value) {
    emit('submit', {
      contextType: 'fcq',
      fcq: fcqAnswers.value,
      jc: null
    })
  } else if (selectedContextType.value === 'jc' && jcAnswers.value) {
    emit('submit', {
      contextType: 'jc',
      fcq: null,
      jc: jcAnswers.value
    })
  } else if (selectedContextType.value === 'both' && fcqAnswers.value && jcAnswers.value) {
    emit('submit', {
      contextType: 'both',
      fcq: fcqAnswers.value,
      jc: jcAnswers.value
    })
  }
}
</script>

<style scoped>
.btn-skip {
  background: #ff9800;
  color: white;
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1.5rem;
}

.btn-skip:hover {
  background: #f57c00;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}
</style>

<style scoped>
.questionnaire-selector {
  padding: 1rem;
}

h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

h3 {
  color: #555;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.description, .info {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.context-selection {
  margin-bottom: 2rem;
}

.context-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.context-option {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.context-option:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.context-option input[type="radio"] {
  margin-right: 1rem;
  margin-top: 0.25rem;
  cursor: pointer;
}

.option-content strong {
  display: block;
  color: #333;
  margin-bottom: 0.25rem;
}

.option-content p {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.context-preview {
  margin: 2rem 0;
}

.context-box {
  background: #f5f5f5;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  line-height: 1.6;
  color: #333;
}

.questionnaire-display {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e0e0e0;
}

.jc-form {
  margin-top: 1rem;
}

.both-separator {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid #e0e0e0;
}

.continue-button {
  margin-top: 1.5rem;
  padding: 0.75rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.continue-button:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.continue-button:active {
  transform: translateY(0);
}
</style>
