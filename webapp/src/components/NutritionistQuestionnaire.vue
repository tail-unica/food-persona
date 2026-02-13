<template>
  <div class="nutritionist-questionnaire">
    <form @submit.prevent="submitForm" :class="{ 'form-disabled': disabled }">
      <!-- Demographics - Only shown for external users (not from Prolific) -->
      <section class="form-section" v-if="!fromProlific">
        <h4>{{ t.demographics }} <span class="required">*</span></h4>
        <div class="form-group" data-field="age">
          <label>{{ t.age }} <span class="required">*</span></label>
          <input type="number" v-model="formData.age" min="18" max="120" required />
          <div v-if="errors.age" class="error-message">{{ errors.age }}</div>
        </div>

        <div class="form-group" data-field="gender">
          <label>{{ t.gender }} <span class="required">*</span></label>
          <select v-model="formData.gender" required>
            <option value="">{{ t.select }}</option>
            <option value="M">{{ t.male }}</option>
            <option value="F">{{ t.female }}</option>
            <option value="other">{{ t.other }}</option>
          </select>
          <div v-if="errors.gender" class="error-message">{{ errors.gender }}</div>
        </div>

        <div class="form-group" data-field="birthCountry">
          <label>{{ t.birthCountry }} <span class="required">*</span></label>
          <select v-model="formData.birthCountry" required>
            <option value="">{{ t.select }}</option>
            <option v-for="country in countries" :key="country.code" :value="country.name">
              {{ country.name }}
            </option>
          </select>
          <div v-if="errors.birthCountry" class="error-message">{{ errors.birthCountry }}</div>
        </div>

        <div class="form-group" data-field="birthRegion">
          <label>{{ t.birthRegion }} <span class="required">*</span></label>
          <input type="text" v-model="formData.birthRegion" required />
          <div v-if="errors.birthRegion" class="error-message">{{ errors.birthRegion }}</div>
        </div>

        <div class="form-group" data-field="residenceCountry">
          <label>{{ t.residenceCountry }} <span class="required">*</span></label>
          <select v-model="formData.residenceCountry" required>
            <option value="">{{ t.select }}</option>
            <option v-for="country in countries" :key="country.code" :value="country.name">
              {{ country.name }}
            </option>
          </select>
          <div v-if="errors.residenceCountry" class="error-message">{{ errors.residenceCountry }}</div>
        </div>

        <div class="form-group" data-field="residenceRegion">
          <label>{{ t.residenceRegion }} <span class="required">*</span></label>
          <input type="text" v-model="formData.residenceRegion" required />
          <div v-if="errors.residenceRegion" class="error-message">{{ errors.residenceRegion }}</div>
        </div>
      </section>

      <!-- Region of Birth and Residence - Always shown (including for Prolific users) -->
      <section class="form-section" v-if="fromProlific">
        <h4>{{ t.demographics }} <span class="required">*</span></h4>
        <div class="form-group" data-field="birthRegion">
          <label>{{ t.birthRegion }} <span class="required">*</span></label>
          <input type="text" v-model="formData.birthRegion" required />
          <div v-if="errors.birthRegion" class="error-message">{{ errors.birthRegion }}</div>
        </div>
        <div class="form-group" data-field="residenceRegion">
          <label>{{ t.residenceRegion }} <span class="required">*</span></label>
          <input type="text" v-model="formData.residenceRegion" required />
          <div v-if="errors.residenceRegion" class="error-message">{{ errors.residenceRegion }}</div>
        </div>
      </section>

      <!-- Health Conditions -->
      <section class="form-section">
        <h4>{{ t.healthConditions }} <span class="required">*</span></h4>
        <div class="checkbox-group" data-field="conditions">
          <label v-for="condition in healthConditions" :key="condition.value">
            <input
              type="checkbox"
              :value="condition.value"
              v-model="formData.conditions"
              :disabled="formData.conditions.includes('none') && condition.value !== 'none'"
              @change="handleHealthConditionChange"
            />
            {{ condition.label }}
          </label>
        </div>
        <div v-if="errors.conditions" class="error-message">{{ errors.conditions }}</div>
        <br>
        <div class="form-group" v-if="formData.conditions.includes('other')">
          <label>{{ t.otherCondition }} <span class="required">*</span></label>
          <input type="text" v-model="formData.otherCondition" required />
        </div>

        <div class="form-group" data-field="medications">
          <label>{{ t.medications }} <span class="required">*</span></label>
          <textarea v-model="formData.medications" rows="2" :disabled="formData.noMedications"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noMedications" @change="handleNoMedicationsChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.medications" class="error-message">{{ errors.medications }}</div>
        </div>

        <div class="form-group" data-field="supplements">
          <label>{{ t.supplements }} <span class="required">*</span></label>
          <textarea v-model="formData.supplements" rows="2" :disabled="formData.noSupplements"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noSupplements" @change="handleNoSupplementsChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.supplements" class="error-message">{{ errors.supplements }}</div>
        </div>
      </section>

      <!-- Allergies and Restrictions -->
      <section class="form-section">
        <h4>{{ t.allergiesRestrictions }}</h4>

        <div class="form-group" data-field="allergies">
          <label>{{ t.allergies }} <span class="required">*</span></label>
          <textarea v-model="formData.allergies" rows="2" :disabled="formData.noAllergies"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noAllergies" @change="handleNoAllergiesChangeIndividual" />
            {{ t.none }}
          </label>
          <div v-if="errors.allergies" class="error-message">{{ errors.allergies }}</div>
        </div>

        <div class="form-group" data-field="intolerances">
          <label>{{ t.intolerances }} <span class="required">*</span></label>
          <textarea v-model="formData.intolerances" rows="2" :disabled="formData.noIntolerances"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noIntolerances" @change="handleNoIntolerancesChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.intolerances" class="error-message">{{ errors.intolerances }}</div>
        </div>

        <div class="form-group" data-field="dislikedFoods">
          <label>{{ t.dislikedFoods }} <span class="required">*</span></label>
          <textarea v-model="formData.dislikedFoods" rows="2" :disabled="formData.noDislikedFoods"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noDislikedFoods" @change="handleNoDislikedFoodsChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.dislikedFoods" class="error-message">{{ errors.dislikedFoods }}</div>
        </div>

        <div class="form-group" data-field="restrictions">
          <label>{{ t.dietaryRestrictions }} <span class="required">*</span></label>
          <div class="checkbox-group">
            <label v-for="restriction in dietaryRestrictions" :key="restriction.value">
              <input type="checkbox" :value="restriction.value" v-model="formData.restrictions" :disabled="formData.noDietaryRestrictions" />
              {{ restriction.label }}
            </label>
            <label>
              <input type="checkbox" v-model="formData.noDietaryRestrictions" @change="handleNoDietaryRestrictionsChange" />
              {{ t.none }}
            </label>
          </div>
          <div v-if="errors.restrictions" class="error-message">{{ errors.restrictions }}</div>
        </div>
        <div class="form-group" v-if="formData.restrictions.includes('other')">
          <label>{{ t.otherRestriction }} <span class="required">*</span></label>
          <input type="text" v-model="formData.otherRestriction" required :disabled="formData.noDietaryRestrictions" />
        </div>
      </section>

      <!-- Lifestyle -->
      <section class="form-section">
        <h4>{{ t.lifestyle }}</h4>
        <div class="form-group">
          <label>{{ t.workActivity }} <span class="required">*</span></label>
          <select v-model="formData.workActivity" required>
            <option value="">{{ t.select }}</option>
            <option value="sedentary">{{ t.sedentary }}</option>
            <option value="moderate">{{ t.moderate }}</option>
            <option value="active">{{ t.active }}</option>
          </select>
        </div>

        <div class="form-group" data-field="sport">
          <label>{{ t.sport }} <span class="required">*</span></label>
          <input type="text" v-model="formData.sport" :disabled="formData.noSport" />
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noSport" @change="handleNoSportChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.sport" class="error-message">{{ errors.sport }}</div>
        </div>

        <div class="form-group" data-field="sportFrequency">
          <label>{{ t.sportFrequency }} <span class="required">*</span></label>
          <input type="text" v-model="formData.sportFrequency" :placeholder="t.sportFrequencyPlaceholder" :disabled="formData.noSport" />
          <div v-if="errors.sportFrequency" class="error-message">{{ errors.sportFrequency }}</div>
        </div>

        <div class="form-group" data-field="sportLevel">
          <label>{{ t.sportLevel }} <span class="required">*</span></label>
          <select v-model="formData.sportLevel" :disabled="formData.noSport">
            <option value="">{{ t.select }}</option>
            <option value="amateur">{{ t.amateur }}</option>
            <option value="competitive">{{ t.competitive }}</option>
          </select>
          <div v-if="errors.sportLevel" class="error-message">{{ errors.sportLevel }}</div>
        </div>

        <div class="form-group" data-field="walkingTime">
          <label>{{ t.walkingTime }} <span class="required">*</span></label>
          <input type="text" v-model="formData.walkingTime" :placeholder="t.walkingTimePlaceholder" :disabled="formData.noSignificantWalking" />
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noSignificantWalking" @change="handleNoSignificantWalkingChange" />
            {{ t.noSignificantWalking }}
          </label>
          <div v-if="errors.walkingTime" class="error-message">{{ errors.walkingTime }}</div>
        </div>

        <div class="form-group">
          <label>{{ t.mealsPerDay }} <span class="required">*</span></label>
          <select v-model="formData.mealsPerDay" required>
            <option value="">{{ t.select }}</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="other">{{ t.other }}</option>
          </select>
        </div>
      </section>

      <!-- Food Consumption -->
      <section class="form-section">
        <h4>{{ t.foodConsumption }}</h4>
        <div class="form-group">
          <label>{{ t.fruitsVeggies }} <span class="required">*</span></label>
          <select v-model="formData.fruitsVeggies" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1-2">1-2 {{ t.portionsDay }}</option>
            <option value="3-5">3-5 {{ t.portionsDay }}</option>
            <option value=">5">&gt;5 {{ t.portionsDay }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.meatConsumption }} <span class="required">*</span></label>
          <select v-model="formData.meat" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1">1 {{ t.timesWeek }}</option>
            <option value="2-3">2-3 {{ t.timesWeek }}</option>
            <option value=">4">&gt;4 {{ t.timesWeek }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.fishConsumption }} <span class="required">*</span></label>
          <select v-model="formData.fish" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1">1 {{ t.timesWeek }}</option>
            <option value="2-3">2-3 {{ t.timesWeek }}</option>
            <option value=">4">&gt;4 {{ t.timesWeek }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.eggsConsumption }} <span class="required">*</span></label>
          <select v-model="formData.eggs" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1">1 {{ t.timesWeek }}</option>
            <option value="2-3">2-3 {{ t.timesWeek }}</option>
            <option value=">4">&gt;4 {{ t.timesWeek }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.legumesConsumption }} <span class="required">*</span></label>
          <select v-model="formData.legumes" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1">1 {{ t.timesWeek }}</option>
            <option value="2-3">2-3 {{ t.timesWeek }}</option>
            <option value=">4">&gt;4 {{ t.timesWeek }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.dairyConsumption }} <span class="required">*</span></label>
          <select v-model="formData.dairy" required>
            <option value="">{{ t.select }}</option>
            <option value="daily">{{ t.daily }}</option>
            <option value="occasional">{{ t.occasional }}</option>
            <option value="never">{{ t.never }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.sweetsConsumption }} <span class="required">*</span></label>
          <select v-model="formData.sweets" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="1-2">1-2 {{ t.timesWeek }}</option>
            <option value="frequent">{{ t.frequent }}</option>
          </select>
        </div>
      </section>

      <!-- Beverages -->
      <section class="form-section">
        <h4>{{ t.beverages }}</h4>
        <div class="form-group">
          <label>{{ t.alcohol }} <span class="required">*</span></label>
          <select v-model="formData.alcohol" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="occasional">{{ t.occasional }}</option>
            <option value="frequent">{{ t.frequent }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.coffee }} <span class="required">*</span></label>
          <select v-model="formData.coffee" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="occasional">{{ t.occasional }}</option>
            <option value="frequent">{{ t.frequent }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ t.sweetDrinks }} <span class="required">*</span></label>
          <select v-model="formData.sweetDrinks" required>
            <option value="">{{ t.select }}</option>
            <option value="never">{{ t.never }}</option>
            <option value="occasional">{{ t.occasional }}</option>
            <option value="frequent">{{ t.frequent }}</option>
          </select>
        </div>
      </section>

      <!-- Habits -->
      <section class="form-section">
        <h4>{{ t.habits }}</h4>
        <div class="form-group">
          <label>{{ t.breakfast }} <span class="required">*</span></label>
          <select v-model="formData.breakfast" required>
            <option value="">{{ t.select }}</option>
            <option value="always">{{ t.always }}</option>
            <option value="sometimes">{{ t.sometimes }}</option>
            <option value="never">{{ t.never }}</option>
          </select>
        </div>

        <div class="form-group" data-field="particularHabits">
          <label>{{ t.particularHabits }} <span class="required">*</span></label>
          <textarea v-model="formData.particularHabits" rows="2" :placeholder="t.particularHabitsPlaceholder" :disabled="formData.noParticularHabits"></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.noParticularHabits" @change="handleNoParticularHabitsChange" />
            {{ t.none }}
          </label>
          <div v-if="errors.particularHabits" class="error-message">{{ errors.particularHabits }}</div>
        </div>

        <div class="form-group">
          <label>{{ t.motivationLevel }} <span class="required">*</span></label>
          <select v-model="formData.motivationLevel" required>
            <option value="">{{ t.select }}</option>
            <option value="1">1 - {{ t.veryLow }}</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5 - {{ t.veryHigh }}</option>
          </select>
        </div>

        <!-- Attention Check -->
        <div class="form-group attention-check-field">
          <label>{{ t.attentionCheck }} <span class="required">*</span></label>
          <select v-model="formData.attentionCheck" required>
            <option value="">{{ t.select }}</option>
            <option value="option1">{{ t.attentionOption1 }}</option>
            <option value="option2">{{ t.attentionOption2 }}</option>
            <option value="option3">{{ t.attentionOption3 }}</option>
            <option value="correct">{{ t.attentionOptionCorrect }}</option>
            <option value="option4">{{ t.attentionOption4 }}</option>
          </select>
        </div>
      </section>

      <!-- Goals -->
      <section class="form-section">
        <h4>{{ t.goals }} <span class="required">*</span></h4>
        <div class="checkbox-group" data-field="goals">
          <label v-for="goal in personalGoals" :key="goal.value">
            <input type="checkbox" :value="goal.value" v-model="formData.goals" :disabled="formData.noGoals" />
            {{ goal.label }}
          </label>
          <label>
            <input type="checkbox" v-model="formData.noGoals" @change="handleNoGoalsChange" />
            {{ t.none }}
          </label>
        </div>
        <div v-if="errors.goals" class="error-message">{{ errors.goals }}</div>
        <div class="form-group" v-if="formData.goals.includes('other')">
          <label>{{ t.otherGoal }} <span class="required">*</span></label>
          <input type="text" v-model="formData.otherGoal" :disabled="formData.noGoals" />
        </div>
      </section>

      <!-- Context Scenarios -->
      <section class="form-section">
        <h4>{{ t.contextScenarios }}</h4>

        <div class="form-group" data-field="lowSleepBreakfast">
          <label>{{ t.lowSleepBreakfast }} <span class="required">*</span></label>
          <textarea v-model="formData.lowSleepBreakfast" rows="2"></textarea>
          <div v-if="errors.lowSleepBreakfast" class="error-message">{{ errors.lowSleepBreakfast }}</div>
        </div>

        <div class="form-group" data-field="vacationLunch">
          <label>{{ t.vacationLunch }} <span class="required">*</span></label>
          <textarea v-model="formData.vacationLunch" rows="2"></textarea>
          <div v-if="errors.vacationLunch" class="error-message">{{ errors.vacationLunch }}</div>
        </div>

        <div class="form-group" data-field="quickMeal">
          <label>{{ t.quickMeal }} <span class="required">*</span></label>
          <textarea v-model="formData.quickMeal" rows="2"></textarea>
          <div v-if="errors.quickMeal" class="error-message">{{ errors.quickMeal }}</div>
        </div>

        <div class="form-group" data-field="stressedFood">
          <label>{{ t.stressedFood }} <span class="required">*</span></label>
          <textarea v-model="formData.stressedFood" rows="2"></textarea>
          <div v-if="errors.stressedFood" class="error-message">{{ errors.stressedFood }}</div>
        </div>
      </section>

      <button v-if="!disabled" type="submit" class="btn-primary">{{ t.continue }}</button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  language: {
    type: String,
    required: true
  },
  fromProlific: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  initialData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit'])

