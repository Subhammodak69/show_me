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
    let categoryStates = {}; 
    

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
        const wishlistOnClick = window.isAuthenticated 
        ? `toggle_wishlist_create_update(${item.id})`
        : `window.location.href='${window.loginUrl}'`;
        return `
        <div class="card p-2 text-center position-relative" style="min-width: 150px; max-width: 150px; height: 270px; flex: 0 0 150px;">
            <i class="bi bi-heart position-absolute top-0 end-0 m-2 wishlist-icon"
               data-product-id="${item.id}"
               style="cursor:pointer;width: 30px;height: 30px;display: flex;justify-content: center;align-items: center;background: aliceblue;border-radius: 50%;"
                onclick="${wishlistOnClick}"></i>

            <div style="margin: auto;width: 130px;height: 150px;" class="d-flex justify-content-center align-items-center">
                <img src="${item.photo_url}" class="card-img-top mx-auto rounded" style="width: 100%;height: 100%;object-fit: cover;">
            </div>

            <div class="card-body px-0">
                <div class="text-muted">⭐${item.rating.toFixed(1)} (${item.rating_count})</div>
                <div style="
                     display: -webkit-box;
                     -webkit-line-clamp: 3;
                     -webkit-box-orient: vertical;
                     overflow: hidden;
                     text-overflow: ellipsis;
                     max-height: 40px;
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
                    ? `<span style="text-decoration: line-through;font-size:14px; color: #dc3545;">₹${item.original_price}</span> <span style="font-size:14px;">₹${item.sale_price}</span>`
                    : `₹${item.original_price}`
                }
            </div>
        </div>`;
    }

    // 🔥 LOADING SKELETONS HTML
    function createLoadingSkeletons(count = 6) {
        let html = '';
        for(let i = 0; i < count; i++) {
            html += `<div class="loading-skeleton" style="flex: 0 0 150px; height: 270px; background: #f0f0f0; border-radius: 8px; animation: pulse 1.5s infinite;"></div>`;
        }
        return html;
    }

    /* =======================
     BEST DEALS - WITH LOADING
    ======================= */
    async function loadBestDeals() {
        const box = document.getElementById('best-deals-container');
        box.innerHTML = createLoadingSkeletons(7); 
        
        try {
            const res = await fetch('/api/best-deals/');
            const data = await res.json();
            box.innerHTML = '';
            data.best_deals.forEach(p => box.innerHTML += createProductCard(p));
            await loadWishlistProducts(); // Update hearts after loading
        } catch (error) {
            box.innerHTML = '<div class="text-center py-4 text-muted">Failed to load deals</div>';
        }
    }

    /* =======================
     PRODUCTS + SCROLL - FIXED LOADING
    ======================= */
    async function loadProductsByCategory(page) {
        const box = document.getElementById('products-container');
        const loadingEl = document.getElementById('loading');
        
        if (page === 1) {
            allProductsHtml = '';
            categoryStates = {};
            cleanupCategoryScrolls();
            box.innerHTML = '<div class="text-center py-5"><div class="spinner-border" style="width: 3rem; height: 3rem;"></div><p>Loading products...</p></div>';
            loadingEl.style.display = 'none';
        } else {
            loadingEl.style.display = 'block';
        }

        try {
            const res = await fetch(`/api/products-by-category/${page}/`);
            const data = await res.json();

            allProductsHtml = ''; 
            data.categories.forEach(cat => {
                if (!categoryStates[cat.category_id]) {
                    categoryStates[cat.category_id] = { page: 1, isLoading: false, scrollListener: null, section: null };
                }

                allProductsHtml += `
                <section class="mb-4 product-section" style="width: 100%;">
                    <h5 class="fw-bold ms-1 mb-3">${cat.category_name}</h5>
                    <div class="hot-items d-flex flex-row category-products-container loading-section product-section" 
                         data-category-id="${cat.category_id}" 
                         style="overflow-x: auto; gap: 14px; min-height: 320px; scrollbar-width: thin;">
                        ${createLoadingSkeletons(8)}
                    </div>
                </section>`;
            });

            box.innerHTML = allProductsHtml;
            currentPage = data.page;

            // 🔥 Replace skeletons with real data after short delay
            setTimeout(async () => {
                document.querySelectorAll('.category-products-container').forEach(container => {
                    const catId = container.dataset.categoryId;
                    const category = data.categories.find(c => c.category_id == parseInt(catId));
                    
                    if (category) {
                        container.innerHTML = '';
                        category.products.forEach(p => container.innerHTML += createProductCard(p));
                    }
                });
                await loadWishlistProducts(); // 🔥 Update ALL hearts
                setupCategoryScrolls();
                loadingEl.style.display = 'none';
            }, 800);

        } catch (error) {
            box.innerHTML = '<div class="text-center py-5 text-danger">Failed to load products</div>';
            loadingEl.style.display = 'none';
        }
    }

    /* =======================
     MAIN CONTAINER SCROLL (for more categories)
    ======================= */
    function setupInfiniteScroll() {
        const box = document.getElementById('products-container');
        box.addEventListener('scroll', () => {
            if (box.scrollTop + box.clientHeight >= box.scrollHeight - 50 && !isLoadingMore) {
                isLoadingMore = true;
                document.getElementById('loading').style.display = 'block';
                loadProductsByCategory(currentPage + 1).then(() => {
                    isLoadingMore = false;
                    document.getElementById('loading').style.display = 'none';
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
            
            if (!catId || state.scrollListener) return;

            container.scrollHeight;
            const listener = () => {
                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50 && 
                    !state.isLoading) {
                    
                    state.isLoading = true;
                    container.insertAdjacentHTML('beforeend', createLoadingSkeletons(4));
                    
                    loadMoreCategoryProducts(catId, state.page + 1).then(async () => {
                        state.isLoading = false;
                        container.querySelectorAll('.loading-skeleton').forEach(s => s.remove());
                        await loadWishlistProducts(); // 🔥 Update hearts after new products
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
                container.insertAdjacentHTML('beforeend', html);
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
     WISHLIST - FIXED FOR ALL SECTIONS
    ======================= */
    window.toggle_wishlist_create_update = function (item_id) {
        // 🔥 FIX: Target ALL icons for this product ID across entire page
        const allIcons = document.querySelectorAll(`.wishlist-icon[data-product-id="${item_id}"]`);
        if (allIcons.length === 0) return;

        // Toggle ALL icons immediately for instant feedback
        const isCurrentlyLiked = allIcons[0].classList.contains('bi-heart-fill');
        
        allIcons.forEach(icon => {
            if (isCurrentlyLiked) {
                // Remove from wishlist
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
            } else {
                // Add to wishlist
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                icon.style.color = '#ff4444';
            }
        });

        // Send request to server
        fetch(window.DJANGO_URLS.wishlist, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id })
        }).catch(error => {
            console.error('Wishlist toggle failed:', error);
            // Revert ALL icons on error
            allIcons.forEach(icon => {
                if (isCurrentlyLiked) {
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                    icon.style.color = '#ff4444';
                } else {
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                }
            });
        });
    };

    async function loadWishlistProducts() {
        try {
            const res = await fetch('/api/is-liked-status-check/');
            const data = await res.json();
            
            // 🔥 Clear all hearts first
            document.querySelectorAll('.wishlist-icon').forEach(icon => {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                icon.style.color = 'red';
            });
            
            // 🔥 Set filled hearts for liked products
            data.forEach(i => {
                document.querySelectorAll(`.wishlist-icon[data-product-id="${i.product_item_id}"]`)
                    .forEach(icon => {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        icon.style.color = '#ff4444';
                    });
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
