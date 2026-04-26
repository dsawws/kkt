function initVKWidget() {
    const screenWidth = window.innerWidth;
    const vkContainer = document.getElementById("vk_groups");

    if (!vkContainer) return;

    // Очищаем контейнер
    vkContainer.innerHTML = "";

    // Определяем параметры для разных устройств
    let widgetId, widgetParams;

    if (screenWidth < 768) {
        // Мобильная версия
        widgetId = "vk_groups_mobile";
        widgetParams = {
            mode: 4,
            wide: 0,
            width: "auto",
            height: 300,
            color1: "FFFFFF",
            color2: "000000",
            color3: "3cae3e"
        };
    } else {
        // Десктоп версия
        widgetId = "vk_groups_desktop";
        widgetParams = {
            mode: 4,
            wide: 1,
            width: "auto",
            height: 400,
            color1: "FFFFFF",
            color2: "000000",
            color3: "3cae3e"
        };
    }

    // Создаем новый div для виджета
    const widgetDiv = document.createElement('div');
    widgetDiv.id = widgetId;
    vkContainer.appendChild(widgetDiv);

    // Инициализируем виджет
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