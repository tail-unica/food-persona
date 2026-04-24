<template>
  <div class="static-context-input">
    <h2 v-if="!disabled">{{ t.title }}</h2>
    <p v-if="!disabled" class="description">{{ t.description }}</p>

    <div class="input-container">
      <div class="textarea-wrapper">
        <textarea
          v-model="contextText"
          :placeholder="t.placeholder"
          :maxlength="maxChars"
          @input="updateStats"
          :disabled="disabled"
          rows="17"
        ></textarea>

        <button
          v-if="!disabled"
          type="button"
          class="help-icon"
          @click="showHelp = !showHelp"
          :title="t.helpTooltip"
        >
          ?
        </button>
      </div>

      <div class="stats">
        <span>{{ t.characters }}: {{ charCount }} / {{ maxChars }}</span>
        <span>{{ t.words }}: {{ wordCount }}</span>
        <span v-if="wordCount < minWords" class="warning">{{ t.minWordsWarning }}</span>
      </div>

      <div v-if="showHelp" class="help-section">
        <h4>{{ t.helpTitle }}</h4>
        <div class="help-content">{{ t.helpContent }}</div>
      </div>
    </div>

    <div v-if="!disabled" class="button-group">
      <button
        class="btn-primary"
        @click="submit"
        :disabled="!isValid"
        :title="!isValid ? t.validationError : ''"
      >
        {{ t.continue }}
      </button>
      <button
        v-if="betaTesting"
        class="btn-skip"
        @click="emit('skip')"
        type="button"
      >
        {{ t.skip }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  language: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  initialValue: {
    type: String,
    default: ''
  },
  betaTesting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'skip'])

const contextText = ref(props.initialValue || '')
const charCount = ref(props.initialValue?.length || 0)
const wordCount = ref(props.initialValue ? props.initialValue.trim().split(/\s+/).filter(w => w.length > 0).length : 0)
const showHelp = ref(false)
const maxChars = 10000
const minWords = 150

const translations = {
  en: {
    title: 'Tell us about yourself',
    description: 'Please share your personal story and relationship with food. This helps us understand what shapes your food preferences. A good bio should be about 200-300 words.',
    placeholder: 'Tell us about yourself and your relationship with food. Consider including:\n\n• Your background (where you\'re from, where you\'ve lived, family situation)\n• Your food journey (how you learned to cook, memorable meals, food traditions)\n• Travel experiences where you discovered new cuisines or ingredients\n• Significant life changes that affected your eating habits (health conditions, relocations, lifestyle changes)\n• Your current cooking style and preferences (favorite cuisines, typical meals, cooking frequency)\n• Any dietary restrictions, allergies, or health-related food considerations\n• Hobbies and interests that influence your food choices\n• Specific memories of dishes or restaurants that made an impact on you\n\nBe as detailed and personal as you\'d like - we want to understand the unique factors that shape your food preferences.',
    helpTooltip: 'Click for detailed instructions',
    helpTitle: 'What to include in your biography',
    helpContent: 'Tell us about yourself and your relationship with food. Consider including:\n\n• Your background (where you\'re from, where you\'ve lived, family situation)\n• Your food journey (how you learned to cook, memorable meals, food traditions)\n• Travel experiences where you discovered new cuisines or ingredients\n• Significant life changes that affected your eating habits (health conditions, relocations, lifestyle changes)\n• Your current cooking style and preferences (favorite cuisines, typical meals, cooking frequency)\n• Any dietary restrictions, allergies, or health-related food considerations\n• Hobbies and interests that influence your food choices\n• Specific memories of dishes or restaurants that made an impact on you\n\nBe as detailed and personal as you\'d like - we want to understand the unique factors that shape your food preferences.',
    characters: 'Characters',
    words: 'Words',
    minWordsWarning: 'Please write at least '+minWords+' words',
    continue: 'Continue',
    skip: 'Next (and skip)',
    validationError: 'Please write at least '+minWords+' words before continuing'
  }
}

const t = computed(() => translations[props.language])

const isValid = computed(() => {
  return wordCount.value >= minWords && charCount.value <= maxChars
})

function updateStats() {
  charCount.value = contextText.value.length
  wordCount.value = contextText.value.trim().split(/\s+/).filter(w => w.length > 0).length
}

function submit() {
  if (isValid.value) {
    emit('submit', {
      text: contextText.value,
      charCount: charCount.value,
      wordCount: wordCount.value
    })
  }
}
</script>

<style scoped>
.static-context-input {
  padding: 1rem;
}

h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

.description {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.input-container {
  margin-bottom: 1.5rem;
}

.textarea-wrapper {
  position: relative;
}

textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

.help-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  border: 2px solid white;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.help-icon:hover {
  background: #5568d3;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.help-section {
  margin-top: 1rem;
  padding: 1.5rem;
  background: #f8f9ff;
  border: 2px solid #667eea;
  border-radius: 8px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.help-section h4 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.help-content {
  color: #333;
  line-height: 1.8;
  white-space: pre-line;
  font-size: 0.95rem;
}

.stats {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.stats .warning {
  color: #ff6b6b;
  font-weight: 600;
}

.button-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

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
}

.btn-skip:hover {
  background: #f57c00;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}
</style>
