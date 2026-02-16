document.addEventListener('DOMContentLoaded', function() {
    loadExtraProductImages();
});

async function loadExtraProductImages() {
    const container = document.getElementById('extraProductsContainer');
    const productItemId = document.getElementById('product_item_id').value;
    
    try {
        const response = await fetch(`/api/extra-product-images/${productItemId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExtraProducts(data.extra_product_images || data.extra_products);
        } else {
            container.innerHTML = '<div class="text-center text-muted p-2"><small>No extra images</small></div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="text-center text-muted p-2"><small>Error loading images</small></div>';
    }
}

function displayExtraProducts(products) {
    const container = document.getElementById('extraProductsContainer');
    
    if (!products || products.length === 0) {
        container.innerHTML = '<div class="text-center text-muted p-2"><small>No extra images</small></div>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="border text-center flex-shrink-0 mx-1 mb-2 cursor-pointer" 
            style="width: 70px; height:50px; cursor: pointer; transition: all 0.3s ease; border: 2px solid transparent;"
            onclick=" this.style.boxShadow='0 0 0 3px rgba(0,123,255,0.50)'; changeMainPic('${product.photo_url}')"
            onmouseover="this.style.border=='3px solid #007bff' ? null : (this.style.transform='scale(1.05)', this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)')"
            onmouseout="this.style.border=='3px solid #007bff' ? null : (this.style.transform='scale(1)', this.style.boxShadow='none')">
          <img src="${product.photo_url}" 
                class="img-fluid w-100 h-100" 
                style="height: 100%; width: 100%; object-fit: cover;"
                alt="Extra image">
        </div>

    `).join('');
}

function changeMainPic(imageUrl) {
    const mainPic = document.getElementById('mainPic');
    if (mainPic) {
        mainPic.src = imageUrl;  // ✅ FIXED: Proper string interpolation
        mainPic.style.opacity = '0.5';
        mainPic.onload = () => mainPic.style.opacity = '1';
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
