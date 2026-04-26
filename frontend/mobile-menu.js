document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navList = document.querySelector('.nav-list');
    
    // Проверяем наличие элементов перед использованием
    if (!menuToggle || !navList) {
        console.warn('Элементы меню не найдены на странице');
        return;
    }
    
    const icon = menuToggle.querySelector('i');
    
    // Если иконка не найдена, создаем её
    if (!icon) {
        const iconElement = document.createElement('i');
        iconElement.className = 'fas fa-bars';
        menuToggle.appendChild(iconElement);
    }

    function toggleMenu() {
        const isOpen = navList.classList.toggle('active');
        menuToggle.classList.toggle('active', isOpen);
        const currentIcon = menuToggle.querySelector('i');
        if (currentIcon) {
            currentIcon.classList.toggle('fa-bars', !isOpen);
            currentIcon.classList.toggle('fa-times', isOpen);
        }
    }

    function closeMenu() {
        navList.classList.remove('active');
        menuToggle.classList.remove('active');
        const currentIcon = menuToggle.querySelector('i');
        if (currentIcon) {
            currentIcon.classList.add('fa-bars');
            currentIcon.classList.remove('fa-times');
        }
    }

    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMenu();
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.main-nav') && navList.classList.contains('active')) {
            closeMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 992) closeMenu();
    });
});