const errors = ref({})

const defaultFormData = {
  // Demographics - HIDDEN (collected in Prolific)
  age: null,
  gender: '',
  birthCountry: '',
  birthRegion: '',
  residenceCountry: '',
  residenceRegion: '',
  // Health conditions
  conditions: [],
  otherCondition: '',
  noMedications: false,
  medications: '',
  noSupplements: false,
  supplements: '',
  // Allergies and restrictions
  noAllergies: false,
  allergies: '',
  noIntolerances: false,
  intolerances: '',
  noDislikedFoods: false,
  dislikedFoods: '',
  noDietaryRestrictions: false,
  restrictions: [],
  otherRestriction: '',
  // Lifestyle
  workActivity: '',
  noSport: false,
  sport: '',
  sportFrequency: '',
  sportLevel: '',
  noSignificantWalking: false,
  walkingTime: '',
  mealsPerDay: '',
  // Food consumption
  fruitsVeggies: '',
  meat: '',
  fish: '',
  eggs: '',
  legumes: '',
  dairy: '',
  sweets: '',
  // Beverages
  alcohol: '',
  coffee: '',
  sweetDrinks: '',
  // Habits
  breakfast: '',
  noParticularHabits: false,
  particularHabits: '',
  motivationLevel: '',
  attentionCheck: '',
  // Goals
  noGoals: false,
  goals: [],
  otherGoal: '',
  // Context scenarios
  lowSleepBreakfast: '',
  vacationLunch: '',
  quickMeal: '',
  stressedFood: ''
}

