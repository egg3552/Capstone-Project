// Blog JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
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
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
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
    button.setAttribute('aria-label', 'Back to top');
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

// Lazy Loading for Images
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
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
        // Add search suggestions (if implemented)
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Implement search suggestions here
                console.log('Searching for:', query);
            }
        }, 300));
        
        // Auto-submit on filter change
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

// Copy to Clipboard Functionality
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'absolute';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        } catch (error) {
            document.body.removeChild(textArea);
            return Promise.reject(error);
        }
    }
}

// Share Functionality
function sharePost(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        }).catch(console.error);
    } else {
        // Fallback to copy URL
        copyToClipboard(url).then(() => {
            showToast('Link copied to clipboard!');
        }).catch(() => {
            showToast('Failed to copy link');
        });
    }
}

// Toast Notification System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
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
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Print Page Function
function printPage() {
    window.print();
}

// Dark Mode Toggle (if implemented)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
}

// Initialize dark mode from localStorage
function initializeDarkMode() {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Export functions for external use
window.BlogJS = {
    showToast,
    sharePost,
    copyToClipboard,
    calculateReadingTime,
    printPage,
    toggleDarkMode
};