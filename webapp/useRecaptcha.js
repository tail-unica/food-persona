/**
 * useRecaptcha.js
 * A Vue composable for handling both reCAPTCHA v2 and v3 integrations.
 * 
 * This composable provides functionality to:
 * - Load reCAPTCHA v2 and v3 scripts
 * - Execute reCAPTCHA v3 challenges
 * - Display reCAPTCHA v2 dialog when needed
 */
import { ref } from 'vue'
/**
 * Creates a reCAPTCHA integration that supports both v2 and v3
 * 
 * @param {string} v3SiteKey - The Google reCAPTCHA v3 site key
 * @param {string} v2SiteKey - The Google reCAPTCHA v2 site key
 * @returns {Object} - Methods and reactive properties for reCAPTCHA integration
 */
export function useRecaptcha(v3SiteKey, v2SiteKey) {
    // Reactive state
    const isLoaded = ref(false)  // Tracks if reCAPTCHA scripts have loaded
    const token = ref('')        // Stores the most recent reCAPTCHA token

    /**
     * Loads both reCAPTCHA v2 and v3 scripts immediately
     */
    const loadScripts = () => {
        // Load reCAPTCHA v3 script
        const scriptV3 = document.createElement('script')
        scriptV3.src = `https://www.google.com/recaptcha/api.js?render=${v3SiteKey}`

        // Load reCAPTCHA v2 script
        const scriptV2 = document.createElement('script')
        scriptV2.src = 'https://www.google.com/recaptcha/api.js'

        // Wait for both scripts to load before setting isLoaded to true
        Promise.all([
            new Promise(resolve => {
                scriptV3.onload = resolve
                document.head.appendChild(scriptV3)
            }),
            new Promise(resolve => {
                scriptV2.onload = resolve
                document.head.appendChild(scriptV2)
            })
        ]).then(() => {
            isLoaded.value = true
            console.log('reCAPTCHA scripts loaded successfully')
        }).catch(error => {
            console.error('Failed to load reCAPTCHA scripts:', error)
        })
    }

    // Load scripts immediately when useRecaptcha is called
    loadScripts()

    /**
     * Executes a reCAPTCHA v3 challenge
     * 
     * @param {string} action - The action name to be associated with this verification
     * @returns {Promise<string>} - A promise that resolves to the reCAPTCHA token
     * @throws {Error} - If reCAPTCHA execution fails
     */
    const executeRecaptchaV3 = async (action) => {
        // Wait for reCAPTCHA to load if it hasn't already
        if (!isLoaded.value) {
            await new Promise(resolve => {
                const checkLoaded = setInterval(() => {
                    if (isLoaded.value) {
                        clearInterval(checkLoaded)
                        resolve()
                    }
                }, 100)
            })
        }

        try {
            // Execute reCAPTCHA v3 and store the token
            token.value = await window.grecaptcha.execute(v3SiteKey, { action })
            return token.value
        } catch (error) {
            console.error('reCAPTCHA v3 execution failed:', error)
            throw error
        }
    }

    /**
     * Displays a modal dialog with reCAPTCHA v2 challenge
     * 
     * @param {Object} focusMonitor - An object that tracks focus state for the application
     * @returns {Promise<string>} - A promise that resolves to the reCAPTCHA token when verification completes
     */
    const showRecaptchaV2Dialog = (focusMonitor) => {
        return new Promise((resolve) => {
            // Update UI state to show we're verifying with CAPTCHA
            focusMonitor.setVerifyingCaptcha(true)
            
            // Create modal for v2 CAPTCHA
            const modal = document.createElement('div')
            modal.innerHTML = `
                <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 9999;">
                    <div style="background: white; padding: 20px; border-radius: 8px; max-width: 400px; width: 100%;">
                        <h3 style="margin-top: 0;">Please Verify</h3>
                        <p>For security purposes, please complete this quick verification.</p>
                        <div id="recaptcha-container"></div>
                        <p style="font-size: 0.8em; color: #666;">This helps us ensure the quality of our study data. Thank you for your understanding.</p>
                    </div>
                </div>`
            document.body.appendChild(modal)

            // Render the v2 CAPTCHA in the modal
            window.grecaptcha.render('recaptcha-container', {
                sitekey: v2SiteKey,
                callback: (response) => {
                    // Reset UI state when verification is complete
                    focusMonitor.setVerifyingCaptcha(false)
                    modal.remove()
                    resolve(response)
                }
            })
        })
    }

    // Return public API
    return {
        executeRecaptchaV3,
        showRecaptchaV2Dialog,
        isLoaded,
        token
    }
}
