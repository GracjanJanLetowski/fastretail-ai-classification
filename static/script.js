document.addEventListener('DOMContentLoaded', () => {
    const browseBtn = document.getElementById('browse-btn');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const uploadForm = document.getElementById('upload-form');
    const loader = document.getElementById('loader');
    const productsGrid = document.getElementById('products-grid');

    // Handle file selection
    browseBtn.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', () => {
        if (imageInput.files.length > 0) {
            fileNameSpan.textContent = imageInput.files[0].name;
        } else {
            fileNameSpan.textContent = 'Ningún archivo seleccionado';
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (imageInput.files.length === 0) {
            alert('Por favor, selecciona una imagen primero.');
            return;
        }

        const formData = new FormData();
        formData.append('file', imageInput.files[0]);

        // UI state management
        loader.classList.remove('hidden');
        uploadForm.classList.add('hidden');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en el servidor');
            }

            const data = await response.json();
            
            // Add new product card to grid
            prependProductCard(data);
            
            // Reset form
            uploadForm.reset();
            fileNameSpan.textContent = 'Ningún archivo seleccionado';
            alert('¡Imagen procesada con éxito!');

        } catch (error) {
            console.error('Error:', error);
            alert(`Error al procesar la imagen: ${error.message}`);
        } finally {
            loader.classList.add('hidden');
            uploadForm.classList.remove('hidden');
        }
    });

    function prependProductCard(data) {
        const card = document.createElement('div');
        card.className = 'product-card';
        
        const labelsHtml = data.labels.map(label => `
            <span class="label" title="Confianza: ${label.Confidence}%">
                ${label.Name}
            </span>
        `).join('');

        const date = new Date().toISOString().slice(0, 16).replace('T', ' ');

        card.innerHTML = `
            <div class="product-image" style="background-image: url('${data.s3_url}')"></div>
            <div class="product-info">
                <h3>${imageInput.files[0].name}</h3>
                <div class="labels">${labelsHtml}</div>
                <small>${date}</small>
            </div>
        `;
        
        productsGrid.insertBefore(card, productsGrid.firstChild);
    }
});
