

function removeItem(itemId) {
  fetch(`/cart/remove/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': 'csrfToken'
    }
  }).then(() => location.reload());
}


document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('order-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const form = this;
      const formData = new FormData(form);

      fetch("", {
        method: "POST",
        body: formData,
        headers: {
          'X-CSRFToken':'csrfToken'   // ✅ Fixed CSRF token
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.order_id) {
          showMessage('success', data.message || `Order #${data.order_id} created successfully!`, '/orders/');
        } else {
          showMessage('error', data.error || "Unknown error occurred");
        }
      })
      .catch(error => {
        console.error('Order error:', error);
        showMessage('error', "Network or server error. Please try again.");
      });
    });
  }
});


// =====================================================
// 1. VARIANT CHOOSING MODULE (Visual + Smart Updates)
// =====================================================
const VariantManager = {
    initAll() {
        document.querySelectorAll('.cart-item').forEach(cartItem => {
            const itemId = cartItem.dataset.id;
            this.initCartItem(itemId);
        });
    },
    
    initCartItem(itemId) {
        const cartItemDiv = document.querySelector(`[data-id="${itemId}"]`);
        const variantsScript = document.getElementById(`variants-${itemId}`);
        const sizeSelect = document.getElementById(`size-${itemId}`);
        const colorSelect = document.getElementById(`color-${itemId}`);
        const productImage = document.getElementById(`product-image-${itemId}`);
        const availabilitySpan = document.getElementById(`display-availability-${itemId}`);
        
        // Store variants globally for this item
        window[`variants_${itemId}`] = JSON.parse(variantsScript.textContent);
        const variants = window[`variants_${itemId}`];
        
        const initialSize = cartItemDiv.dataset.sizeDisplay;
        const initialColor = cartItemDiv.dataset.colorDisplay;
        
        productImage.dataset.originalSrc = productImage.src;
        
        // Initial setup
        this.populateColors(variants, colorSelect, initialColor);
        this.updateSizes(variants, colorSelect, sizeSelect, initialSize);
        this.setupInitialVariant(variants, sizeSelect, colorSelect, productImage, availabilitySpan, initialSize, initialColor);
        
        // Event listeners
        colorSelect.addEventListener('change', () => {
            this.updateSizes(variants, colorSelect, sizeSelect, initialSize);
            this.handleVariantChange(itemId);
        });
        
        sizeSelect.addEventListener('change', () => {
            this.handleVariantChange(itemId);
        });
    },
    
    setupInitialVariant(variants, sizeSelect, colorSelect, productImage, availabilitySpan, initialSize, initialColor) {
        const matchingVariant = variants.find(v => 
            v.display_size === initialSize && v.display_color === initialColor
        );
        
        ['border-success', 'border-warning', 'border-danger'].forEach(cls => {
            sizeSelect.classList.remove(cls);
            colorSelect.classList.remove(cls);
        });
        
        if (matchingVariant) {
            this.showVariantInfo(matchingVariant, productImage, availabilitySpan, sizeSelect, colorSelect);
        } else {
            this.showDefaultState(productImage, availabilitySpan, 'Select color & size');
        }
    },
    
    handleVariantChange(itemId) {
        const sizeSelect = document.getElementById(`size-${itemId}`);
        const colorSelect = document.getElementById(`color-${itemId}`);
        const productImage = document.getElementById(`product-image-${itemId}`);
        const availabilitySpan = document.getElementById(`display-availability-${itemId}`);
        const variants = window[`variants_${itemId}`];
        
        this.updateVariant(variants, sizeSelect, colorSelect, productImage, availabilitySpan, itemId);
        CartManager.triggerUpdate(itemId); // ✅ NOW UPDATES!
    },
    
    populateColors(variants, colorSelect, initialColor) {
        const uniqueColors = [...new Set(variants.map(v => v.display_color))].sort();
        colorSelect.innerHTML = '<option value="">Select Color</option>';
        
        uniqueColors.forEach(color => {
            const option = document.createElement('option');
            option.value = color;
            option.textContent = color;
            colorSelect.appendChild(option);
        });
        
        if (initialColor && uniqueColors.includes(initialColor)) {
            colorSelect.value = initialColor;
        }
    },
    
    updateSizes(variants, colorSelect, sizeSelect, initialSize) {
        const selectedColor = colorSelect.value;
        sizeSelect.innerHTML = '<option value="">Select Size</option>';
        
        if (selectedColor && variants.length > 0) {
            const availableSizes = [...new Set(
                variants
                    .filter(v => v.display_color === selectedColor && v.stock > 0)
                    .map(v => v.display_size)
            )].sort();
            
            availableSizes.forEach(size => {
                const option = document.createElement('option');
                option.value = size;
                option.textContent = size;
                sizeSelect.appendChild(option);
            });
            
            if (initialSize && availableSizes.includes(initialSize)) {
                sizeSelect.value = initialSize;
            }
        }
    },
    
    updateVariant(variants, sizeSelect, colorSelect, productImage, availabilitySpan, itemId) {
        const selectedSize = sizeSelect.value;
        const selectedColor = colorSelect.value;
        const matchingVariant = variants.find(v => 
            v.display_size === selectedSize && v.display_color === selectedColor
        );
        
        ['border-success', 'border-warning', 'border-danger'].forEach(cls => {
            sizeSelect.classList.remove(cls);
            colorSelect.classList.remove(cls);
        });
        
        if (matchingVariant) {
            this.showVariantInfo(matchingVariant, productImage, availabilitySpan, sizeSelect, colorSelect);
        } else if (selectedSize && selectedColor) {
            this.showErrorState(productImage, availabilitySpan, 'Combination not available');
        } else {
            this.showDefaultState(productImage, availabilitySpan, 'Select color & size');
        }
    },
    
    showVariantInfo(variant, productImage, availabilitySpan, sizeSelect, colorSelect) {
        if (variant.image) {
            productImage.src = variant.image;
            productImage.alt = `${variant.display_color} - ${variant.display_size}`;
        }
        
        if (variant.stock > 10) {
            availabilitySpan.textContent = 'In Stock';
            availabilitySpan.className = 'badge bg-success';
            sizeSelect.classList.add('border-success');
            colorSelect.classList.add('border-success');
        } else if (variant.stock > 0) {
            availabilitySpan.textContent = `Low Stock (${variant.stock})`;
            availabilitySpan.className = 'badge bg-warning';
            sizeSelect.classList.add('border-warning');
            colorSelect.classList.add('border-warning');
        }
    },
    
    showErrorState(productImage, availabilitySpan, message) {
        availabilitySpan.textContent = message;
        availabilitySpan.className = 'badge bg-danger';
        productImage.src = productImage.dataset.originalSrc;
    },
    
    showDefaultState(productImage, availabilitySpan, message) {
        availabilitySpan.textContent = message;
        availabilitySpan.className = 'badge bg-secondary';
        productImage.src = productImage.dataset.originalSrc;
    }
};