const formData = ref(props.initialData ? { ...defaultFormData, ...props.initialData } : { ...defaultFormData })

const countriesText = `AF|Afghanistan
AL|Albania
DZ|Algeria
AS|American Samoa
AD|Andorra
AO|Angola
AI|Anguilla
AQ|Antarctica
AG|Antigua And Barbuda
AR|Argentina
AM|Armenia
AW|Aruba
AU|Australia
AT|Austria
AZ|Azerbaijan
BS|Bahamas
BH|Bahrain
BD|Bangladesh
BB|Barbados
BY|Belarus
BE|Belgium
BZ|Belize
BJ|Benin
BM|Bermuda
BT|Bhutan
BO|Bolivia
BA|Bosnia And Herzegovina
BW|Botswana
BV|Bouvet Island
BR|Brazil
IO|British Indian Ocean Territory
BN|Brunei Darussalam
BG|Bulgaria
BF|Burkina Faso
BI|Burundi
KH|Cambodia
CM|Cameroon
CA|Canada
CV|Cape Verde
KY|Cayman Islands
CF|Central African Republic
TD|Chad
CL|Chile
CN|China
CX|Christmas Island
CC|Cocos (keeling) Islands
CO|Colombia
KM|Comoros
CG|Congo
CD|Congo, The Democratic Republic Of The
CK|Cook Islands
CR|Costa Rica
CI|Cote D'ivoire
HR|Croatia
CU|Cuba
CY|Cyprus
CZ|Czech Republic
DK|Denmark
DJ|Djibouti
DM|Dominica
DO|Dominican Republic
TP|East Timor
EC|Ecuador
EG|Egypt
SV|El Salvador
GQ|Equatorial Guinea
ER|Eritrea
EE|Estonia
ET|Ethiopia
FK|Falkland Islands (malvinas)
FO|Faroe Islands
FJ|Fiji
FI|Finland
FR|France
GF|French Guiana
PF|French Polynesia
TF|French Southern Territories
GA|Gabon
GM|Gambia
GE|Georgia
DE|Germany
GH|Ghana
GI|Gibraltar
GR|Greece
GL|Greenland
GD|Grenada
GP|Guadeloupe
GU|Guam
GT|Guatemala
GN|Guinea
GW|Guinea-bissau
GY|Guyana
HT|Haiti
HM|Heard Island And Mcdonald Islands
VA|Holy See (vatican City State)
HN|Honduras
HK|Hong Kong
HU|Hungary
IS|Iceland
IN|India
ID|Indonesia
IR|Iran, Islamic Republic Of
IQ|Iraq
IE|Ireland
IL|Israel
IT|Italy
JM|Jamaica
JP|Japan
JO|Jordan
KZ|Kazakstan
KE|Kenya
KI|Kiribati
KP|Korea, Democratic People's Republic Of
KR|Korea, Republic Of
KV|Kosovo
KW|Kuwait
KG|Kyrgyzstan
LA|Lao People's Democratic Republic
LV|Latvia
LB|Lebanon
LS|Lesotho
LR|Liberia
LY|Libyan Arab Jamahiriya
LI|Liechtenstein
LT|Lithuania
LU|Luxembourg
MO|Macau
MK|Macedonia, The Former Yugoslav Republic Of
MG|Madagascar
MW|Malawi
MY|Malaysia
MV|Maldives
ML|Mali
MT|Malta
MH|Marshall Islands
MQ|Martinique
MR|Mauritania
MU|Mauritius
YT|Mayotte
MX|Mexico
FM|Micronesia, Federated States Of
MD|Moldova, Republic Of
MC|Monaco
MN|Mongolia
MS|Montserrat
ME|Montenegro
MA|Morocco
MZ|Mozambique
MM|Myanmar
NA|Namibia
NR|Nauru
NP|Nepal
NL|Netherlands
AN|Netherlands Antilles
NC|New Caledonia
NZ|New Zealand
NI|Nicaragua
NE|Niger
NG|Nigeria
NU|Niue
NF|Norfolk Island
MP|Northern Mariana Islands
NO|Norway
OM|Oman
PK|Pakistan
PW|Palau
PS|Palestinian Territory, Occupied
PA|Panama
PG|Papua New Guinea
PY|Paraguay
PE|Peru
PH|Philippines
PN|Pitcairn
PL|Poland
PT|Portugal
PR|Puerto Rico
QA|Qatar
RE|Reunion
RO|Romania
RU|Russian Federation
RW|Rwanda
SH|Saint Helena
KN|Saint Kitts And Nevis
LC|Saint Lucia
PM|Saint Pierre And Miquelon
VC|Saint Vincent And The Grenadines
WS|Samoa
SM|San Marino
ST|Sao Tome And Principe
SA|Saudi Arabia
SN|Senegal
RS|Serbia
SC|Seychelles
SL|Sierra Leone
SG|Singapore
SK|Slovakia
SI|Slovenia
SB|Solomon Islands
SO|Somalia
ZA|South Africa
GS|South Georgia And The South Sandwich Islands
ES|Spain
LK|Sri Lanka
SD|Sudan
SR|Suriname
SJ|Svalbard And Jan Mayen
SZ|Swaziland
SE|Sweden
CH|Switzerland
SY|Syrian Arab Republic
TW|Taiwan, Province Of China
TJ|Tajikistan
TZ|Tanzania, United Republic Of
TH|Thailand
TG|Togo
TK|Tokelau
TO|Tonga
TT|Trinidad And Tobago
TN|Tunisia
TR|Turkey
TM|Turkmenistan
TC|Turks And Caicos Islands
TV|Tuvalu
UG|Uganda
UA|Ukraine
AE|United Arab Emirates
GB|United Kingdom
US|United States
UM|United States Minor Outlying Islands
UY|Uruguay
UZ|Uzbekistan
VU|Vanuatu
VE|Venezuela
VN|Viet Nam
VG|Virgin Islands, British
VI|Virgin Islands, U.s.
WF|Wallis And Futuna
EH|Western Sahara
YE|Yemen
ZM|Zambia
ZW|Zimbabwe`

