// Auto-init wishlist on page load
document.addEventListener('DOMContentLoaded', function() {
    loadWishlistProducts();  // 🔥 CHECK WISHLIST STATUS ON PAGE LOAD
});

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

// 🔥 PAGE LOAD: Check wishlist status for ALL products
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

// 🔥 TOGGLE: Update one product, then refresh ALL hearts
window.toggle_wishlist_create_update = async function(item_id) {
    console.log("Toggling wishlist for item:", item_id);
    
    const allIcons = document.querySelectorAll(`.wishlist-icon[data-product-id="${item_id}"]`);
    if (allIcons.length === 0) return;

    const firstIcon = allIcons[0];
    const isCurrentlyLiked = firstIcon.classList.contains('bi-heart-fill');
    
    console.log("Current state - isLiked:", isCurrentlyLiked); // ✅ Better logging
    
    // Optimistic update
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
        console.log("🔥 SENDING REQUEST to:", wishlistUrl); // ✅ Debug this line
        
        const response = await fetch(wishlistUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id: item_id }) // ✅ Ensure proper key
        });

        console.log("Response status:", response.status); // ✅ Check response
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Refresh ALL hearts
        await loadWishlistProducts();
        
    } catch (error) {
        console.error('❌ Wishlist toggle FAILED:', error);
        // Revert on error
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