// =====================================================
// 2. CART UPDATE MODULE (PERFECTED)
// =====================================================
const CartManager = {
    updateTimeout: {},
    recentUpdates: new Set(),
    
    init() {
        document.querySelectorAll('.cart-item').forEach(cartItem => {
            const itemId = cartItem.dataset.id;
            const quantityInput = document.getElementById(`quantity-${itemId}`);
            
            if (quantityInput) {
                quantityInput.addEventListener('blur', () => this.debounceUpdate(itemId));
                quantityInput.addEventListener('change', () => this.debounceUpdate(itemId));
                // ✅ ALSO on quantity 'input' for real-time feel
                quantityInput.addEventListener('input', () => this.debounceUpdate(itemId));
            }
        });
    },
    
    // ✅ PUBLIC TRIGGER METHOD - Called by VariantManager
    triggerUpdate(itemId) {
        this.debounceUpdate(itemId);
    },
    
    debounceUpdate(itemId) {
        if (this.updateTimeout[itemId]) {
            clearTimeout(this.updateTimeout[itemId]);
        }
        
        this.updateTimeout[itemId] = setTimeout(() => {
            this.updateItem(itemId);
        }, 350); // ✅ Faster debounce for better UX
    },
    
    updateItem(itemId) {
        if (this.recentUpdates.has(itemId)) {
            console.log(`⏳ Item ${itemId} update already in progress`);
            return;
        }
        this.recentUpdates.add(itemId);

        const quantityInput = document.getElementById(`quantity-${itemId}`);
        const sizeSelect = document.getElementById(`size-${itemId}`);
        const colorSelect = document.getElementById(`color-${itemId}`);

        const quantity = parseInt(quantityInput.value) || 1;
        const sizeDisplay = sizeSelect.value;
        const colorDisplay = colorSelect.value;

        if (!this.validateUpdate(quantity, sizeDisplay, colorDisplay, itemId)) {
            this.recentUpdates.delete(itemId);
            return;
        }

        const variants = window[`variants_${itemId}`];
        const matchingVariant = variants.find(v => 
            v.display_size === sizeDisplay && v.display_color === colorDisplay
        );

        if (!matchingVariant || matchingVariant.stock === 0 || quantity > matchingVariant.stock) {
            showMessage('error', `Insufficient stock (${matchingVariant?.stock || 0})`);
            this.recentUpdates.delete(itemId);
            return;
        }

        this.showLoader(`Updating item ${itemId}...`);
        this.callUpdateAPI(itemId, quantity, matchingVariant);
    },
    
    validateUpdate(quantity, sizeDisplay, colorDisplay, itemId) {
        if (!quantity || quantity <= 0) {
            showMessage('error', 'Please enter valid quantity');
            return false;
        }
        if (!sizeDisplay || !colorDisplay) {
            showMessage('error', 'Please select size and color');
            return false;
        }
        return true;
    },
    
    callUpdateAPI(itemId, quantity, variant) {
        fetch('/api/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cart_item_id: parseInt(itemId),
                quantity: quantity,
                size: variant.size_value,
                color: variant.color_value
            })
        })
        .then(response => response.json())
        .then(data => {
            this.handleUpdateResponse(data, itemId);
        })
        .catch(error => {
            this.hideLoader();
            this.recentUpdates.delete(itemId);
            console.error('Cart update error:', error);
            showMessage('error', 'Network error');
        });
    },
    
    handleUpdateResponse(data, itemId) {
        this.hideLoader();
        this.recentUpdates.delete(itemId);
        
        if (data.success) {
            if (data.summary) {
                OrderSummary.update(data.summary);
            }
            showMessage('success', data.message || 'Cart updated!');
        } else {
            showMessage('error', data.error || 'Update failed');
        }
    },
    
    removeItem(itemId) {
        if (!confirm('Remove this item from cart?')) return;
        
        this.showLoader('Removing item...');
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ cart_item_id: parseInt(itemId) })
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoader();
            if (data.success) {
                showMessage('success', 'Item removed!');
                setTimeout(() => location.reload(), 1500);
            } else {
                showMessage('error', data.error || 'Remove failed');
            }
        })
        .catch(() => {
            this.hideLoader();
            showMessage('error', 'Network error');
        });
    },
    
    showLoader(message = 'Updating...') {
        let loader = document.querySelector('.loading');
        
        loader.style.display = 'block';
    },
    
    hideLoader() {
        const loader = document.querySelector('.loading');
        if (loader) loader.style.display = 'none';
    }
};

