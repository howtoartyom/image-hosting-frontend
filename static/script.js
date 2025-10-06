/**
 * --- ПОЛУЧЕНИЕ ЭЛЕМЕНТОВ ---
 */

document.addEventListener('DOMContentLoaded', () => {
    const heroPage = document.getElementById('hero-page');
    const mainAppPage = document.getElementById('main-app-page');
    const gotoAppButton = document.getElementById('goto-app-button');
    const navButtons = document.querySelectorAll('.app-nav__button');
    const uploadView = document.getElementById('upload-view');
    const imagesView = document.getElementById('images-view');
    const dropZone = document.getElementById('upload-drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadError = document.getElementById('upload-error');
    const urlInput = document.getElementById('url-input');
    const copyBtn = document.getElementById('copy-btn');
    const imageList = document.getElementById('image-list');
    const imageItemTemplate = document.getElementById('image-item-template');

    const heroImages = [
        'assets/images/bird.png',
        'assets/images/cat.png',
        'assets/images/dog1.png',
        'assets/images/dog2.png',
        'assets/images/dog3.png',
    ];
    let uploadedImages = [];

    gotoAppButton.addEventListener(
        'click',
        () => {
            heroPage.classList.add('hidden');
            mainAppPage.classList.remove('hidden');
        }
    )

    // --- ЛОГИКА НАВИГАЦИИ ---
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const view = button.dataset.view;

            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            if (view === 'upload') {
                uploadView.classList.remove('hidden');
                imagesView.classList.add('hidden');
            } else {
                uploadView.classList.add('hidden');
                imagesView.classList.remove('hidden');
                renderImages();
            }
        })
    })

        // --- ЛОГИКА UPLOAD ---
        function handleFileUpload(file) {
            urlInput.value = '';
            uploadError.classList.add('hidden');

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    urlInput.value = data.url;
                    uploadedImages.push({ id: Date.now(), name: file.name, url: data.url });
                    if (imagesView.classList.contains('hidden')) {
                    } else {
                        renderImages();
                    }
                } else {
                    uploadError.textContent = data.message;
                    uploadError.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Upload failed:', error);
                uploadError.textContent = 'Upload failed due to network error.';
                uploadError.classList.remove('hidden');
            });
        }

        browseBtn.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) handleFileUpload(fileInput.files[0]);
        });
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0]);
        });
        copyBtn.addEventListener('click', () => {
            if (urlInput.value) {
                navigator.clipboard.writeText(urlInput.value).then(() => {
                    copyBtn.textContent = 'COPIED!';
                    setTimeout(() => {
                        copyBtn.textContent = 'COPY';
                    }, 2000);
                });
            }
        });

        let currentPage = 1;

        async function renderImages(page = 1) {
            try {
                const response = await fetch(`/images-list?page=${page}`);
                const data = await response.json();
                console.log(data);
                console.log(data.pagination);
                console.log(data.images);
                console.log(data.images.length);

                imageList.innerHTML = '';
                const paginationContainer = document.getElementById('pagination');

                if (data.images.length === 0) {
                    imageList.innerHTML = '<p style="text-align:center;">Нет изображений</p>';
                    paginationContainer.innerHTML = ''; // Очищаем пагинацию если нет изображений
                    return;
                }

                // Отрисовка изображений
                data.images.forEach(image => {
                    const templateClone = imageItemTemplate.content.cloneNode(true);
                    templateClone.querySelector('.image-item').dataset.id = image.id;
                    templateClone.querySelector('.image-item__name span').textContent = image.original_name;
                    const urlLink = templateClone.querySelector('.image-item__url a');
                    urlLink.href = `/images/${image.filename}`;
                    urlLink.textContent = `/images/${image.filename}`;
                    imageList.appendChild(templateClone);
                });

                // Обновление пагинации
                if (paginationContainer) {
                    paginationContainer.innerHTML = `
                        <button id="prev-page" ${!data.pagination.has_prev ? 'disabled' : ''}>
                            Предыдущая страница
                        </button>
                        <span>Страница ${data.pagination.current_page} из ${data.pagination.total_pages}</span>
                        <button id="next-page" ${!data.pagination.has_next ? 'disabled' : ''}>
                            Следующая страница
                        </button>
                    `;

                    // Обработчики пагинации
                    document.getElementById('prev-page')?.addEventListener('click', () => {
                        if (currentPage > 1) {
                            currentPage--;
                            renderImages(currentPage);
                        }
                    });

                    document.getElementById('next-page')?.addEventListener('click', () => {
                        if (data.pagination.has_next) {
                            currentPage++;
                            renderImages(currentPage);
                        }
                    });
                }

            } catch (e) {
                console.error('Ошибка загрузки списка:', e);
                const paginationContainer = document.getElementById('pagination');
                if (paginationContainer) {
                    paginationContainer.innerHTML = ''; // Очищаем пагинацию в случае ошибки
                }
            }
        }

        imageList.addEventListener('click', async (e) => {
                const deleteButton = e.target.closest('.delete-btn');
                if (deleteButton) {
                    const listItem = e.target.closest('.image-item');
                    const imageId = listItem.dataset.id;
                if (confirm('Удалить изображение?')) {
                     try {
                         const response = await fetch(`/delete/${imageId}`, { method: 'DELETE' });
                        if (response.ok)
                            renderImages();
            } catch (e) {
                console.error('Ошибка удаления:', e); // Обработка ошибок
            }
        }
    }
})})