const countries = countriesText.split('\n').map(line => {
  const [code, name] = line.split('|')
  return { code, name }
})

const translations = {
  en: {
    none: 'None',
    demographics: 'Demographics',
    age: 'Age',
    gender: 'Gender',
    male: 'Male',
    female: 'Female',
    other: 'Other',
    birthCountry: 'Country of Birth',
    birthRegion: 'Region of Birth',
    residenceCountry: 'Country of Residence',
    residenceRegion: 'Region of Residence',
    healthConditions: 'Health Conditions',
    otherCondition: 'Other condition',
    medications: 'Medications',
    supplements: 'Supplements',
    allergiesRestrictions: 'Allergies and Restrictions',
    noAllergiesRestrictions: 'None',
    allergies: 'Food Allergies',
    intolerances: 'Intolerances',
    dislikedFoods: 'Disliked/Avoided Foods',
    dietaryRestrictions: 'Dietary Restrictions',
    otherRestriction: 'Other restriction',
    lifestyle: 'Lifestyle',
    workActivity: 'Work Activity Level',
    sedentary: 'Sedentary (office work)',
    moderate: 'Moderately active',
    active: 'Active (physical work)',
    sport: 'Sport(s) Practiced',
    sportFrequency: 'Weekly Frequency',
    sportFrequencyPlaceholder: 'e.g., 3 times/week',
    sportLevel: 'Level',
    amateur: 'Amateur',
    competitive: 'Competitive',
    walkingTime: 'Daily Walking Time (hours)',
    walkingTimePlaceholder: 'e.g., 1 hour',
    noSignificantWalking: 'I don\'t walk significantly',
    mealsPerDay: 'Number of Main Meals (e.g. breakfast, lunch, dinner)',
    foodConsumption: 'Food Consumption',
    fruitsVeggies: 'Fruits and Vegetables',
    portionsDay: 'portions/day',
    meatConsumption: 'Meat Consumption',
    fishConsumption: 'Fish Consumption',
    eggsConsumption: 'Eggs Consumption',
    legumesConsumption: 'Legumes Consumption',
    dairyConsumption: 'Dairy Products',
    sweetsConsumption: 'Sweets/Industrial Snacks',
    daily: 'Daily',
    occasional: 'Occasional',
    frequent: 'Frequent',
    timesWeek: 'times/week',
    beverages: 'Beverages',
    alcohol: 'Alcohol',
    coffee: 'Coffee/Tea',
    sweetDrinks: 'Sugary Drinks',
    never: 'Never',
    habits: 'Habits',
    breakfast: 'Breakfast',
    always: 'Always',
    sometimes: 'Sometimes',
    particularHabits: 'Particular Habits',
    particularHabitsPlaceholder: 'e.g., fasting, large evening meals, etc.',
    motivationLevel: 'Motivation to Change (1-5)',
    veryLow: 'Very Low',
    veryHigh: 'Very High',
    attentionCheck: 'To ensure data quality, please select "Banana" from the following options',
    attentionOption1: 'Apple',
    attentionOption2: 'Orange',
    attentionOption3: 'Grape',
    attentionOptionCorrect: 'Banana',
    attentionOption4: 'Strawberry',
    goals: 'Personal Goals',
    otherGoal: 'Other goal',
    contextScenarios: 'Context Scenarios',
    lowSleepBreakfast: 'After a night of little sleep, what do you prefer for breakfast?',
    vacationLunch: 'If you are on vacation, what do you order for lunch?',
    quickMeal: 'If you only have 15 minutes, what do you cook or eat?',
    stressedFood: 'When you are stressed, which foods do you seek most?',
    select: 'Select...',
    continue: 'Continue'
  }
}