// =====================================================
// 3. ORDER SUMMARY MODULE
// =====================================================
const OrderSummary = {
    update(summary) {
        const formatPrice = (value) => {
            const num = parseFloat(value) || 0;
            return `₹${num.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        };
        
        const priceEl = document.getElementById('summary-price');
        const discountEl = document.getElementById('summary-discount');
        const totalEl = document.getElementById('summary-total');
        
        if (priceEl) priceEl.textContent = formatPrice(summary.original_price);
        if (discountEl) discountEl.textContent = `-${formatPrice(summary.discount)}`;
        if (totalEl) totalEl.textContent = formatPrice(summary.total);
    }
};

// =====================================================
// 4. DELIVERY FORM MODULE (Unchanged)
// =====================================================
const DeliveryForm = {
    orderBtn: null, paymentSelect: null, saveAddressBtn: null,
    orderForm: null, deliveryModal: null,
    
    init() {
        this.orderBtn = document.getElementById('orderBtn');
        this.paymentSelect = document.getElementById('paymentSelect');
        this.saveAddressBtn = document.getElementById('saveAddressBtn');
        this.orderForm = document.getElementById('order-form');
        this.deliveryModal = new bootstrap.Modal(document.getElementById('deliveryAddressModal'));
        
        this.bindEvents();
        this.initStateCityDropdowns();
    },
    
    bindEvents() {
        if (this.paymentSelect) {
            this.paymentSelect.addEventListener('change', () => {
                this.orderBtn.disabled = this.paymentSelect.value !== 'cod';
            });
        }
        
        if (this.orderBtn) {
            this.orderBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.deliveryModal.show();
            });
        }
        
        if (this.saveAddressBtn) {
            this.saveAddressBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleOrderSubmit();
            });
        }
    },
    
    handleOrderSubmit() {
        if (!this.validateAddress()) return;
        
        CartManager.showLoader('Processing order...');
        this.saveAddressBtn.disabled = true;
        
        const addressData = this.buildAddressString();
        this.addHiddenFields(addressData);
        this.deliveryModal.hide();
        
        setTimeout(() => {
            this.orderForm.submit();
        }, 300);
    },
    
    validateAddress() {
        const fields = ['stateSelect', 'citySelect', 'pinCode', 'locality', 'road', 'phoneNumber'];
        let isValid = true;
        
        fields.forEach(id => {
            const field = document.getElementById(id);
            if (field && !field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else if (field) {
                field.classList.remove('is-invalid');
            }
        });
        
        if (!isValid) showMessage('error', 'Please fill all address fields');
        return isValid;
    },
    
    buildAddressString() {
        return {
            address: [
                document.getElementById('stateSelect')?.value,
                document.getElementById('citySelect')?.value,
                document.getElementById('locality')?.value,
                document.getElementById('road')?.value,
                document.getElementById('pinCode')?.value
            ].filter(Boolean).join(', '),
            phone: document.getElementById('phoneNumber')?.value || ''
        };
    },
    
    addHiddenFields(data) {
        const form = this.orderForm;
        if (form) {
            form.insertAdjacentHTML('beforeend', 
                `<input type="hidden" name="address" value="${data.address}">
                 <input type="hidden" name="phone" value="${data.phone}">`
            );
        }
    },
    
    initStateCityDropdowns() {
        const states = ['West Bengal', 'Delhi', 'Maharashtra', 'Uttar Pradesh', 'Kerala'];
        const stateSelect = document.getElementById('stateSelect');
        
        if (stateSelect) {
            states.forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateSelect.appendChild(option);
            });
            
            stateSelect.addEventListener('change', () => {
                const citySelect = document.getElementById('citySelect');
                if (citySelect) {
                    citySelect.innerHTML = '<option value="">Select City</option>';
                    
                    const cities = {
                        'West Bengal': ['Kolkata', 'Siliguri', 'Durgapur', 'Asansol'],
                        'Delhi': ['New Delhi', 'Delhi'],
                        'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik'],
                        'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra'],
                        'Kerala': ['Kochi', 'Thiruvananthapuram', 'Kozhikode']
                    };
                    
                    if (cities[stateSelect.value]) {
                        cities[stateSelect.value].forEach(city => {
                            const option = document.createElement('option');
                            option.value = city;
                            option.textContent = city;
                            citySelect.appendChild(option);
                        });
                    }
                }
            });
        }
    }
};


// =====================================================
// 6. UTILITY FUNCTIONS
// =====================================================
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

// =====================================================
// 7. INITIALIZATION
// =====================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Cart JS Initialized');
    VariantManager.initAll();
    CartManager.init();
    DeliveryForm.init();
});
