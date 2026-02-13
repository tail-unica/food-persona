/**
 * FocusMonitor
 *
 * A class that monitors user focus and activity on a webpage to ensure continuous engagement.
 * It detects when a user leaves the page or becomes inactive, and provides visual and audio
 * notifications to prompt the user to return.
 * This is necessary to prevent users on Prolific to get paid extra for time spent doing nothing.
 *
 * Features:
 * - Detects when the mouse leaves the window
 * - Monitors window/tab focus state
 * - Tracks user inactivity (lack of mouse movement)
 * - Provides visual overlays for focus and inactivity warnings
 * - Flashes the page title with countdown information
 * - Plays audio notifications to alert the user
 * - Executes callback functions when focus is lost, regained, or times out
 *
 * @example
 * const monitor = new FocusMonitor(
 *   () => console.log('Focus lost'),
 *   () => console.log('Focus regained'),
 *   () => console.log('Session timed out. Redirect to specific endpoint on Prolific')
 * );
 *
 * @param {Function} start_func - Callback function executed when focus is lost
 * @param {Function} stop_func - Callback function executed when focus is regained
 * @param {Function} timedout_func - Callback function executed when the countdown reaches zero
 */

class FocusMonitor {
    constructor(start_func, stop_func, timedout_func) {
        this.defaultCountdown = 60 // seconds of lost focus before automatic return
        this.inactivityThreshold = 50 // seconds before inactivity warning
        this.defaultInactivityCountdown = 25 // seconds to respond to inactivity warning

        // Load persisted values from sessionStorage or use defaults
        this.countdown = this.loadFromSession('focusMonitor_countdown', this.defaultCountdown)
        this.inactivityCountdown = this.loadFromSession('focusMonitor_inactivityCountdown', this.defaultInactivityCountdown)
        this.isCounting = this.loadFromSession('focusMonitor_isCounting', false)
        this.isInactivityWarning = this.loadFromSession('focusMonitor_isInactivityWarning', false)

        this.timer = null
        this.inactivityTimer = null
        this.inactivityWarningTimer = null
        this.lastMouseMoveTime = Date.now()
        this.titleFlashTimer = null
        this.audioContext = null
        this.overlay = this.createOverlay()
        this.inactivityOverlay = this.createInactivityOverlay()
        this.isMouseInWindow = true
        this.isWindowFocused = true
        this.isTabActive = true
        this.originalTitle = document.title
        this.setupEventListeners()
        this.start_func = start_func
        this.stop_func = stop_func
        this.timedout_func = timedout_func

        // Tracking metrics for logging
        this.focusLostCount = this.loadFromSession('focusMonitor_focusLostCount', 0)
        this.totalFocusLostTime = this.loadFromSession('focusMonitor_totalFocusLostTime', 0)
        this.inactivityWarnings = this.loadFromSession('focusMonitor_inactivityWarnings', 0)
        this.focusLostStartTime = this.loadFromSession('focusMonitor_focusLostStartTime', null)

        // Resume timers if they were active before page refresh
        if (this.isCounting) {
            this.resumeCountdown()
        } else if (this.isInactivityWarning) {
            this.resumeInactivityWarning()
        } else {
            // Store the initial state
            this.updateFocusState()
            this.startInactivityCheck()
        }
    }

    loadFromSession(key, defaultValue) {
        try {
            const stored = sessionStorage.getItem(key)
            if (stored !== null) {
                return JSON.parse(stored)
            }
        } catch (e) {
            // sessionStorage not available or parse error
        }
        return defaultValue
    }

