<template>
  <div class="informed-consent">
    <h2>{{ t.title }}</h2>

    <div class="consent-content">
      <p class="placeholder-text" v-html="t.placeholderText"></p>
    </div>

    <div class="consent-checkboxes">
      <label class="checkbox-item">
        <input
          type="checkbox"
          v-model="isAdult"
          :disabled="disabled"
        />
        <span>{{ t.adultDeclaration }}</span>
      </label>

      <label class="checkbox-item">
        <input
          type="checkbox"
          v-model="agreedToStudy"
          :disabled="disabled"
        />
        <span>{{ t.studyAgreement }}</span>
      </label>
    </div>

    <button
      v-if="!disabled"
      class="btn-primary"
      @click="submit"
      :disabled="!isValid"
      :title="!isValid ? t.validationError : ''"
    >
      {{ t.continue }}
    </button>
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
  }
})

const emit = defineEmits(['submit'])

const isAdult = ref(false)
const agreedToStudy = ref(false)

const translations = {
  en: {
    title: 'Informed Consent',
    placeholderText: '<strong>Consent form</strong><br>This study is in line with the current laws D. Lgs 196/2003 and EU GDPR 679/2016 on data protection and by performing the study you consent to the processing and communication of personal data, within the limits, for the purposes and for the duration specified by the current laws (D. Lgs 196/2003 and EU GDPR 679/2016). The data collection complies with the obligations laid down by current legislation in terms of the collection, processing, and storage of sensitive data.<br><br><strong>Potential risks:</strong><br>There are no known or anticipated risks to you by participating in this research.<br><br><strong>Confidentiality:</strong><br>No personally identifiable information will be collected, and although the data from this research project will be published and presented at conferences or journals. Thus, it will not be possible to identify individuals.<br><br><strong>Recruitment:</strong><br>You have been recruited through Prolific.com or through word-of-mouth.<br><br><strong>Storage of Data:</strong><br>During the study, the collected data will be electronically saved on Data Processor/s Aruba s.p.a, via San Clemente 52, 24036 Ponte San Pietro (BG), ITALY. Moreover, this data will be subsequently stored on the storage service offered by the University of Torino and/or the University of Cagliari.<br>The data will be stored for a period that is no longer than what is needed for the present research. Then, it will be destroyed.<br><br><strong>Right to Withdraw:</strong><br>The participation in this study is voluntary. You can decide not to participate at any time. You can do that by closing your browser and contacting the principal investigator: please include the assigned ID to withdraw. On the top-right of the screen, you can find your ID and you should write it down, in case you decide to withdraw at a later point. After receiving via email your withdrawal request, we will destroy the data that we collected and are associated with your ID, the email message we received, and the email account of the sender.<br>Your right to withdraw data from the study will apply before the data analysis phase of this experiment, which will happen after the end of the study on January 10th, 2026. After this date, it is possible that some form of research dissemination will have already occurred, and it might not be possible to withdraw the collected data.<br><br><strong>Follow up:</strong><br>To obtain results from the study, please contact the principal investigators.<br><br><strong>Questions or Concerns:</strong><br>Contact the principal investigators, Noemi Mauro (noemi.mauro@unito.it) and Giacomo Medda (giacomo.medda@unica.it).<br><br>By completing and submitting this form, your free and informed consent is implied and indicates that you understand the above conditions of participation in this study and the experimental procedures.',
    adultDeclaration: 'I declare to be at least 18 years old.',
    studyAgreement: 'I agree to participate in the study and to the processing of the data collected during the test.',
    continue: 'Continue',
    validationError: 'Please check both boxes to continue'
  }
}

const t = computed(() => translations[props.language])

const isValid = computed(() => {
  return isAdult.value && agreedToStudy.value
})

function submit() {
  if (isValid.value) {
    emit('submit', {
      isAdult: isAdult.value,
      agreedToStudy: agreedToStudy.value
    })
  }
}
</script>

<style scoped>
.informed-consent {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.consent-content {
  background-color: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.placeholder-text {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.consent-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #fff;
  border-radius: 8px;
}

.checkbox-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.checkbox-item:hover {
  background-color: #f8f9fa;
}

.checkbox-item input[type="checkbox"] {
  margin-top: 0.25rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.checkbox-item input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.checkbox-item span {
  color: #333;
  line-height: 1.5;
  font-size: 1rem;
}

.btn-primary {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>
