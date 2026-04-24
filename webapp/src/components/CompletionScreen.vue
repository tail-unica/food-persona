<template>
  <div class="completion-screen">
    <div class="success-animation">
      <div class="checkmark-circle">
        <svg class="checkmark" viewBox="0 0 52 52">
          <circle class="checkmark-circle-path" cx="26" cy="26" r="25" fill="none"/>
          <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
        </svg>
      </div>
    </div>

    <h1>{{ t.title }}</h1>
    <p class="description">{{ t.description }}</p>

    <!-- Show Prolific return button ONLY for Prolific participants -->
    <div v-if="fromProlific" class="prolific-return">
      <div class="mandatory-notice">
        <h3>⚠️ {{ t.mandatoryTitle }}</h3>
        <p>{{ t.mandatoryMessage }}</p>
      </div>
      <button
        class="btn-prolific"
        @click="returnToProlific"
        :disabled="!dataUploaded"
      >
        {{ t.returnToProlific }}
      </button>
      <p v-if="!dataUploaded" class="upload-status">{{ t.uploadingData }}</p>
    </div>

    <!-- Show simple thank you for external participants -->
    <div v-else class="external-thank-you">
      <p>{{ t.externalThankYou }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  language: {
    type: String,
    required: true
  },
  dataUploaded: {
    type: Boolean,
    default: false
  },
  fromProlific: {
    type: Boolean,
    default: true
  }
})

const translations = {
  en: {
    title: 'Study Completed!',
    description: 'Thank you for completing this study. Your responses have been recorded successfully.',
    whatNext: 'What happens next?',
    whatNextDesc: 'Your data will be analyzed along with other participants to understand how well AI can model human food preferences and how context affects food choices.',
    thankYou: 'Thank you for your valuable contribution!',
    contribution: 'Your participation helps advance research in AI and personalized recommendation systems.',
    mandatoryTitle: 'IMPORTANT - Action Required!',
    mandatoryMessage: 'You MUST click the button below to complete your submission and receive payment on Prolific. Without clicking this button, we cannot evaluate your submission.',
    returnToProlific: 'Complete Study & Return to Prolific',
    uploadingData: 'Uploading your data, please wait...',
    externalThankYou: 'You may now close this window. Thank you again for your time!'
  }
}

const t = computed(() => translations[props.language])

// Import completion URL from exampleLogger where all Prolific URLs are defined
const PROLIFIC_COMPLETION_URL = import.meta.env.VITE_PROLIFIC_COMPLETED_URL || 'https://app.prolific.com/submissions/complete?cc=PLACEHOLDER'

function returnToProlific() {
  if (props.dataUploaded) {
    window.location.href = PROLIFIC_COMPLETION_URL
  }
}
</script>

<style scoped>
.completion-screen {
  text-align: center;
  padding: 3rem 1rem;
  max-width: 700px;
  margin: 0 auto;
}

.success-animation {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.checkmark-circle {
  width: 120px;
  height: 120px;
  position: relative;
}

.checkmark {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: block;
  stroke-width: 3;
  stroke: #4caf50;
  stroke-miterlimit: 10;
  box-shadow: inset 0 0 0 #4caf50;
  animation: fill 0.4s ease-in-out 0.4s forwards, scale 0.3s ease-in-out 0.9s both;
}

.checkmark-circle-path {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  stroke-width: 3;
  stroke-miterlimit: 10;
  stroke: #4caf50;
  fill: none;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke: #4caf50;
  stroke-width: 3;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}

@keyframes scale {
  0%, 100% {
    transform: none;
  }
  50% {
    transform: scale3d(1.1, 1.1, 1);
  }
}

@keyframes fill {
  100% {
    box-shadow: inset 0 0 0 60px #4caf50;
  }
}

h1 {
  color: #4caf50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.description {
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.info-box {
  background: #e3f2fd;
  border: 2px solid #2196f3;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: left;
}

.info-box h3 {
  color: #1976d2;
  margin-bottom: 1rem;
}

.info-box p {
  color: #555;
  line-height: 1.6;
}

.thank-you {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.thank-you p {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.sub-text {
  font-size: 1rem !important;
  font-weight: 400 !important;
  opacity: 0.9;
}

.prolific-return {
  background: #f5f5f5;
  padding: 2rem;
  border-radius: 12px;
  border: 2px solid #e0e0e0;
}

.mandatory-notice {
  background: #fff3cd;
  border: 3px solid #ff9800;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: pulse 2s ease-in-out infinite;
}

.mandatory-notice h3 {
  color: #e65100;
  margin: 0 0 0.75rem 0;
  font-size: 1.3rem;
  font-weight: 700;
}

.mandatory-notice p {
  color: #663c00;
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.5;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(255, 152, 0, 0);
  }
}

.btn-prolific {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.25rem 3rem;
  font-size: 1.2rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-prolific:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-prolific:disabled {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.6;
}

.upload-status {
  margin-top: 1rem;
  color: #666;
  font-style: italic;
  font-size: 0.95rem;
}

.external-thank-you {
  background: #f5f5f5;
  padding: 2rem;
  border-radius: 12px;
  border: 2px solid #e0e0e0;
}

.external-thank-you p {
  font-size: 1.1rem;
  color: #555;
  margin: 0;
}
</style>
