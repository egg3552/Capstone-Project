// Blog JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components when DOM is fully loaded
    initializeBackToTop();
    initializeCommentReplies();
    initializeImageLazyLoading();
    initializeSearchFilters();
    initializeFormValidation();
    
    console.log('Blog JavaScript initialized');
});

// Back to Top Button
function initializeBackToTop() {
    const backToTopButton = createBackToTopButton();
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    // Smooth scroll to top when clicked
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

function createBackToTopButton() {
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.innerHTML = '<i class="fas fa-chevron-up"></i>';
    button.setAttribute('aria-label', 'Back to top');  // Accessibility
    button.style.display = 'none';
    document.body.appendChild(button);
    return button;
}

// Comment Reply System
function initializeCommentReplies() {
    const replyButtons = document.querySelectorAll('.reply-btn');
    
    replyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.getAttribute('data-comment-id');
            const commentForm = document.getElementById('comment-form');
            const parentInput = document.getElementById('parent-comment-id');
            
            if (commentForm && parentInput) {
                parentInput.value = commentId;
                
                // Scroll to comment form
                commentForm.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
                
                // Focus on textarea
                const textarea = commentForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                }
                
                // Update form heading
                const formHeading = commentForm.querySelector('h4');
                if (formHeading) {
                    formHeading.textContent = 'Reply to Comment';
                }
                
                // Add cancel button if not exists
                addCancelReplyButton(commentForm);
            }
        });
    });
}

function addCancelReplyButton(form) {
    let cancelBtn = form.querySelector('.cancel-reply-btn');
    
    if (!cancelBtn) {
        cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.className = 'btn btn-secondary btn-sm cancel-reply-btn ms-2';
        cancelBtn.textContent = 'Cancel Reply';
        
        cancelBtn.addEventListener('click', function() {
            const parentInput = document.getElementById('parent-comment-id');
            const formHeading = form.querySelector('h4');
            
            if (parentInput) parentInput.value = '';
            if (formHeading) formHeading.textContent = 'Add a Comment';
            
            this.remove();
        });
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && submitBtn.parentNode) {
            submitBtn.parentNode.insertBefore(cancelBtn, submitBtn.nextSibling);
        }
    }
}

// Lazy Loading for Images using Intersection Observer API
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    // Check if browser supports Intersection Observer
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;  // Load actual image
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);  // Stop observing
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// Search and Filter Enhancement
function initializeSearchFilters() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.querySelector('input[name="query"]');
    
    if (searchForm && searchInput) {
        // Add search suggestions with debounced input handling
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Implement search suggestions here
                console.log('Searching for:', query);
            }
        }, 300));
        
        // Auto-submit form when filter options change
        const filterSelects = searchForm.querySelectorAll('select');
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                searchForm.submit();
            });
        });
    }
}

// Form Validation Enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormErrors(this);
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const isValid = value !== '';
    
    // Remove existing error styling
    field.classList.remove('is-invalid', 'is-valid');
    
    // Add appropriate styling
    if (field.hasAttribute('required')) {
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    }
    
    return isValid;
}

function showFormErrors(form) {
    const firstInvalidField = form.querySelector('.is-invalid');
    if (firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// Utility Functions

// Debounce function to limit function calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Reading Time Calculator
function calculateReadingTime(text) {
    const wordsPerMinute = 200;
    const words = text.trim().split(/\s+/).length;
    const time = Math.ceil(words / wordsPerMinute);
    return time < 1 ? 1 : time;
}

// Copy to Clipboard with modern and fallback methods
function copyToClipboard(text) {
    // Use modern Clipboard API if available and in secure context
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'absolute';
        textArea.style.left = '-999999px';  // Hide off-screen
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');  // Legacy copy command
            document.body.removeChild(textArea);
            return Promise.resolve();
        } catch (error) {
            document.body.removeChild(textArea);
            return Promise.reject(error);
        }
    }
}

// Share Functionality with Web Share API fallback
function sharePost(title, url) {
    // Use native Web Share API if available
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        }).catch(console.error);
    } else {
        // Fallback to copy URL to clipboard
        copyToClipboard(url).then(() => {
            showToast('Link copied to clipboard!');
        }).catch(() => {
            showToast('Failed to copy link');
        });
    }
}

// Toast Notification System with Bootstrap integration
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');  // Accessibility
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1050';  // Above other content
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Initialize and show toast using Bootstrap
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Clean up DOM after toast is hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Print Page Function
function printPage() {
    window.print();
}

// Dark Mode Toggle with localStorage persistence
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);  // Save preference
}

// Initialize dark mode preference from localStorage
function initializeDarkMode() {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Export functions for external use - Global API
window.BlogJS = {
    showToast,
    sharePost,
    copyToClipboard,
    calculateReadingTime,
    printPage,
    toggleDarkMode
};