const t = computed(() => translations[props.language])

const healthConditions = computed(() => {
  return [
    { value: 'diabetes', label: 'Diabetes' },
    { value: 'hypertension', label: 'Hypertension' },
    { value: 'dyslipidemia', label: 'Dyslipidemia' },
    { value: 'high_cholesterol', label: 'High Cholesterol' },
    { value: 'irc', label: 'IRC' },
    { value: 'pcos', label: 'PCOS' },
    { value: 'copd', label: 'COPD' },
    { value: 'reflux', label: 'Reflux' },
    { value: 'rcu', label: 'Ulcerative Colitis' },
    { value: 'crohn', label: 'Crohn\'s Disease' },
    { value: 'ibs', label: 'IBS' },
    { value: 'other', label: 'Other' },
    { value: 'none', label: 'None' }
  ]
})

const dietaryRestrictions = computed(() => {
  return [
    { value: 'vegetarian', label: 'Vegetarian' },
    { value: 'vegan', label: 'Vegan' },
    { value: 'kosher', label: 'Kosher' },
    { value: 'halal', label: 'Halal' },
    { value: 'other', label: 'Other' }
  ]
})

const personalGoals = computed(() => {
  return [
    { value: 'weight_loss', label: 'Weight Loss' },
    { value: 'muscle_gain', label: 'Muscle Gain' },
    { value: 'sports_performance', label: 'Improve Sports Performance' },
    { value: 'disease_management', label: 'Disease Management' },
    { value: 'other', label: 'Other' }
  ]
})

