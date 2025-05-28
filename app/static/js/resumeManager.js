// Global function to reset everything
function resetPageState() {
    try {
        sessionStorage.clear();
        localStorage.clear();
        console.log('Page state reset (global function from resumeManager.js)');
    } catch (e) {
        console.log('Error in global resetPageState (from resumeManager.js):', e);
    }
}

// Call global reset immediately when this script loads
// We assume this script is loaded AFTER the main page elements it might try to manipulate initially,
// or that such manipulations are guarded.
console.log('resumeManager.js: EXECUTING SCRIPT FILE - resetPageState() is next.');
resetPageState();

console.log('resumeManager.js: SCRIPT BLOCK for resumeManager DEFINITION: STARTING');

// Attempt to hide success message directly, before Alpine init
// This might run before the DOM is fully ready, so we'll wrap it or ensure it's robust.
document.addEventListener('DOMContentLoaded', () => {
    try {
        const successDivPreAlpine = document.getElementById('resumeSuccessMessage');
        if (successDivPreAlpine) {
            console.log('resumeManager.js (DOMContentLoaded): Pre-Alpine - Attempting to hide successDiv by ID.');
            successDivPreAlpine.style.display = 'none';
        } else {
            console.log('resumeManager.js (DOMContentLoaded): Pre-Alpine - successDivPreAlpine not found.');
        }
    } catch(e) {
        console.log('resumeManager.js (DOMContentLoaded): Pre-Alpine - Error hiding successDiv by ID:', e);
    }
});

function resumeManager() {
    console.log('resumeManager.js: resumeManager FUNCTION BODY EXECUTED (Alpine should pick this up)');
    return {
        // State variables (restored)
        resumeUploaded: false,
        uploadedFileName: '',
        resumeText: '',
        manualResumeText: '',
        isUploading: false,
        uploadError: null,
        dragOver: false, // Restored

        // INITIALIZATION
        init() {
            console.log('resumeManager.js: Alpine Component init() CALLED');
            this.nuclearReset(); // Call the comprehensive reset
            console.log('resumeManager.js: Alpine init() - State after nuclearReset(): resumeUploaded is', this.resumeUploaded);

            // Final check to hide success message
            const successDiv = document.getElementById('resumeSuccessMessage');
            if (successDiv) {
                console.log('resumeManager.js: Alpine init() - Forcing resumeSuccessMessage to display:none');
                successDiv.style.display = 'none';
            }
            console.log('resumeManager.js: Alpine init() FINISHED');
        },

        nuclearReset() {
            console.log('resumeManager.js: nuclearReset() CALLED');
            try {
                sessionStorage.clear();
                localStorage.clear(); // Redundant with global reset, but safe
                this.resumeUploaded = false;
                this.uploadedFileName = '';
                this.resumeText = '';
                this.manualResumeText = '';
                this.uploadError = null;
                this.isUploading = false;
                this.dragOver = false;
                console.log('resumeManager.js: nuclearReset() - All state and storage cleared.');
            } catch (error) {
                console.error('resumeManager.js: Error in nuclearReset():', error);
            }
        },

        handleFileSelect(event) {
            console.log('resumeManager.js: handleFileSelect triggered');
            const file = event.target.files[0];
            if (file) {
                this.uploadFile(file);
            }
            event.target.value = null; // Reset file input
        },

        handleFileDrop(event) {
            console.log('resumeManager.js: handleFileDrop triggered');
            this.dragOver = false;
            const file = event.dataTransfer.files[0];
            if (file) {
                this.uploadFile(file);
            }
        },

        async uploadFile(file) {
            console.log('resumeManager.js: uploadFile called with file:', file.name);
            this.isUploading = true;
            this.uploadError = null;
            this.resumeUploaded = false;

            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await axios.post("/extract-resume-text", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
                console.log('resumeManager.js: /extract-resume-text response', response.data);
                if (response.data && response.data.resume_text) {
                    this.storeResumeData(response.data.resume_text, file.name);
                } else {
                    throw new Error(response.data.detail || "Failed to extract text from resume.");
                }
            } catch (error) {
                console.error('resumeManager.js: Error uploading or processing file:', error);
                this.uploadError = error.response?.data?.detail || error.message || "An unknown error occurred during file upload.";
                this.resumeUploaded = false;
            } finally {
                this.isUploading = false;
                console.log('resumeManager.js: uploadFile finished. resumeUploaded:', this.resumeUploaded, 'Error:', this.uploadError);
            }
        },

        saveManualResume() {
            console.log('resumeManager.js: saveManualResume called');
            if (!this.manualResumeText.trim()) {
                this.uploadError = "Please paste some resume text.";
                return;
            }
            this.isUploading = true; // Show loading state
            this.uploadError = null;
            // Simulate a short delay as if processing text, then store it
            setTimeout(() => {
                this.storeResumeData(this.manualResumeText, "Pasted Resume");
                this.manualResumeText = ""; // Clear textarea
                this.isUploading = false;
                console.log('resumeManager.js: Manual resume saved. resumeUploaded:', this.resumeUploaded);
            }, 500);
        },
        
        storeResumeData(text, fileName) {
            console.log('resumeManager.js: storeResumeData called. FileName:', fileName);
            const resumeData = {
                text: text,
                fileName: fileName,
                uploadedAt: new Date().toISOString()
            };
            try {
                sessionStorage.setItem('resumeData', JSON.stringify(resumeData));
                this.resumeText = text;
                this.uploadedFileName = fileName;
                this.resumeUploaded = true;
                this.uploadError = null;
                console.log('resumeManager.js: Resume data stored in sessionStorage and Alpine state. resumeUploaded:', this.resumeUploaded);
            } catch (e) {
                console.error('resumeManager.js: Error storing resume data in sessionStorage:', e);
                this.uploadError = "Could not store resume data. Session storage might be full or disabled.";
                this.resumeUploaded = false;
            }
        },

        clearResume() {
            console.log('resumeManager.js: clearResume CALLED');
            this.resumeUploaded = false;
            this.uploadedFileName = '';
            this.resumeText = '';
            this.manualResumeText = '';
            this.uploadError = null;
            try {
                sessionStorage.removeItem('resumeData');
                console.log('resumeManager.js: resumeData removed from sessionStorage.');
            } catch (e) {
                 console.error('resumeManager.js: Error removing resumeData from sessionStorage:', e);
            }
        },

        navigateToFeature(feature) {
            console.log('resumeManager.js: navigateToFeature called for:', feature);
            if (!this.resumeUploaded) {
                alert("Please upload a resume first.");
                return;
            }
            // Store a flag or specific data if needed before navigation
            sessionStorage.setItem('resumePreloadedForFeature', feature); // Changed key name
            
            if (feature === 'analyzer') {
                window.location.href = '/resume-analysis';
            } else if (feature === 'interview') {
                window.location.href = '/interview-assistant';
            } else if (feature === 'salary') {
                window.location.href = '/salary-intelligence';
            }
        }
    };
}

console.log('resumeManager.js: SCRIPT BLOCK for resumeManager DEFINITION: ENDED');

// It's good practice to ensure Alpine.js initializes after the DOM is ready.
// If Alpine.js is included with `defer`, this is often handled automatically.
// If not, or for extra safety:
document.addEventListener('alpine:init', () => {
    console.log('resumeManager.js: alpine:init event fired. Alpine is ready.');
    // You can register components here if needed, but x-data in HTML usually suffices.
});

console.log('resumeManager.js: SCRIPT FILE EXECUTION FINISHED.'); 