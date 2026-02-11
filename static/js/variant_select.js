// variant_select.js - PERFECTLY FIXED (Initial + All Changes)
let updateTimeout = null;

function getAvailableSizesForColor(variants, colorValue) {
  if (!colorValue) {
    return [...new Set(variants.map(v => v.size_value))];
  }
  const availableSizes = variants
    .filter(v => v.color_value == colorValue)
    .map(v => v.size_value);
  return [...new Set(availableSizes)];
}

function initSingleProductVariants() {
  const variantsScript = document.getElementById('variants-data');
  const sizeSelect = document.getElementById('size');
  const colorSelect = document.getElementById('color');
  const quantityInput = document.getElementById('quantity');
  const productImage = document.getElementById('product-image');
  const availabilitySpan = document.getElementById('display-availability');
  
  if (!variantsScript || !sizeSelect) return;
  
  let variants = [];
  
  // Parse variants JSON
  try {
    const jsonText = variantsScript.textContent.trim();
    if (jsonText && jsonText !== 'null' && jsonText !== '[]') {
      variants = JSON.parse(jsonText);
    }
  } catch (e) {
    console.error('JSON Parse Error:', e);
    availabilitySpan.textContent = 'Variant data unavailable';
    return;
  }

  if (variants.length === 0) {
    availabilitySpan.textContent = 'No variants available';
    return;
  }

  // 🔥 STORE ALL ORIGINAL SIZE OPTIONS ONCE (THE FIX!)
  const ALL_SIZE_OPTIONS = {};
  Array.from(sizeSelect.options).forEach(option => {
    if (option.value) {
      ALL_SIZE_OPTIONS[option.value] = {
        text: option.text,
        display: option.dataset.display || ''
      };
    }
  });

  // Store original image
  productImage.dataset.originalSrc = productImage.src;
  
  // Set initial values
  const initialSize = sizeSelect.dataset.initialSize || '';
  const initialColor = colorSelect?.dataset.initialColor || '';
  
  if (initialSize) sizeSelect.value = initialSize;
  if (colorSelect && initialColor) colorSelect.value = initialColor;

  function updateVariantInfo() {
    const selectedSize = sizeSelect.value;
    const selectedColor = colorSelect ? colorSelect.value : null;
    
    const matchingVariant = variants.find(v => 
      v.size_value == selectedSize && 
      (!selectedColor || v.color_value == selectedColor)
    );

    // Reset styling
    [sizeSelect, colorSelect].forEach(el => {
      if (el) el.classList.remove('border-success', 'border-warning', 'border-danger');
    });
    quantityInput.classList.remove('border-warning', 'border-danger');
    
    if (matchingVariant) {
      if (matchingVariant.image) {
        productImage.src = matchingVariant.image;
      }
      
      const stock = matchingVariant.stock;
      const currentQty = parseInt(quantityInput.value) || 1;
      quantityInput.max = stock;
      
      if (currentQty > stock) {
        quantityInput.value = stock;
        availabilitySpan.textContent = `Max ${stock} available`;
        availabilitySpan.className = 'badge bg-warning text-dark';
        [quantityInput, sizeSelect, colorSelect].forEach(el => {
          if (el) el.classList.add('border-warning');
        });
        window.showMessage?.('warning', `Quantity adjusted to ${stock} (max available)`);
      } else if (stock > 10) {
        availabilitySpan.textContent = `In Stock (${stock})`;
        availabilitySpan.className = 'badge bg-success';
        [sizeSelect, colorSelect].forEach(el => {
          if (el) el.classList.add('border-success');
        });
      } else if (stock > 0) {
        availabilitySpan.textContent = `Low Stock (${stock})`;
        availabilitySpan.className = 'badge bg-warning text-dark';
        [sizeSelect, colorSelect].forEach(el => {
          if (el) el.classList.add('border-warning');
        });
      } else {
        availabilitySpan.textContent = 'Out of Stock';
        availabilitySpan.className = 'badge bg-danger';
        [sizeSelect, colorSelect, quantityInput].forEach(el => {
          if (el) el.classList.add('border-danger');
        });
        quantityInput.value = 0;
        quantityInput.disabled = true;
      }
      debounceUpdateOrder();
    } else {
      availabilitySpan.textContent = 'Select valid combination';
      availabilitySpan.className = 'badge bg-secondary';
      if (!selectedSize) productImage.src = productImage.dataset.originalSrc;
      quantityInput.disabled = true;
      quantityInput.value = 1;
    }
  }

  // 🔥 PERFECTED FILTER FUNCTION - Uses ALL_SIZE_OPTIONS
  function filterSizesByColor(selectedColor) {
    const availableSizes = getAvailableSizesForColor(variants, selectedColor);
    
    // 🔥 CLEAR & REBUILD using ALL original options (NOT current filtered ones!)
    sizeSelect.innerHTML = '<option value="">Select Size</option>';
    
    availableSizes.forEach(sizeValue => {
      if (ALL_SIZE_OPTIONS[sizeValue]) {
        const optionData = ALL_SIZE_OPTIONS[sizeValue];
        const newOption = new Option(optionData.text, sizeValue, false, false);
        newOption.dataset.display = optionData.display;
        sizeSelect.appendChild(newOption);
      }
    });
    
    // Smart size restoration
    const currentSize = sizeSelect.value;
    if (availableSizes.includes(parseInt(currentSize))) {
      sizeSelect.value = currentSize;
    } else if (availableSizes.length > 0) {
      sizeSelect.value = availableSizes[0];
    } else {
      sizeSelect.value = '';
      availabilitySpan.textContent = 'No sizes available for this color';
      availabilitySpan.className = 'badge bg-secondary';
    }
    
    sizeSelect.dispatchEvent(new Event('change'));
  }

  // 🔥 SINGLE COLOR HANDLER - NO DUPLICATES
  if (colorSelect) {
    colorSelect.addEventListener('change', function() {
      const selectedColor = this.value;
      
      // Image change
      if (selectedColor) {
        const colorVariants = variants.filter(v => v.color_value == selectedColor);
        if (colorVariants.length > 0 && colorVariants[0].image) {
          productImage.src = colorVariants[0].image;
        }
      } else {
        productImage.src = productImage.dataset.originalSrc;
      }
      
      // Filter sizes
      filterSizesByColor(selectedColor);
      debounceUpdateOrder();
    });

    // 🔥 INITIAL FILTER - Perfect!
    if (colorSelect.value) {
      filterSizesByColor(colorSelect.value);
    }
  }

  // Quantity validation
  quantityInput.addEventListener('input', function() {
    const selectedSize = sizeSelect.value;
    const selectedColor = colorSelect ? colorSelect.value : null;
    const matchingVariant = variants.find(v => 
      v.size_value == selectedSize && (!selectedColor || v.color_value == selectedColor)
    );
    
    if (matchingVariant) {
      const stock = matchingVariant.stock;
      quantityInput.max = stock;
      if (parseInt(this.value) > stock || parseInt(this.value) < 1) {
        this.value = Math.max(1, Math.min(stock, parseInt(this.value) || 1));
        window.showMessage?.('warning', `Available: 1-${stock}`);
      }
    }
  });

  function debounceUpdateOrder() {
    if (updateTimeout) clearTimeout(updateTimeout);
    updateTimeout = setTimeout(() => {
      if (typeof window.updateOrder === 'function') {
        window.updateOrder();
      }
    }, 350);
  }

  // Event listeners - CLEAN (no duplicates)
  sizeSelect.addEventListener('change', updateVariantInfo);
  quantityInput.addEventListener('input', debounceUpdateOrder);
  quantityInput.addEventListener('change', debounceUpdateOrder);

  // Initial load
  updateVariantInfo();
}

// Auto-init
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSingleProductVariants);
} else {
  initSingleProductVariants();
}
