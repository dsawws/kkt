function initVKWidget() {
    const vkContainer = document.getElementById("vk_groups");
    if (!vkContainer) return;

    vkContainer.innerHTML = "";

    // Берём реальную ширину контейнера
    const containerWidth = vkContainer.parentElement
        ? vkContainer.parentElement.offsetWidth
        : window.innerWidth;

    const isMobile = window.innerWidth < 768;

    const widgetId = isMobile ? "vk_groups_mobile" : "vk_groups_desktop";
    const widgetParams = {
        mode: 4,
        wide: 1,
        width: Math.max(containerWidth, 300),
        height: isMobile ? 350 : 500,
        color1: "FFFFFF",
        color2: "000000",
        color3: "2e7d32"
    };

    const widgetDiv = document.createElement('div');
    widgetDiv.id = widgetId;
    vkContainer.appendChild(widgetDiv);

    VK.Widgets.Group(widgetId, widgetParams, 218711190);
}

// Функция для обновления виджета при изменении размера
function updateVKWidget() {
    const vkContainer = document.getElementById("vk_groups");
    if (vkContainer) {
        initVKWidget();
    }
}

// Улучшенная функция инициализации с повторными попытками
function initializeVKWidget() {
    if (typeof VK !== 'undefined' && VK.Widgets) {
        // Если API уже загружено, сразу инициализируем
        initVKWidget();
    } else {
        // Если API еще не загружено, ждем его
        let attempts = 0;
        const maxAttempts = 10;

        const checkVKLoaded = setInterval(() => {
            attempts++;

            if (typeof VK !== 'undefined' && VK.Widgets) {
                clearInterval(checkVKLoaded);
                initVKWidget();
            } else if (attempts >= maxAttempts) {
                clearInterval(checkVKLoaded);
                console.warn('VK API не загрузилось после ' + maxAttempts + ' попыток');

                // Показываем fallback сообщение
                const vkContainer = document.getElementById("vk_groups");
                if (vkContainer) {
                    vkContainer.innerHTML = `
                        <div style="text-align: center; padding: 20px; background: #f5f5f5; border-radius: 8px;">
                            <p>Не удалось загрузить виджет ВКонтакте</p>
                            <a href="https://vk.com/belkkt" target="_blank" style="color: #8BC34A; text-decoration: underline;">
                                Перейти в нашу группу ВКонтакте
                            </a>
                        </div>
                    `;
                }
            }
        }, 200);
    }
}

// Инициализация при полной загрузке страницы
window.addEventListener('load', function() {
    initializeVKWidget();
});

// Также пробуем инициализировать при DOMContentLoaded на случай быстрой загрузки
document.addEventListener('DOMContentLoaded', function() {
    // Небольшая задержка для гарантии загрузки VK API
    setTimeout(initializeVKWidget, 100);
});

// Обновляем виджет при изменении размера окна
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateVKWidget, 250);
});

// Дополнительная инициализация через 2 секунды на всякий случай
setTimeout(initializeVKWidget, 2000);