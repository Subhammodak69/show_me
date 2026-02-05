document.addEventListener('DOMContentLoaded', () => {

    /* =======================
       CAROUSEL
    ======================= */
    const slides = document.querySelectorAll('.carousel-item');
    let currentSlide = 0;

    function showSlide(idx) {
        slides.forEach((s, i) => s.classList.toggle('active', i === idx));
    }

    if (slides.length) {
        setInterval(() => {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }, 3000);
    }

    /* =======================
       GLOBAL STATE
    ======================= */
    let currentPage = 1;
    let isLoadingMore = false;
    let allProductsHtml = '';

    /* =======================
       HELPERS
    ======================= */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                }
            });
        }
        return cookieValue;
    }

    function createProductCard(item) {
        const hasDiscount = item.original_price !== item.sale_price;
        return `
        <div class="card p-2 text-center position-relative" style="min-width:170px;max-width:180px;height:300px;">
            <i class="bi bi-heart position-absolute top-0 end-0 m-2 wishlist-icon"
               data-product-id="${item.product_id}"
               style="cursor:pointer"
               onclick="toggle_wishlist_create_update(${item.product_id})"></i>

            <div style="height:150px" class="d-flex justify-content-center align-items-center">
                <img src="${item.photo_url}" style="width:100px;height:130px;object-fit:contain">
            </div>

            <div class="card-body px-0">
                <div class="text-muted">⭐${item.rating.toFixed(1)} (${item.rating_count})</div>
                <div style="cursor:pointer;color:blue"
                     onclick="location.href='${window.DJANGO_URLS.product_details}${item.id}/'">
                     ${item.title}
                </div>
                ${
                    hasDiscount
                    ? `<del>₹${item.original_price}</del> ₹${item.sale_price}`
                    : `₹${item.original_price}`
                }
            </div>
        </div>`;
    }

    /* =======================
       BEST DEALS
    ======================= */
    async function loadBestDeals() {
        const res = await fetch('/api/best-deals/');
        const data = await res.json();
        const box = document.getElementById('best-deals-container');
        box.innerHTML = '';
        data.best_deals.forEach(p => box.innerHTML += createProductCard(p));
    }

    /* =======================
       PRODUCTS + SCROLL
    ======================= */
    async function loadProductsByCategory(page) {
        const res = await fetch(`/api/products-by-category/${page}/`);
        const data = await res.json();
        const box = document.getElementById('products-container');

        if (page === 1) {
            allProductsHtml = '';
            box.innerHTML = '';
        }

        data.categories.forEach(cat => {
            allProductsHtml += `<h5>${cat.category_name}</h5><section class="d-flex gap-3">`;
            cat.products.forEach(p => allProductsHtml += createProductCard(p));
            allProductsHtml += '</section>';
        });

        box.innerHTML = allProductsHtml;
        currentPage = data.page;
    }

    function setupInfiniteScroll() {
        const box = document.getElementById('products-container');
        box.addEventListener('scroll', () => {
            if (box.scrollTop + box.clientHeight >= box.scrollHeight - 50 && !isLoadingMore) {
                isLoadingMore = true;
                loadProductsByCategory(currentPage + 1).then(() => isLoadingMore = false);
            }
        });
    }

    /* =======================
       WISHLIST (GLOBAL)
    ======================= */
    window.toggle_wishlist_create_update = function (item_id) {
        fetch(window.DJANGO_URLS.wishlist, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id })
        }).then(() => location.reload());
    };

    async function loadWishlistProducts() {
        const res = await fetch('/api/is-liked-status-check/');
        const data = await res.json();
        data.forEach(i => {
            document.querySelectorAll(
                `.wishlist-icon[data-product-id="${i.product_item_id}"]`
            ).forEach(icon => icon.classList.replace('bi-heart', 'bi-heart-fill'));
        });
    }

    /* =======================
       INIT (ONLY HERE!)
    ======================= */
    setupInfiniteScroll();
    loadBestDeals();
    loadProductsByCategory(1);
    loadWishlistProducts();

});
