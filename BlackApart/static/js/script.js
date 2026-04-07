document.addEventListener('DOMContentLoaded', function() {
    console.log('BlackApartment - Premium Apartment Rentals loaded');
    
    // Анимации
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Плавный скролл
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
    
    // Мобильное меню
    window.toggleMobileMenu = function() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu) mobileMenu.classList.toggle('hidden');
    };
    
    // Формат цен
    window.formatPrice = function(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0
        }).format(price);
    };
    
    // Календарь для детальной страницы
    window.generateCalendar = function(bookedDates) {
        const calendarDays = document.getElementById('calendarDays');
        if (!calendarDays) return;
        calendarDays.innerHTML = '';
        const today = new Date();
        for (let i = 0; i < 30; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            const dayElement = document.createElement('div');
            dayElement.className = 'text-sm p-2 rounded text-center';
            const dateString = date.toISOString().split('T')[0];
            if (bookedDates.includes(dateString)) {
                dayElement.classList.add('bg-red-500', 'text-white', 'font-medium');
            } else {
                dayElement.classList.add('bg-white', 'text-noir-900', 'border', 'border-noir-300');
            }
            dayElement.textContent = date.getDate();
            calendarDays.appendChild(dayElement);
        }
    };
    
    // Рендер карточки квартиры (если используется шаблонизация)
    window.renderApartment = function(apartmentData) {
        const template = document.querySelector('#apartment-template').content.cloneNode(true);
        const img = template.querySelector('img');
        img.src = apartmentData.imageUrl || 'default-image.jpg';
        img.alt = apartmentData.title || '';
        template.querySelector('h3').textContent = apartmentData.title || '';
        template.querySelector('p').textContent = apartmentData.description || '';
        template.querySelector('.text-2xl').textContent = `${apartmentData.price}/month`;
        template.querySelector('a').href = './apartment-detail.html?id=' + apartmentData.id;
        return template;
    };
});