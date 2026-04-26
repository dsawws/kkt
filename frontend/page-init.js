// Функция для определения текущей страницы
function getCurrentPage() {
    const path = window.location.pathname;
    const pageMap = {
        'abiturient': 'abiturient',
        'student': 'student',
        'teacher': 'teacher',
        'ssk': 'ssk',
        'kredit': 'kredit',
        'antinarko': 'antinarko',
        'profilakika': 'profilakika'
    };

    for (const [key, value] of Object.entries(pageMap)) {
        if (path.includes(key)) {
            return value;
        }
    }
    return null;
}

// Функция загрузки данных страницы
async function loadPageData(pageKey) {
    try {
        // В реальном приложении здесь будет fetch к API
        // const response = await fetch(`/api/pages/${pageKey}`);
        // return await response.json();

        // Временно используем тестовые данные
        return window.pageData[pageKey];
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        return null;
    }
}

// Функция отображения изображений
function renderImages(images, container) {
    if (!images || images.length === 0) return;

    container.style.display = 'block';
    const galleryContainer = document.getElementById('gallery-container');

    images.forEach(image => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        galleryItem.innerHTML = `
            <img src="${image.url}" alt="${image.alt}" class="gallery-image">
            <p class="gallery-caption">${image.caption}</p>
        `;
        galleryContainer.appendChild(galleryItem);
    });
}

// Функция отображения видео
function renderVideos(videos, container) {
    if (!videos || videos.length === 0) return;

    container.style.display = 'block';
    const videosContainer = document.getElementById('videos-container');

    videos.forEach(video => {
        const videoItem = document.createElement('div');
        videoItem.className = 'video-item';
        videoItem.innerHTML = `
            <div class="video-wrapper">
                <div class="video-placeholder">
                    <i class="fas fa-video"></i>
                    <p>Здесь будет видео</p>
                    <p><strong>${video.title}</strong></p>
                </div>
            </div>
            <h3>${video.title}</h3>
            <p>${video.description}</p>
        `;
        videosContainer.appendChild(videoItem);
    });
}

// Функция отображения документов
function renderDocuments(documents, container) {
    if (!documents || documents.length === 0) return;

    container.style.display = 'block';
    const documentsContainer = document.getElementById('documents-container');

    documents.forEach(doc => {
        const docItem = document.createElement('div');
        docItem.className = 'document-item';
        docItem.innerHTML = `
            <div class="document-icon">
                <i class="fas fa-file-pdf"></i>
            </div>
            <div class="document-info">
                <h3>${doc.title}</h3>
                <p>${doc.description}</p>
                <span class="document-size">${doc.size}</span>
            </div>
            <a href="${doc.url}" class="download-btn" download>
                <i class="fas fa-download"></i> Скачать
            </a>
        `;
        documentsContainer.appendChild(docItem);
    });
}

// Основная функция инициализации
async function initializePage() {
    const pageKey = getCurrentPage();

    if (!pageKey) {
        console.log('Страница не найдена в конфигурации');
        return;
    }

    const data = await loadPageData(pageKey);

    if (!data) {
        console.error('Данные для страницы не найдены');
        return;
    }

    // Заполняем основную информацию
    document.getElementById('page-title').textContent = data.title;
    document.getElementById('page-description').textContent = data.description;
    document.getElementById('current-page-title').textContent = data.title;
    document.getElementById('text-content').innerHTML = data.content;

    // Заполняем медиа-контент
    const imagesSection = document.getElementById('images-section');
    const videosSection = document.getElementById('videos-section');
    const documentsSection = document.getElementById('documents-section');

    renderImages(data.images, imagesSection);
    renderVideos(data.videos, videosSection);
    renderDocuments(data.documents, documentsSection);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', initializePage);