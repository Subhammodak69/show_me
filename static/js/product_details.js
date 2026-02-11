// CSRF Cookie helper
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

// WISHLIST FUNCTIONS
async function loadWishlistProducts() {
    try {
        const res = await fetch('/api/is-liked-status-check/');
        const data = await res.json();
        
        // Reset ALL hearts first (for ALL products on page)
        document.querySelectorAll('.wishlist-icon').forEach(icon => {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            icon.style.color = 'red';
            icon.title = 'Add to wishlist';
        });
        
        // Set filled hearts for wishlist products ONLY
        data.forEach(item => {
            document.querySelectorAll(`.wishlist-icon[data-product-id="${item.product_item_id}"]`)
                .forEach(icon => {
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                    icon.style.color = '#ff4444';
                    icon.title = 'Remove from wishlist';
                });
        });
        
        console.log(`✅ Loaded ${data.length} wishlist products`);
    } catch (error) {
        console.error('Failed to load wishlist status:', error);
    }
}

window.toggle_wishlist_create_update = async function(item_id) {
    console.log("Toggling wishlist for item:", item_id);
    
    const allIcons = document.querySelectorAll(`.wishlist-icon[data-product-id="${item_id}"]`);
    if (allIcons.length === 0) return;

    const isCurrentlyLiked = allIcons[0].classList.contains('bi-heart-fill');
    
    // Instant visual feedback (optimistic update)
    allIcons.forEach(icon => {
        if (isCurrentlyLiked) {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            icon.style.color = 'red';
            icon.title = 'Add to wishlist';
        } else {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
            icon.style.color = '#ff4444';
            icon.title = 'Remove from wishlist';
        }
    });

    try {
        const wishlistUrl = "/wishlist/create_update/"; 
        
        const response = await fetch(wishlistUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        await loadWishlistProducts();
    } catch (error) {
        console.error('Wishlist toggle failed:', error);
        // Revert visual feedback on error
        allIcons.forEach(icon => {
            if (isCurrentlyLiked) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                icon.style.color = '#ff4444';
                icon.title = 'Remove from wishlist';
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                icon.style.color = 'red';
                icon.title = 'Add to wishlist';
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', function () {

    /* ===============================
      DOM ELEMENTS
    ================================ */

    const variantsScript = document.getElementById('product-variants');
    const sizeSelect = document.getElementById('size-select');
    const colorSelect = document.getElementById('color-select');
    const addToCartBtn = document.getElementById('addToCartBtn');
    const buyNowBtn = document.getElementById('buyNowBtn');
    const productImage = document.querySelector('.main-product-image');
    const availabilitySpan = document.getElementById('display-availability');
    const relatedItems = document.querySelectorAll('.related-item'); // 🔥 NEW

    let variants = [];
    let selectedVariantId = null;
    let originalImageSrc = productImage ? productImage.src : '';

    /* ===============================
      LOAD VARIANTS JSON
    ================================ */

    if (variantsScript) {
        try {
            variants = JSON.parse(variantsScript.textContent);
        } catch (e) {
            console.error("JSON Parse Error:", e);
        }
    }

    /* ===============================
      UTILITY FUNCTIONS (UNCHANGED)
    ================================ */

    function loadColors() {
        const uniqueColors = [...new Set(variants.map(v => v.display_color))];
        colorSelect.innerHTML =
            '<option value="">Select Color</option>' +
            uniqueColors.map(color =>
                `<option value="${color}">${color}</option>`
            ).join('');
    }

    function loadSizesByColor(color) {
        const filtered = variants.filter(v => v.display_color === color);
        const uniqueSizes = [...new Set(filtered.map(v => v.display_size))];
        sizeSelect.innerHTML =
            '<option value="">Select Size</option>' +
            uniqueSizes.map(size =>
                `<option value="${size}">${size}</option>`
            ).join('');
    }

    function setAvailability(message, className) {
        if (!availabilitySpan) return;
        availabilitySpan.textContent = message;
        availabilitySpan.className = className;
    }

    function enableButtons() {
        if (addToCartBtn) {
            addToCartBtn.disabled = false;
            addToCartBtn.classList.remove('btn-secondary');
            addToCartBtn.classList.add('btn-warning');
        }
        if (buyNowBtn) {
            buyNowBtn.disabled = false;
            buyNowBtn.classList.remove('btn-secondary');
            buyNowBtn.classList.add('btn-danger');
        }
    }

    function disableButtons() {
        selectedVariantId = null;
        if (addToCartBtn) {
            addToCartBtn.disabled = true;
            addToCartBtn.classList.remove('btn-warning');
            addToCartBtn.classList.add('btn-secondary');
        }
        if (buyNowBtn) {
            buyNowBtn.disabled = true;
            buyNowBtn.classList.remove('btn-danger');
            buyNowBtn.classList.add('btn-secondary');
        }
    }

    /* ===============================
      🔥 NEW: RELATED ITEMS CLICK HANDLER
    ================================ */

    function handleRelatedItemClick(item) {
        const color = item.dataset.color;
        const size = item.dataset.size;
        const image = item.dataset.image;

        // Update main image immediately
        if (productImage && image) {
            productImage.src = image;
        }

        // Auto-select color if available
        if (color && colorSelect) {
            colorSelect.value = color;
            colorSelect.dispatchEvent(new Event('change')); // Trigger color change logic
        }

        // Auto-select size if available (after color change settles)
        setTimeout(() => {
            if (size && sizeSelect) {
                sizeSelect.value = size;
                sizeSelect.dispatchEvent(new Event('change')); // Trigger size change logic
            }
        }, 100);
    }

    // Add click listeners to all related items
    relatedItems.forEach(item => {
        item.addEventListener('click', function() {
            // Visual feedback
            relatedItems.forEach(i => i.style.borderColor = '#dee2e6');
            this.style.borderColor = '#ffc107';
            this.style.borderWidth = '2px';
            
            handleRelatedItemClick(this);
        });
    });

    /* ===============================
      INITIAL LOAD
    ================================ */

    loadColors();
    sizeSelect.innerHTML = '<option value="">Select Size</option>';
    setAvailability('Not selected yet', 'text-muted');
    disableButtons();

    /* ===============================
      COLOR CHANGE (UNCHANGED)
    ================================ */

    colorSelect?.addEventListener('change', function () {
        const selectedColor = this.value;
        selectedVariantId = null;

        if (!selectedColor) {
            sizeSelect.innerHTML = '<option value="">Select Size</option>';
            productImage.src = originalImageSrc;
            setAvailability('Not selected yet', 'text-muted');
            disableButtons();
            return;
        }

        // Change image immediately by color
        const firstVariantWithColor = variants.find(v => v.display_color === selectedColor);
        if (firstVariantWithColor?.image) {
            productImage.src = firstVariantWithColor.image;
        }

        loadSizesByColor(selectedColor);
        setAvailability('Select size', 'text-muted');
        disableButtons();
    });

    /* ===============================
      SIZE CHANGE (UNCHANGED)
    ================================ */

    sizeSelect?.addEventListener('change', function () {
        const selectedColor = colorSelect.value;
        const selectedSize = this.value;

        if (!selectedColor || !selectedSize) {
            setAvailability('Select color and size', 'text-muted');
            disableButtons();
            return;
        }

        const matchingVariant = variants.find(v =>
            v.display_color === selectedColor &&
            v.display_size === selectedSize
        );

        if (!matchingVariant) {
            setAvailability('Combination not available', 'text-danger');
            disableButtons();
            return;
        }

        selectedVariantId = matchingVariant.id;

        if (matchingVariant.image) {
            productImage.src = matchingVariant.image;
        }

        const stock = matchingVariant.stock || 0;
        if (stock > 10) {
            setAvailability('In Stock', 'text-success');
            enableButtons();
        } else if (stock > 0) {
            setAvailability(`Hurry! Only ${stock} left`, 'text-warning');
            enableButtons();
        } else {
            setAvailability('Out of stock', 'text-danger');
            disableButtons();
        }
    });

    /* ===============================
      ACTION BUTTONS (UNCHANGED)
    ================================ */

    window.addToCartDynamic = function (e) {
        e.preventDefault();
        if (selectedVariantId) {
            addToCart(selectedVariantId);
        }
    };

    window.buyNowDynamic = function (e) {
        e.preventDefault();
        if (selectedVariantId) {
            window.location.href = `/direct-order/create/?variant_id=${encodeURIComponent(selectedVariantId)}`;
        }
    };

});




// REVIEW FUNCTIONALITY
function openreviewmodal() {
    document.getElementById('reviewModal').style.display = 'block';
}

// Star rating functionality
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('#starRating .star');
    const ratingInput = document.getElementById('rating');

    stars.forEach(star => {
        star.addEventListener('click', () => {
            star.classList.toggle('selected');
            updateRating();
        });
    });

    function updateRating() {
        let total = 0;
        stars.forEach(star => {
            if (star.classList.contains('selected')) {
                total += parseInt(star.getAttribute('data-value'));
            }
        });
        if (ratingInput) ratingInput.value = total;
        console.log('Current total rating:', total);
    }
});

// Photo upload & preview
document.addEventListener('DOMContentLoaded', function() {
    const photoIcon = document.getElementById('photoIcon');
    const photoInput = document.getElementById('photoInput');
    const photoPreviewContainer = document.getElementById('photoPreviewContainer');
    const photoPreview = document.getElementById('photoPreview');

    if (photoIcon) {
        photoIcon.addEventListener('click', () => {
            if (photoInput) photoInput.click();
        });
    }

    if (photoInput) {
        photoInput.addEventListener('change', () => {
            const file = photoInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    if (photoPreview) photoPreview.src = e.target.result;
                    if (photoPreviewContainer) photoPreviewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                if (photoPreview) photoPreview.src = '';
                if (photoPreviewContainer) photoPreviewContainer.style.display = 'none';
            }
        });
    }
});