// Health Conditions handlers
function handleHealthConditionChange() {
  if (formData.value.conditions.includes('none')) {
    // If "None" is selected, clear all other conditions
    formData.value.conditions = ['none']
    formData.value.otherCondition = ''
  }
}

function handleNoMedicationsChange() {
  if (formData.value.noMedications) {
    formData.value.medications = ''
  }
}

function handleNoSupplementsChange() {
  if (formData.value.noSupplements) {
    formData.value.supplements = ''
  }
}

// Allergies handlers
function handleNoAllergiesChangeIndividual() {
  if (formData.value.noAllergies) {
    formData.value.allergies = ''
  }
}

function handleNoIntolerancesChange() {
  if (formData.value.noIntolerances) {
    formData.value.intolerances = ''
  }
}

function handleNoDislikedFoodsChange() {
  if (formData.value.noDislikedFoods) {
    formData.value.dislikedFoods = ''
  }
}

function handleNoDietaryRestrictionsChange() {
  if (formData.value.noDietaryRestrictions) {
    formData.value.restrictions = []
    formData.value.otherRestriction = ''
  }
}

// Sport handler
function handleNoSportChange() {
  if (formData.value.noSport) {
    formData.value.sport = ''
    formData.value.sportFrequency = 'None'
    formData.value.sportLevel = 'None'
  } else {
    if (formData.value.sportFrequency === 'None') formData.value.sportFrequency = ''
    if (formData.value.sportLevel === 'None') formData.value.sportLevel = ''
  }
}

