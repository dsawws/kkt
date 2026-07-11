// Анимация появления элементов при скролле
document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов при скролле
    const animatedElements = document.querySelectorAll('.link-card, .news-card, .specialty-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    const adminPanel = document.createElement('div');
    adminPanel.className = 'admin-panel';
    adminPanel.innerHTML = `
        <div class="admin-panel-btn" id="adminPanelBtn">
            <i class="fas fa-cog"></i>
        </div>
    `;
    document.body.appendChild(adminPanel);
    
    // Проверяем, авторизован ли пользователь
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
        // Показываем кнопку админ-панели
        document.getElementById('adminPanelBtn').style.display = 'flex';
        
        // Добавляем обработчик клика
        document.getElementById('adminPanelBtn').addEventListener('click', function() {
            window.open('/admin/', '_blank');
        });
    } else {
        // Скрываем кнопку админ-панели
        document.getElementById('adminPanelBtn').style.display = 'none';
    }
    
    // Функция для версии для слабовидящих
    const accessibilityToggle = document.getElementById('accessibilityToggle');
    if (accessibilityToggle) {
        accessibilityToggle.addEventListener('click', function() {
            document.body.classList.toggle('accessibility-mode');
            
            if (document.body.classList.contains('accessibility-mode')) {
                localStorage.setItem('accessibilityMode', 'enabled');
            } else {
                localStorage.setItem('accessibilityMode', 'disabled');
            }
        });
    }
    
    // Проверяем, была ли включена версия для слабовидящих
    if (localStorage.getItem('accessibilityMode') === 'enabled') {
        document.body.classList.add('accessibility-mode');
    }
});
    // Версия для слабовидящих
    const accessibilityToggle = document.getElementById('accessibilityToggle');
    
    if (accessibilityToggle) {
        accessibilityToggle.addEventListener('click', function() {
            document.body.classList.toggle('accessibility-mode');
            
            if (document.body.classList.contains('accessibility-mode')) {
                localStorage.setItem('accessibilityMode', 'enabled');
            } else {
                localStorage.setItem('accessibilityMode', 'disabled');
            }
        });
    }
    
    // Проверяем, была ли включена версия для слабовидящих
    if (localStorage.getItem('accessibilityMode') === 'enabled') {
        document.body.classList.add('accessibility-mode');
    }
    
    // Плавная прокрутка для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Обработка выпадающих меню на мобильных устройствах
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (window.innerWidth < 992) {
                this.classList.toggle('open');
            }
        });
    });

