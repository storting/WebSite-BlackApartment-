document.addEventListener('DOMContentLoaded', function() {
    console.log('BlackApartment - Premium Apartment Rentals loaded');
    
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
    
    // API integration for apartment data (можно оставить для будущего использования)
    window.fetchApartments = async function() {
        try {
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
            const response = await fetch(`/api/apartments/${apartmentId}`);
            const apartment = await response.json();
            return apartment;
        } catch (error) {
            console.error('Error fetching apartment details:', error);
            return null;
        }
    };
    
    // Функция renderApartment (если используется)
    window.renderApartment = function(apartmentData) {
        const template = document.querySelector('#apartment-template').content.cloneNode(true);
    
        const img = template.querySelector('img');
        img.src = apartmentData.imageUrl || 'default-image.jpg';
        img.alt = apartmentData.title || '';
    
        const title = template.querySelector('h3');
        title.textContent = apartmentData.title || 'No Title Provided';
    
        const description = template.querySelector('p');
        description.textContent = apartmentData.description || '';
    
        const price = template.querySelector('.text-2xl');
        price.textContent = `${apartmentData.price}/month` || '';
    
        const link = template.querySelector('a');
        link.href = './apartment-detail.html?id=' + apartmentData.id;
        link.textContent = 'VIEW DETAILS';
    };
});