    saveToSession(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value))
        } catch (e) {
            // sessionStorage not available
        }
    }

    clearSessionTimers() {
        try {
            sessionStorage.removeItem('focusMonitor_countdown')
            sessionStorage.removeItem('focusMonitor_inactivityCountdown')
            sessionStorage.removeItem('focusMonitor_isCounting')
            sessionStorage.removeItem('focusMonitor_isInactivityWarning')
            sessionStorage.removeItem('focusMonitor_focusLostStartTime')
        } catch (e) {
            // sessionStorage not available
        }
    }

    resumeCountdown() {
        // Resume the focus lost countdown after page refresh
        this.overlay.style.display = 'flex'
        this.startTitleFlash()

        // Stop inactivity checking when main overlay is shown
        if (this.inactivityTimer) {
            clearInterval(this.inactivityTimer)
            this.inactivityTimer = null
        }

        let soundCounter = 0
        this.timer = setInterval(() => {
            if (!this.isCounting) {
                clearInterval(this.timer)
                this.timer = null
                return
            }

            this.countdown--
            this.saveToSession('focusMonitor_countdown', this.countdown)
            this.overlay.textContent = `Please return to the study. Otherwise, your submission will automatically be returned in: ${this.formatTime(this.countdown)}`

            soundCounter++
            if (soundCounter >= 15) {
                this.playNotification()
                soundCounter = 0
            }

            if (this.countdown <= 0) {
                this.stopCountdown()
                this.timedout_func()
            }
        }, 1000)
        this.start_func()
    }

    resumeInactivityWarning() {
        // Resume the inactivity warning after page refresh
        this.inactivityOverlay.style.display = 'flex'
        this.startTitleFlash()

        this.inactivityWarningTimer = setInterval(() => {
            this.inactivityCountdown--
            this.saveToSession('focusMonitor_inactivityCountdown', this.inactivityCountdown)
            this.inactivityOverlay.textContent = `Are you still there? Move your mouse to prevent automatic return (${this.formatTime(this.inactivityCountdown)})`

            if (this.inactivityCountdown <= 0) {
                this.stopInactivityWarning()
                this.timedout_func()
            }
        }, 1000)

        this.playNotification()
    }

    createOverlay() {
        const overlay = document.createElement('div')
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            font-size: 24px;
        `
        document.body.appendChild(overlay)
        return overlay
    }

    createInactivityOverlay() {
        const overlay = document.createElement('div')
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            color: white;
            font-size: 24px;
        `
        document.body.appendChild(overlay)
        return overlay
    }

    startTitleFlash() {
        if (this.titleFlashTimer) return

        let isOriginal = true
        this.titleFlashTimer = setInterval(() => {
            const message = this.isInactivityWarning
                ? `⚠ Move mouse to continue (${this.formatTime(this.inactivityCountdown)})`
                : `⚠ Discarding in ${this.formatTime(this.countdown)}`
            document.title = isOriginal ? message : this.originalTitle
            isOriginal = !isOriginal
        }, 1000)
    }

    stopTitleFlash() {
        if (this.titleFlashTimer) {
            clearInterval(this.titleFlashTimer)
            this.titleFlashTimer = null
            document.title = this.originalTitle
        }
    }

    updateFocusState() {
        const hasFocus = this.isMouseInWindow && this.isWindowFocused && this.isTabActive

        if (!hasFocus) {
            this.startCountdown()
        } else {
            this.checkAndStopCountdown()
        }
    }

    setupEventListeners() {
        // Tab visibility change detection
        document.addEventListener('visibilitychange', () => {
            this.isTabActive = !document.hidden
            this.updateFocusState()
        })

        // Mouse tracking with debouncing for reliability
        let mouseOutTimer
        document.addEventListener('mouseout', (e) => {
            if (e.relatedTarget === null && e.toElement === null) {
                clearTimeout(mouseOutTimer)
                mouseOutTimer = setTimeout(() => {
                    this.isMouseInWindow = false
                    this.updateFocusState()
                }, 100) // Small delay to prevent false triggers
            }
        })

        document.addEventListener('mouseover', () => {
            clearTimeout(mouseOutTimer)
            this.isMouseInWindow = true
            this.updateFocusState()
        })

        // Track user activity (mouse, keyboard, clicks) for inactivity
        const handleActivity = () => {
            this.lastMouseMoveTime = Date.now()
            if (this.isInactivityWarning) {
                this.stopInactivityWarning()
            }
        }

        document.addEventListener('mousemove', handleActivity)
        document.addEventListener('keydown', handleActivity)
        document.addEventListener('click', handleActivity)

        // Window focus/blur - using both window and document events for better cross-browser support
        window.addEventListener('blur', () => {
            this.isWindowFocused = false
            this.updateFocusState()
        })

        window.addEventListener('focus', () => {
            this.isWindowFocused = true
            this.updateFocusState()
        })

        // Additional document-level focus events for better detection
        document.addEventListener('blur', () => {
            this.isWindowFocused = false
            this.updateFocusState()
        })

        document.addEventListener('focus', () => {
            this.isWindowFocused = true
            this.updateFocusState()
        })

        // Handle page visibility changes
        document.addEventListener('pagehide', () => {
            this.isTabActive = false
            this.updateFocusState()
        })

        document.addEventListener('pageshow', () => {
            this.isTabActive = true
            this.updateFocusState()
        })
    }

    startInactivityCheck() {
        if (this.inactivityTimer) return

        this.inactivityTimer = setInterval(() => {
            const timeSinceLastMove = (Date.now() - this.lastMouseMoveTime) / 1000
            if (timeSinceLastMove >= this.inactivityThreshold && !this.isInactivityWarning) {
                this.startInactivityWarning()
            }
        }, 1000)
    }

    startInactivityWarning() {
        // Prevent multiple warnings from being triggered simultaneously
        if (this.isInactivityWarning) return

        // Reset inactivity countdown to default value for each new warning
        this.inactivityCountdown = this.defaultInactivityCountdown

        this.isInactivityWarning = true
        this.inactivityWarnings++
        this.inactivityOverlay.style.display = 'flex'
        this.startTitleFlash()

        // Persist state to sessionStorage
        this.saveToSession('focusMonitor_isInactivityWarning', true)
        this.saveToSession('focusMonitor_inactivityWarnings', this.inactivityWarnings)

        this.inactivityWarningTimer = setInterval(() => {
            this.inactivityCountdown--
            this.saveToSession('focusMonitor_inactivityCountdown', this.inactivityCountdown)
            this.inactivityOverlay.textContent = `Are you still there? Move your mouse to prevent automatic return (${this.formatTime(this.inactivityCountdown)})`

            if (this.inactivityCountdown <= 0) {
                this.stopInactivityWarning()
                this.timedout_func()
            }
        }, 1000)

        this.playNotification()
    }

    stopInactivityWarning() {
        if (!this.isInactivityWarning) return

        this.isInactivityWarning = false
        this.inactivityOverlay.style.display = 'none'
        if (this.inactivityWarningTimer) {
            clearInterval(this.inactivityWarningTimer)
            this.inactivityWarningTimer = null
        }

        // Preserve inactivity countdown value in sessionStorage
        this.saveToSession('focusMonitor_isInactivityWarning', false)
        this.saveToSession('focusMonitor_inactivityCountdown', this.inactivityCountdown)
        this.saveToSession('focusMonitor_inactivityWarnings', this.inactivityWarnings)

        if (!this.isCounting) {
            this.stopTitleFlash()
        }
    }

    checkAndStopCountdown() {
        if (this.isMouseInWindow && this.isWindowFocused && this.isTabActive) {
            this.stopCountdown()
        }
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60)
        const remainingSeconds = seconds % 60
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    async playNotification() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
        }

        const playBeep = () => {
            if (!this.isCounting && !this.isInactivityWarning) return

            const oscillator = this.audioContext.createOscillator()
            const gainNode = this.audioContext.createGain()

            oscillator.connect(gainNode)
            gainNode.connect(this.audioContext.destination)

            oscillator.type = 'sine'
            oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime)
            gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime)

            oscillator.start()
            oscillator.stop(this.audioContext.currentTime + 0.1)
        }

        // Play first beep
        playBeep()

        // Only play second beep if still counting or in warning
        if (this.isCounting || this.isInactivityWarning) {
            await new Promise(resolve => setTimeout(resolve, 200))
            playBeep()
        }
    }

    startCountdown() {
        if (this.isCounting) return
        this.isCounting = true
        this.focusLostCount++
        this.focusLostStartTime = Date.now()
        this.overlay.style.display = 'flex'
        this.startTitleFlash()

        // Persist state to sessionStorage
        this.saveToSession('focusMonitor_isCounting', true)
        this.saveToSession('focusMonitor_focusLostCount', this.focusLostCount)
        this.saveToSession('focusMonitor_focusLostStartTime', this.focusLostStartTime)

        // Stop inactivity checking when main overlay is shown
        if (this.inactivityTimer) {
            clearInterval(this.inactivityTimer)
            this.inactivityTimer = null
        }
        this.stopInactivityWarning()

        let soundCounter = 0
        this.timer = setInterval(() => {
            if (!this.isCounting) {
                clearInterval(this.timer)
                this.timer = null
                return
            }

            this.countdown--
            this.saveToSession('focusMonitor_countdown', this.countdown)
            this.overlay.textContent = `Please return to the study. Otherwise, your submission will automatically be returned in: ${this.formatTime(this.countdown)}`

            soundCounter++
            if (soundCounter >= 15) {
                this.playNotification()
                soundCounter = 0
            }

            if (this.countdown <= 0) {
                this.stopCountdown()
                this.timedout_func()
            }
        }, 1000)
        this.start_func()
    }

    stopCountdown() {
        if (!this.isCounting) return
        this.isCounting = false

        // Track time spent with focus lost
        if (this.focusLostStartTime) {
            this.totalFocusLostTime += Date.now() - this.focusLostStartTime
            this.focusLostStartTime = null
        }

        // Clear active timer state from sessionStorage but preserve countdown value
        this.saveToSession('focusMonitor_isCounting', false)
        this.saveToSession('focusMonitor_countdown', this.countdown)
        this.saveToSession('focusMonitor_totalFocusLostTime', this.totalFocusLostTime)
        this.saveToSession('focusMonitor_focusLostCount', this.focusLostCount)

        this.overlay.style.display = 'none'
        if (!this.isInactivityWarning) {
            this.stopTitleFlash()
        }
        this.stop_func()
        if (this.timer) {
            clearInterval(this.timer)
            this.timer = null
        }

        // Restart inactivity checking when focus is regained
        this.lastMouseMoveTime = Date.now() // Reset the timer
        this.startInactivityCheck()
    }

    setVerifyingCaptcha(verifying) {
        if (verifying) {
            // Disable monitoring without resetting countdown
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }

            if (this.inactivityTimer) {
                clearInterval(this.inactivityTimer);
                this.inactivityTimer = null;
            }

            // Hide overlays while verifying CAPTCHA
            this.overlay.style.display = 'none';
            this.inactivityOverlay.style.display = 'none';

            // Stop title flashing
            this.stopTitleFlash();
        } else {
            // Re-enable monitoring
            this.updateFocusState(); // Check current focus state and restart timers if needed

            // Restart inactivity checking
            if (!this.inactivityTimer && !this.isCounting) {
                this.startInactivityCheck();
            }
        }
    }
}

export default FocusMonitor;