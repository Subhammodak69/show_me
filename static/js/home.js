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
    let categoryStates = {}; // { categoryId: { page: 1, isLoading: false, scrollListener: null, section: null } }

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
                <div style="
                   display: -webkit-box;
                   -webkit-line-clamp: 3;
                   -webkit-box-orient: vertical;
                   overflow: hidden;
                   text-overflow: ellipsis;
                   max-height: 60px;
                   font-size:15px; 
                   color: blue; 
                   cursor:pointer;
                   line-height: 1.3em;
                 "
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
     PRODUCTS + SCROLL - INITIAL CATEGORIES LOAD
    ======================= */
    async function loadProductsByCategory(page) {
        const res = await fetch(`/api/products-by-category/${page}/`);
        const data = await res.json();
        const box = document.getElementById('products-container');

        if (page === 1) {
            allProductsHtml = '';
            box.innerHTML = '';
            categoryStates = {}; // Reset all category states
            cleanupCategoryScrolls(); // Cleanup previous listeners
        }

        data.categories.forEach(cat => {
            // Initialize category state
            if (!categoryStates[cat.category_id]) {
                categoryStates[cat.category_id] = { page: 1, isLoading: false, scrollListener: null, section: null };
            }

            // 🔥 EXACT BEST DEALS STRUCTURE
            allProductsHtml += `
            <section class="mb-4" style="width: 100%;">
                <h5 class="fw-bold ms-1 mb-3">${cat.category_name}</h5>
                <div class="hot-items d-flex flex-row category-products-container loading-section" 
                    data-category-id="${cat.category_id}" 
                    style="overflow-x: auto; gap: 14px; min-height: 320px; scrollbar-width: thin;">
            `;
            
            cat.products.forEach(p => allProductsHtml += createProductCard(p));
            allProductsHtml += `</div></section>`;
        });

        box.innerHTML = allProductsHtml;
        currentPage = data.page;
        
        // Setup per-category scroll listeners after DOM update
        setupCategoryScrolls();
    }



    /* =======================
     MAIN CONTAINER SCROLL (for more categories)
    ======================= */
    function setupInfiniteScroll() {
        const box = document.getElementById('products-container');
        box.addEventListener('scroll', () => {
            if (box.scrollTop + box.clientHeight >= box.scrollHeight - 50 && !isLoadingMore) {
                isLoadingMore = true;
                loadProductsByCategory(currentPage + 1).then(() => {
                    isLoadingMore = false;
                });
            }
        });
    }

    /* =======================
     PER-CATEGORY INFINITE SCROLL
    ======================= */
    function setupCategoryScrolls() {
        document.querySelectorAll('.category-products-container').forEach(container => {
            const catId = container.dataset.categoryId;
            const state = categoryStates[catId];
            
            if (!catId || state.scrollListener) return; // Already setup

            // Force reflow to get accurate scrollHeight
            container.scrollHeight;

            const listener = () => {
                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50 && 
                    !state.isLoading) {
                    
                    state.isLoading = true;
                    loadMoreCategoryProducts(catId, state.page + 1).then(() => {
                        state.isLoading = false;
                    });
                }
            };

            container.addEventListener('scroll', listener);
            state.scrollListener = listener;
            state.section = container;
        });
    }

    /* =======================
     LOAD MORE PRODUCTS FOR SPECIFIC CATEGORY
    ======================= */
    async function loadMoreCategoryProducts(categoryId, page) {
        try {
            const url = `/category/${categoryId}/ajax/?page=${page}`;
            const res = await fetch(url);
            const html = await res.text();
            
            if (html.trim()) {
                const state = categoryStates[categoryId];
                const container = state.section;
                
                // Append new products to existing horizontal container
                container.insertAdjacentHTML('beforeend', html);
                
                // Update wishlist status for new products
                await loadWishlistProducts();
                
                state.page = page;
            }
        } catch (error) {
            console.error('Failed to load category products:', error);
        }
    }


    /* =======================
     CLEANUP CATEGORY SCROLL LISTENERS
    ======================= */
    function cleanupCategoryScrolls() {
        Object.values(categoryStates).forEach(state => {
            if (state.scrollListener && state.section) {
                state.section.removeEventListener('scroll', state.scrollListener);
                state.scrollListener = null;
                state.section = null;
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
        try {
            const res = await fetch('/api/is-liked-status-check/');
            const data = await res.json();
            data.forEach(i => {
                document.querySelectorAll(
                    `.wishlist-icon[data-product-id="${i.product_item_id}"]`
                ).forEach(icon => icon.classList.replace('bi-heart', 'bi-heart-fill'));
            });
        } catch (error) {
            console.error('Failed to load wishlist status:', error);
        }
    }

    /* =======================
     INIT (ONLY HERE!)
    ======================= */
    setupInfiniteScroll();
    loadBestDeals();
    loadProductsByCategory(1);
    loadWishlistProducts();

});
