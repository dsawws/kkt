document.addEventListener('DOMContentLoaded', function () {
    const animatedElements = document.querySelectorAll('.link-card, .news-card, .specialty-card, .profession-card');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach((element) => observer.observe(element));

    const accessibilityToggle = document.getElementById('accessibilityToggle');
    if (accessibilityToggle) {
        accessibilityToggle.addEventListener('click', function () {
            document.body.classList.toggle('accessibility-mode');
            if (document.body.classList.contains('accessibility-mode')) {
                localStorage.setItem('accessibilityMode', 'enabled');
            } else {
                localStorage.setItem('accessibilityMode', 'disabled');
            }
        });
    }
    if (localStorage.getItem('accessibilityMode') === 'enabled') {
        document.body.classList.add('accessibility-mode');
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (!targetId || targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;
            e.preventDefault();
            window.scrollTo({
                top: targetElement.offsetTop - 100,
                behavior: 'smooth',
            });
        });
    });

    function isMobileNav() {
        return window.innerWidth < 992;
    }

    function closeMobileNav() {
        const navList = document.getElementById('navList');
        const menuToggle = document.getElementById('menuToggle');
        if (navList) navList.classList.remove('active');
        document.querySelectorAll('.nav-item.dropdown.active').forEach((d) => d.classList.remove('active'));
        if (menuToggle) {
            const icon = menuToggle.querySelector('i');
            if (icon) icon.className = 'fas fa-bars';
        }
    }

    // Мобильный аккордеон для ВСЕХ пунктов с подменю (одинаково)
    document.querySelectorAll('.nav-item.dropdown').forEach((dropdown) => {
        const link = dropdown.querySelector(':scope > .nav-link');
        if (!link) return;

        link.addEventListener('click', function (e) {
            if (!isMobileNav()) return;
            e.preventDefault();
            e.stopPropagation();
            const willOpen = !dropdown.classList.contains('active');
            document.querySelectorAll('.nav-item.dropdown.active').forEach((other) => {
                if (other !== dropdown) other.classList.remove('active');
            });
            dropdown.classList.toggle('active', willOpen);
        });
    });

    document.querySelectorAll('.dropdown-menu a').forEach((a) => {
        a.addEventListener('click', function () {
            if (!isMobileNav()) return;
            closeMobileNav();
        });
    });

    // Плавный уход со страницы + полоска прогресса + prefetch
    (function initPageTransitions() {
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        document.body.classList.add('page-ready');

        const bar = document.getElementById('nav-progress');
        let progressTimer = null;

        function startProgress() {
            if (!bar || reduce) return;
            bar.classList.add('is-active');
            bar.style.width = '12%';
            clearInterval(progressTimer);
            let w = 12;
            progressTimer = setInterval(function () {
                w = Math.min(w + Math.random() * 12, 88);
                bar.style.width = w + '%';
            }, 180);
        }

        function isInternalNavLink(a) {
            if (!a || a.target === '_blank' || a.hasAttribute('download')) return false;
            const href = a.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) {
                return false;
            }
            try {
                const url = new URL(a.href, window.location.origin);
                if (url.origin !== window.location.origin) return false;
                if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) {
                    return false;
                }
                return true;
            } catch (e) {
                return false;
            }
        }

        document.addEventListener('click', function (e) {
            if (reduce || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
                return;
            }
            const a = e.target.closest('a');
            if (!isInternalNavLink(a)) return;

            // Мобильный аккордеон сам preventDefault на родителях dropdown
            if (isMobileNav() && a.closest('.nav-item.dropdown') && a.matches('.nav-item.dropdown > .nav-link')) {
                return;
            }

            startProgress();
            document.body.classList.add('page-leaving');
        }, true);

        // Prefetch при наведении — страница открывается быстрее
        let prefetchTimer = null;
        document.addEventListener('pointerover', function (e) {
            const a = e.target.closest('a');
            if (!isInternalNavLink(a)) return;
            clearTimeout(prefetchTimer);
            prefetchTimer = setTimeout(function () {
                if (document.querySelector('link[rel="prefetch"][href="' + a.href + '"]')) return;
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = a.href;
                document.head.appendChild(link);
            }, 80);
        });
    })();
});
