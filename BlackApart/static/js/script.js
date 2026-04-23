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

document.addEventListener('DOMContentLoaded', function() {
    const addressInputs = document.querySelectorAll('input[name="address"]');

    addressInputs.forEach(input => {
        let timeoutId = null;
        let suggestionsBox = null;

        function createSuggestionsBox() {
            if (suggestionsBox && suggestionsBox.parentNode) {
                suggestionsBox.remove();
            }
            suggestionsBox = document.createElement('div');
            suggestionsBox.className = 'suggestions-box';
            suggestionsBox.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                z-index: 1050;
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 4px;
                max-height: 200px;
                overflow-y: auto;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            `;
            input.parentNode.style.position = 'relative';
            input.insertAdjacentElement('afterend', suggestionsBox);
        }

        input.addEventListener('input', function(e) {
            clearTimeout(timeoutId);
            const query = this.value.trim();
            if (query.length < 3) {
                if (suggestionsBox) suggestionsBox.remove();
                return;
            }

            createSuggestionsBox();
            suggestionsBox.innerHTML = '<div style="padding: 8px 12px; color: #999;">Загрузка...</div>';

            timeoutId = setTimeout(() => {
                fetch('https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': 'Token 7f81793d693067004f13aa50bf1ca55d7b661c74'
                    },
                    body: JSON.stringify({ query: query })
                })
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    if (data.suggestions && data.suggestions.length) {
                        data.suggestions.forEach(suggestion => {
                            const option = document.createElement('div');
                            option.textContent = suggestion.value;
                            option.style.cssText = 'padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #eee;';
                            option.addEventListener('click', function() {
                                input.value = suggestion.value;
                                suggestionsBox.remove();
                                const form = input.closest('form');
                                if (form && form.method === 'get') {
                                    form.submit();
                                }
                            });
                            suggestionsBox.appendChild(option);
                        });
                    } else {
                        suggestionsBox.innerHTML = '<div style="padding: 8px 12px; color: #999;">Ничего не найдено</div>';
                    }
                })
                .catch(error => {
                    console.error('Ошибка DaData:', error);
                    suggestionsBox.innerHTML = '<div style="padding: 8px 12px; color: #999;">Ошибка при загрузке</div>';
                });
            }, 300);
        });

        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && (!suggestionsBox || !suggestionsBox.contains(e.target))) {
                if (suggestionsBox) suggestionsBox.remove();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const birthDateInput = document.querySelector('input[name="birth_date"]');
    if (birthDateInput) {
        flatpickr(birthDateInput, {
            dateFormat: "Y-m-d",
            locale: "ru",
            allowInput: true,
            altInput: true,
            altFormat: "d.m.Y",
        });
    }
});