// Submit review
document.getElementById('reviewForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    create_review();
});

function create_review() {
    const csrftoken = getCookie('csrftoken');
    const product_id = document.getElementById('product_id').value;
    const rating = document.getElementById('rating').value;
    const review = document.getElementById('review').value;
    const photoInput = document.getElementById('photoInput');

    if (photoInput && photoInput.files.length > 0) {
        const file = photoInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const photo_url = e.target.result;
            sendReviewData(product_id, photo_url, rating, review, csrftoken);
        };
        reader.readAsDataURL(file);
    } else {
        sendReviewData(product_id, '', rating, review, csrftoken);
    }
}

function sendReviewData(product_id, photo_url, rating, review, csrftoken) {
    fetch('/review/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            product_id: product_id,
            photo_url: photo_url,
            rating: rating,
            review: review,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Review submitted successfully!');
            
            // Reset form
            const reviewForm = document.getElementById('reviewForm');
            if (reviewForm) reviewForm.reset();
            
            const ratingField = document.getElementById('rating');
            if (ratingField) ratingField.value = '';
            
            const photoPreview = document.getElementById('photoPreview');
            if (photoPreview) photoPreview.src = '';
            
            const photoPreviewContainer = document.getElementById('photoPreviewContainer');
            if (photoPreviewContainer) photoPreviewContainer.style.display = 'none';

            // Close modal
            const reviewModal = document.getElementById('reviewModal');
            if (reviewModal) reviewModal.style.display = 'none';

            // Add new review to DOM
            const reviewData = data.data;
            const createdByFullname = reviewData.created_by_fullname || 'Anonymous';
            const createdAt = new Date(reviewData.created_at).toLocaleString('en-US', {
                month: 'short', 
                day: '2-digit', 
                year: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit'
            });
            const reviewText = reviewData.review;
            const photoUrl = reviewData.photo;

            let starsHtml = '';
            if (Array.isArray(reviewData.rating_range)) {
                reviewData.rating_range.forEach(() => {
                    starsHtml += '⭐';
                });
            }
            if (Array.isArray(reviewData.empty_range)) {
                reviewData.empty_range.forEach(() => {
                    starsHtml += '☆';
                });
            }

            const reviewsContainer = document.getElementById('reviews-show');
            const noReview = document.getElementById('noReview');
            if (noReview) noReview.style.display = 'none';
            
            if (reviewsContainer) {
                const newReviewDiv = document.createElement('div');
                newReviewDiv.innerHTML = `
                    <div>
                        <div class="d-flex justify-content-between items-center">
                            <div class="d-flex gap-2 font-bold">
                                <p style="font-weight: bold; margin:0px!important;">${createdByFullname}</p>
                                <div style="font-size: medium;color: #75716d;">${createdAt}</div>
                            </div>
                            <div>${starsHtml}</div>
                        </div>
                        <p class="text-gray-700 mb-2 m-auto" style="width:96%;">${reviewText}</p>
                        ${photoUrl ? `<img src="${photoUrl}" alt="Review photo" class="max-w-xs rounded-md mb-2 shadow" />` : ''}
                    </div>
                `;
                reviewsContainer.insertBefore(newReviewDiv, reviewsContainer.firstChild);
            }
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Fetch error: ' + error);
    });
}

// Add to Cart function
function addToCart(ItemInfoId) {
    const csrftoken = getCookie('csrftoken');

    fetch('/cart/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            varient_id: ItemInfoId,
            quantity: 1,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = "/cart/"; 
        } else {
            alert("Failed to add item to cart: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong!');
    });
}

// Initialize wishlist on page load
document.addEventListener('DOMContentLoaded', function() {
    loadWishlistProducts();
});
