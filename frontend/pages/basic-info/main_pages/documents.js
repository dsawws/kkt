// Функция для загрузки и отображения документов
async function loadDocuments() {
    try {
        const response = await fetch('frontend/pages/basic-info/main_pages/pdf/documents.json');
        const data = await response.json();

        // Загружаем основные документы
        loadBasicDocuments(data.documents.basic);

        // Загружаем локальные нормативные акты
        loadLocalDocuments(data.documents.local);

    } catch (error) {
        console.error('Ошибка загрузки документов:', error);
        showError('Не удалось загрузить документы. Пожалуйста, обновите страницу.');
    }
}

// Функция для загрузки основных документов
function loadBasicDocuments(documents) {
    const tbody = document.getElementById('basic-documents-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    documents.forEach(doc => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${doc.id}</td>
            <td>${doc.name}</td>
            <td>
                ${doc.file ? 
                    `<a href="${doc.link}" class="file-link" target="_blank">
                        <i class="fas fa-file-pdf"></i> ${doc.file}
                    </a>` : 
                    `<span class="no-document">${doc.note || 'Документ отсутствует'}</span>`
                }
            </td>
        `;

        tbody.appendChild(row);
    });
}

// Функция для загрузки локальных нормативных актов
function loadLocalDocuments(documents) {
    const tbody = document.getElementById('local-documents-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    documents.forEach(doc => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${doc.id}</td>
            <td>${doc.name}</td>
            <td>
                ${doc.file ? 
                    `<a href="${doc.link}" class="file-link" target="_blank">
                        <i class="fas fa-file-pdf"></i> ${doc.file}
                    </a>` : 
                    `<span class="no-document">${doc.note || 'Документ отсутствует'}</span>`
                }
            </td>
        `;

        tbody.appendChild(row);
    });
}

// Функция для показа ошибки
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;

    const pageContent = document.querySelector('.page-content');
    if (pageContent) {
        pageContent.insertBefore(errorDiv, pageContent.firstChild);
    }
}

// Загружаем документы при загрузке страницы
document.addEventListener('DOMContentLoaded', loadDocuments);