document.addEventListener('DOMContentLoaded', function() {
    // Initialize all DOM elements
    const dashboardImage = document.querySelector('.floating-dashboard');
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const preloader = document.querySelector('.preloader');
    const themeToggle = document.querySelector('.theme-toggle');
    const themeDropdown = document.querySelector('.theme-dropdown');
    const navToggle = document.querySelector('.nav-toggle');
    const mainNav = document.querySelector('.main-nav');
    const navButtons = document.querySelector('.nav-buttons');
    const checkbox = document.querySelector('#checkbox');

    console.log('App initialized');

    // Initialize dashboard image if it exists
    if (dashboardImage) {
        console.log('Dashboard image initialized');
        dashboardImage.addEventListener('load', function() {
            console.log('Dashboard image loaded successfully');
        });
        dashboardImage.addEventListener('error', function() {
            console.error('Failed to load dashboard image');
        });
    } else {
        console.log('Dashboard image element not found - skipping initialization');
    }

    // Theme switcher
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    }

    function switchTheme(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }    
    }

    toggleSwitch.addEventListener('change', switchTheme, false);

    // Preloader
    if (preloader) {
        // Show preloader on page load
        preloader.style.display = 'flex';
        
        // Hide preloader after animation
        setTimeout(() => {
            preloader.classList.add('fade-out');
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }, 3000);
    }

    // Responsive Navigation and Theme Toggle
    function handleResponsive() {
        const isMobileOrTablet = window.innerWidth <= 1024;
        const isMobile = window.innerWidth <= 768;
        
        if (isMobileOrTablet) {
            if (navToggle) navToggle.style.display = 'block';
            
            // Don't hide nav if it's active
            if (mainNav && !mainNav.classList.contains('active')) {
                mainNav.style.display = 'none';
            }
            
            // Ensure theme dropdown is properly positioned for mobile
            if (isMobile && themeDropdown) {
                themeDropdown.style.cssText = `
                    position: fixed !important;
                    top: 60px !important;
                    right: 10px !important;
                    z-index: 1000 !important;
                    background: var(--bg-secondary) !important;
                    padding: 10px !important;
                    border-radius: 4px !important;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
                    min-width: 200px !important;
                `;
            }
        } else {
            if (navToggle) navToggle.style.display = 'none';
            if (mainNav) {
                mainNav.style.display = 'flex';
                mainNav.classList.remove('active');
            }
            if (navToggle) {
                const icon = navToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                }
            }
            // Reset theme dropdown on desktop
            if (themeDropdown) {
                themeDropdown.style.cssText = '';
                themeDropdown.style.display = 'none';
                themeDropdown.classList.remove('active');
            }
            if (themeToggle) {
                const themeIcon = themeToggle.querySelector('i');
                if (themeIcon) {
                    themeIcon.classList.remove('fa-xmark');
                    themeIcon.classList.add('fa-gear');
                }
            }
        }
    }

    // Theme toggle functionality
    if (themeToggle && themeDropdown) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const isMobile = window.innerWidth <= 768;
            
            // Toggle dropdown visibility
            const isVisible = themeDropdown.classList.contains('active');
            
            if (!isVisible) {
                themeDropdown.classList.add('active');
                themeDropdown.style.display = 'block';
                
                // Set mobile-specific styles
                if (isMobile) {
                    themeDropdown.style.position = 'fixed';
                    themeDropdown.style.top = '70px';
                    themeDropdown.style.right = '1rem';
                    themeDropdown.style.width = '200px';
                    themeDropdown.style.zIndex = '1000';
                }
                
                // Close nav menu if open
                if (mainNav && mainNav.classList.contains('active')) {
                    mainNav.classList.remove('active');
                    mainNav.style.display = 'none';
                    if (navToggle) {
                        const navIcon = navToggle.querySelector('i');
                        if (navIcon) {
                            navIcon.classList.remove('fa-xmark');
                            navIcon.classList.add('fa-bars');
                        }
                    }
                }
            } else {
                themeDropdown.classList.remove('active');
                themeDropdown.style.display = 'none';
            }
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        // Close theme dropdown if clicking outside
        if (themeToggle && themeDropdown && 
            !themeToggle.contains(e.target) && 
            !themeDropdown.contains(e.target)) {
            themeDropdown.classList.remove('active');
            themeDropdown.style.display = 'none';
        }

        // Only close mobile menu if clicking outside AND we're in mobile view
        // AND not clicking any nav-related elements
        if (window.innerWidth <= 1024 && navToggle && mainNav && 
            !navToggle.contains(e.target) && 
            !mainNav.contains(e.target) &&
            !e.target.closest('.nav-controls') &&
            !e.target.closest('.main-header') &&  // Don't close when clicking header
            !e.target.closest('.nav-btn') &&      // Don't close when clicking nav buttons
            e.target.tagName !== 'BUTTON' &&      // Don't close when clicking buttons
            !e.target.closest('.theme-dropdown')) {  // Don't close when clicking theme dropdown
            mainNav.classList.remove('active');
            mainNav.style.display = 'none';
            const navIcon = navToggle.querySelector('i');
            if (navIcon) {
                navIcon.classList.remove('fa-xmark');
                navIcon.classList.add('fa-bars');
            }
        }
    });

    // Initial responsive check and window resize handler
    handleResponsive();
    window.addEventListener('resize', handleResponsive);

    // Theme switch handler
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            // Invert the theme logic - unchecked (sun) = light, checked (moon) = dark
            const newTheme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Set initial theme based on localStorage or system preference
    const savedTheme = localStorage.getItem('theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (checkbox) {
        // Set checkbox based on inverted logic
        checkbox.checked = savedTheme === 'dark';
    }

    // Handle preloader
    window.addEventListener('load', function() {
        if (preloader) {
            setTimeout(() => {
                preloader.style.opacity = '0';
                setTimeout(() => {
                    preloader.style.display = 'none';
                }, 500);
            }, 1500);
        }
    });

    // Navigation toggle functionality - Move inside DOMContentLoaded
    if (navToggle && mainNav) {
        navToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isActive = mainNav.classList.contains('active');
            
            // Toggle navigation visibility
            mainNav.classList.toggle('active');
            mainNav.style.display = isActive ? 'none' : 'block';
            
            // Toggle hamburger icon
            const icon = this.querySelector('i');
            if (icon) {
                if (isActive) {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                } else {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-xmark');
                }
            }
            
            // Close theme dropdown if open
            if (themeDropdown && themeDropdown.classList.contains('active')) {
                themeDropdown.classList.remove('active');
                themeDropdown.style.display = 'none';
            }
        });
    }
});

// Show preloader before page unload
window.addEventListener('beforeunload', function() {
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        preloader.classList.remove('fade-out');
        preloader.style.display = 'flex';
    }
});

// Add responsive chart handling
window.addEventListener('resize', function() {
    if (window.trendChart) {
        window.trendChart.resize();
    }
});

// Remove the duplicate navigation toggle functionality from outside DOMContentLoaded
// ... existing code for window event listeners ... 