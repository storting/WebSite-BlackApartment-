
// NoirNest - Shared JavaScript functionality

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('NoirNest - Premium Apartment Rentals loaded');
    
    // Initialize authentication state
    initializeAuth();
    
    // Add loading animations to elements
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate on scroll
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Mobile menu toggle (if needed in components)
    window.toggleMobileMenu = function() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.toggle('hidden');
        }
    };
    
    // Price formatter for Russian Rubles
    window.formatPrice = function(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0
        }).format(price);
    };
    
    // API integration for apartment data
    window.fetchApartments = async function() {
        try {
            // This would be replaced with actual API endpoint
            const response = await fetch('/api/apartments');
            const apartments = await response.json();
            return apartments;
        } catch (error) {
            console.error('Error fetching apartments:', error);
            return [];
        }
    };
    
    // Filter apartments by criteria
    window.filterApartments = function(apartments, filters) {
        return apartments.filter(apartment => {
            return Object.keys(filters).every(key => {
                if (filters[key] === '') return true;
                return apartment[key] === filters[key];
            });
        });
    };
    
    // Authentication functions
    function initializeAuth() {
        // Check if user is logged in
        const user = getCurrentUser();
        if (user) {
            updateNavbarForLoggedInUser(user);
        }
        
        // Initialize login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
        }
        
        // Initialize register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', handleRegister);
        }
    }
    
    // Handle login form submission
    function handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const email = formData.get('email');
        const password = formData.get('password');
        
        // Simple validation
        if (!email || !password) {
            alert('Please fill in all fields');
            return;
        }
        
        // Mock authentication (replace with actual API call)
        const user = {
            id: 1,
            name: 'John Doe',
            email: email,
            phone: '+7 (999) 123-4567'
        };
        
        // Store user in localStorage
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        // Redirect to home page
        window.location.href = '/';
    }
    // Handle register form submission
    function handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const userType = e.target.id === 'tenantForm' ? 'tenant' : 'landlord';
        
        // Common fields
        const name = formData.get('name');
        const email = formData.get('email');
        const phone = formData.get('phone');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        
        // Validation
        if (!name || !email || !phone || !password || !confirmPassword) {
            alert('Пожалуйста, заполните все обязательные поля');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('Пароли не совпадают');
            return;
        }
        
        // Tenant specific validation
        if (userType === 'tenant') {
            const egrnExtract = formData.get('egrn_extract');
            if (!egrnExtract || egrnExtract.size === 0) {
                alert('Пожалуйста, загрузите выписку из ЕГРН');
                return;
            }
        }
        
        // Landlord specific validation
        if (userType === 'landlord') {
            const birthDate = formData.get('birth_date');
            const passportData = formData.get('passport_data');
        const egrnExtract = formData.get('egrn_extract');
            if (!birthDate) {
                alert('Пожалуйста, укажите дату рождения');
                return;
            }
            if (!passportData) {
                alert('Пожалуйста, заполните паспортные данные');
                return;
            }
            if (!egrnExtract || egrnExtract.size === 0) {
                alert('Пожалуйста, загрузите выписку из ЕГРН');
                return;
            }
        }
        
        // Mock registration (replace with actual API call)
        const user = {
            id: Date.now(),
            name: name,
            email: email,
            phone: phone,
            userType: userType
        };
        
        // Store user in localStorage
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        // Redirect to home page
        window.location.href = '/';
    }
// Get current user from localStorage
    function getCurrentUser() {
        const userJson = localStorage.getItem('currentUser');
        return userJson ? JSON.parse(userJson) : null;
    }
    
    // Update navbar for logged in user
    function updateNavbarForLoggedInUser(user) {
        const userMenuItem = document.getElementById('user-menu-item');
        if (userMenuItem) {
            userMenuItem.innerHTML = `
                <div class="user-menu">
                    <span class="user-name">Hello, ${user.name}</span>
                    <button class="loginBut" onclick="handleLogout()">LOGOUT</button>
                </div>
            `;
        }
    }
    // Handle logout
    window.handleLogout = function() {
        localStorage.removeItem('currentUser');
        window.location.href = '/';
    };

    // Calendar functionality for apartment details
    window.generateCalendar = function(bookedDates) {
        const calendarDays = document.getElementById('calendarDays');
        if (!calendarDays) return;

        calendarDays.innerHTML = '';
        const today = new Date();
        
        // Generate 30 days starting from today
        for (let i = 0; i < 30; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'text-sm p-2 rounded text-center';
            
            // Format date as YYYY-MM-DD
            const dateString = date.toISOString().split('T')[0];
            
            // Check if date is booked
            if (bookedDates.includes(dateString)) {
                dayElement.classList.add('bg-red-500', 'text-white', 'font-medium');
            } else {
                dayElement.classList.add('bg-white', 'text-noir-900', 'border', 'border-noir-300');
            }
            
            dayElement.textContent = date.getDate();
            calendarDays.appendChild(dayElement);
        }
    };
// Fetch apartment details from API
    window.fetchApartmentDetails = async function(apartmentId) {
        try {
            // This would be replaced with actual API endpoint
            const response = await fetch(`/api/apartments/${apartmentId}`);
            const apartment = await response.json();
            return apartment;
        } catch (error) {
            console.error('Error fetching apartment details:', error);
            return null;
        }
    };
// Check if user is logged in
    window.isLoggedIn = function() {
        return getCurrentUser() !== null;
    };
    
    // Redirect if not logged in
    window.requireAuth = function() {
        if (!isLoggedIn()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    };
});