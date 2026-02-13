import { ref } from 'vue'
import axios from 'axios'
import { useRecaptcha } from './useRecaptcha'


const logs_url = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/logs` : "http://localhost:3000/server/api/logs"
const RECAPTCHA_V3_SITE_KEY = import.meta.env.VITE_RECAPTCHA_V3_SITE_KEY || ''
const RECAPTCHA_V2_SITE_KEY = import.meta.env.VITE_RECAPTCHA_V2_SITE_KEY || ''
const MAX_RECAPTCHA_CHECKS = parseInt(import.meta.env.VITE_MAX_RECAPTCHA_CHECKS || '5')
const RECAPTCHA_TARGET_EVENTS = (import.meta.env.VITE_RECAPTCHA_TARGET_EVENTS || 'static-context-submitted,questionnaires-submitted,recipe-ratings-static-submitted').split(',').map(e => e.trim())

// Prolific completion URLs - read from environment variables
const completed_url = import.meta.env.VITE_PROLIFIC_COMPLETED_URL || ''
const timedout_url = import.meta.env.VITE_PROLIFIC_TIMEDOUT_URL || ''
const incompatible_device_url = import.meta.env.VITE_PROLIFIC_INCOMPATIBLE_URL || ''


export function useActivityLogger(focusMonitor, fromProlific = true) {
    const isProcessing = ref(false)
    const requestQueue = ref([])

    const redirectTo = ref(null)

    // Track reCAPTCHA checks per user (configurable max per study)
    const recaptchaCheckCount = ref(parseInt(sessionStorage.getItem('recaptcha_check_count') || '0'))

    // Check if beta testing passkey is provided
    const urlParams = new URLSearchParams(window.location.search)
    const betaPasskey = urlParams.get('beta_testing_passkey')

    // Skip captcha if: beta passkey provided OR not from Prolific (external participants)
    const skipCaptcha = betaPasskey === 'beta-testing-passkey-study' || !fromProlific

    const { executeRecaptchaV3, showRecaptchaV2Dialog } = skipCaptcha || !RECAPTCHA_V3_SITE_KEY
        ? { executeRecaptchaV3: null, showRecaptchaV2Dialog: null }
        : useRecaptcha(RECAPTCHA_V3_SITE_KEY, RECAPTCHA_V2_SITE_KEY)

    /**
     * Wait for the log queue to be cleared (ensures all data is uploaded) and redirect to Prolific
     * @param status either 'completed', 'incompatible_device' or 'timedout'
     * @returns {Promise<void>}
     */
    const endStudy = async (status) => {
        // Wait for queue to finish processing (ensures all logs including timeout/incompatible are uploaded)
        if(requestQueue.value.length > 0 || isProcessing.value) {
            // Queue is still processing, wait for it to complete
            await new Promise((resolve) => {
                const checkInterval = setInterval(() => {
                    if(requestQueue.value.length === 0 && !isProcessing.value) {
                        clearInterval(checkInterval)
                        resolve()
                    }
                }, 100)
            })
        }

        // Redirect to appropriate Prolific URL based on status
        // These redirects happen IMMEDIATELY after logs are uploaded (no user interaction needed)
        if (status === 'timedout') {
            window.location.href = timedout_url
        } else if (status === 'incompatible_device') {
            window.location.href = incompatible_device_url
        }
        // Note: For 'completed' status, the CompletionScreen component handles the redirect
        // (waits for user to click the button)
    }

    const logActivity = async (type, data) => {
        let enriched_data = {
            ...data,
            type: type,
            user_id: sessionStorage.getItem("uuid")
        }

        // Get reCAPTCHA token on specific events + random 1% (unless beta passkey provided)
        // Max checks per user during entire study (configurable)
        const shouldCheckRecaptcha = !skipCaptcha && executeRecaptchaV3 &&
            recaptchaCheckCount.value < MAX_RECAPTCHA_CHECKS &&
            (RECAPTCHA_TARGET_EVENTS.includes(type) || Math.random() < 0.01)

        if (shouldCheckRecaptcha) {
            try {
                const recaptchaToken = await executeRecaptchaV3('log_activity')
                enriched_data.recaptcha_token = recaptchaToken
                enriched_data.recaptcha_version = 'v3'

                // Increment and persist check count
                recaptchaCheckCount.value++
                sessionStorage.setItem('recaptcha_check_count', recaptchaCheckCount.value.toString())
            } catch (error) {
                console.error('Failed to get reCAPTCHA v3 token:', error)
            }
        }

        // Add focus data if available
        if (focusMonitor && !skipCaptcha) {
            enriched_data.focus_data = {
                focus_lost_count: focusMonitor.focusLostCount || 0,
                total_focus_lost_time: focusMonitor.totalFocusLostTime || 0,
                inactivity_warnings: focusMonitor.inactivityWarnings || 0
            }
        }

        requestQueue.value.push(enriched_data)
        if (!isProcessing.value) {
            await processQueue()
        }
    }

    const processQueue = async () => {
        isProcessing.value = true
        while (requestQueue.value.length > 0) {
            const data = requestQueue.value[0] // Don't shift yet, in case we need to retry
            try {
                const response = await axios.post(logs_url, data)
                // V2 CAPTCHA verification (unless beta passkey provided)
                if (!skipCaptcha && showRecaptchaV2Dialog && response.data?.requireV2Verification) {
                    // Server indicated suspicious activity, show v2 CAPTCHA
                    try {
                        const v2Token = await showRecaptchaV2Dialog(focusMonitor)
                        // Retry the request with the v2 token
                        await axios.post(logs_url, {
                            ...data,
                            recaptcha_token: v2Token,
                            recaptcha_version: 'v2'
                        })
                        await logActivity('recaptcha_v2', {})
                    } catch (v2Error) {
                        console.error('V2 verification failed:', v2Error)
                        // Maybe show a user-friendly error message here
                    }
                }
                requestQueue.value.shift() // Remove the processed request
            } catch (error) {
                console.error('Error logging data:', error)
                requestQueue.value.shift() // Remove failed request to prevent infinite retry
            }
        }
        isProcessing.value = false
    }

    return { logActivity, endStudy }
}