// Walking handler
function handleNoSignificantWalkingChange() {
  if (formData.value.noSignificantWalking) {
    formData.value.walkingTime = ''
  }
}

// Habits handler
function handleNoParticularHabitsChange() {
  if (formData.value.noParticularHabits) {
    formData.value.particularHabits = ''
  }
}

// Goals handler
function handleNoGoalsChange() {
  if (formData.value.noGoals) {
    formData.value.goals = []
    formData.value.otherGoal = ''
  }
}

function submitForm() {
  // Clear previous errors
  errors.value = {}

  // Validate demographic fields (only if not from Prolific)
  if (!props.fromProlific) {
    if (!formData.value.age) {
      errors.value.age = props.language === 'en'
        ? 'Please fill in this field.'
        : 'Si prega di compilare questo campo.'
    }
    if (!formData.value.gender) {
      errors.value.gender = props.language === 'en'
        ? 'Please select an option.'
        : 'Si prega di selezionare un\'opzione.'
    }
    if (!formData.value.birthCountry) {
      errors.value.birthCountry = props.language === 'en'
        ? 'Please select a country.'
        : 'Si prega di selezionare un paese.'
    }
    if (!formData.value.residenceCountry) {
      errors.value.residenceCountry = props.language === 'en'
        ? 'Please select a country.'
        : 'Si prega di selezionare un paese.'
    }
  }

  // Validate birthRegion and residenceRegion for all users (including Prolific)
  if (!formData.value.birthRegion) {
    errors.value.birthRegion = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }
  if (!formData.value.residenceRegion) {
    errors.value.residenceRegion = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }

  // Validate health conditions: at least one checkbox must be selected
  if (formData.value.conditions.length === 0) {
    errors.value.conditions = props.language === 'en'
      ? 'Please select at least one option.'
      : 'Si prega di selezionare almeno un\'opzione.'
  }

  // Validate medications: either checkbox or text
  if (!formData.value.noMedications && !formData.value.medications) {
    errors.value.medications = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate supplements: either checkbox or text
  if (!formData.value.noSupplements && !formData.value.supplements) {
    errors.value.supplements = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate allergies: either checkbox or text
  if (!formData.value.noAllergies && !formData.value.allergies) {
    errors.value.allergies = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate intolerances: either checkbox or text
  if (!formData.value.noIntolerances && !formData.value.intolerances) {
    errors.value.intolerances = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate disliked foods: either checkbox or text
  if (!formData.value.noDislikedFoods && !formData.value.dislikedFoods) {
    errors.value.dislikedFoods = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate dietary restrictions: either checkbox or at least one selected
  if (!formData.value.noDietaryRestrictions && formData.value.restrictions.length === 0) {
    errors.value.restrictions = props.language === 'en'
      ? 'Please either check "None" or select at least one option.'
      : 'Si prega di selezionare "Nessuna" o di scegliere almeno un\'opzione.'
  }

  // Validate sport: either checkbox or text
  if (!formData.value.noSport && !formData.value.sport) {
    errors.value.sport = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate sport frequency and level if sport is filled
  if (!formData.value.noSport && formData.value.sport) {
    if (!formData.value.sportFrequency) {
      errors.value.sportFrequency = props.language === 'en'
        ? 'Please fill in this field.'
        : 'Si prega di compilare questo campo.'
    }
    if (!formData.value.sportLevel) {
      errors.value.sportLevel = props.language === 'en'
        ? 'Please select an option.'
        : 'Si prega di selezionare un\'opzione.'
    }
  }

  // Validate walking time: either checkbox or text
  if (!formData.value.noSignificantWalking && !formData.value.walkingTime) {
    errors.value.walkingTime = props.language === 'en'
      ? 'Please either check "I don\'t walk significantly" or fill in this field.'
      : 'Si prega di selezionare "Non cammino in modo significativo" o di compilare questo campo.'
  }

  // Validate particular habits: either checkbox or text
  if (!formData.value.noParticularHabits && !formData.value.particularHabits) {
    errors.value.particularHabits = props.language === 'en'
      ? 'Please either check "None" or fill in this field.'
      : 'Si prega di selezionare "Nessuna" o di compilare questo campo.'
  }

  // Validate goals: either checkbox or at least one selected
  if (!formData.value.noGoals && formData.value.goals.length === 0) {
    errors.value.goals = props.language === 'en'
      ? 'Please either check "None" or select at least one option.'
      : 'Si prega di selezionare "Nessuna" o di scegliere almeno un\'opzione.'
  }

  // Validate context scenarios (all required)
  if (!formData.value.lowSleepBreakfast) {
    errors.value.lowSleepBreakfast = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }

  if (!formData.value.vacationLunch) {
    errors.value.vacationLunch = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }

  if (!formData.value.quickMeal) {
    errors.value.quickMeal = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }

  if (!formData.value.stressedFood) {
    errors.value.stressedFood = props.language === 'en'
      ? 'Please fill in this field.'
      : 'Si prega di compilare questo campo.'
  }

  // If there are errors, scroll to the first error
  if (Object.keys(errors.value).length > 0) {
    const firstErrorKey = Object.keys(errors.value)[0]
    const firstErrorElement = document.querySelector(`[data-field="${firstErrorKey}"]`)
    if (firstErrorElement) {
      firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }

  emit('submit', { ...formData.value })
}
</script>

<style scoped>
.nutritionist-questionnaire {
  padding: 1rem 0;
}

.form-section {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.form-section h4 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  margin-right: 0.75rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.required {
  color: #e74c3c;
  font-weight: bold;
  margin-left: 0.25rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 0.75rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

textarea:disabled,
input:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.form-disabled input,
.form-disabled select,
.form-disabled textarea {
  pointer-events: none;
  opacity: 0.6;
  background-color: #f5f5f5;
}

.form-disabled .checkbox-group input[type="checkbox"] {
  pointer-events: none;
}
</style>
