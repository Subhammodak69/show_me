// delivery_address.js - Address modal and order submission
document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const orderBtn = document.getElementById('orderBtn');
  const paymentSelect = document.getElementById('paymentSelect');
  const saveAddressBtn = document.getElementById('saveAddressBtn');
  const deliveryModal = new bootstrap.Modal(document.getElementById('deliveryAddressModal'));

  // Payment validation
  paymentSelect.addEventListener('change', function() {
    orderBtn.disabled = this.value !== 'cod';
  });

  // Open address modal
  orderBtn.addEventListener('click', function(e) {
    e.preventDefault();
    deliveryModal.show();
  });

  // Order placement with stock validation
  saveAddressBtn.addEventListener('click', function(e) {
    e.preventDefault();
    
    if (!validateAddressForm()) return;

    // Final stock check
    const quantity = parseInt(document.getElementById('quantity').value) || 1;
    const size = document.getElementById('size').value;
    const color = document.getElementById('color')?.value;
    const variantsScript = document.getElementById('variants-data');
    
    let variants = [];
    try {
      const jsonText = variantsScript.textContent.trim();
      if (jsonText && jsonText !== 'null' && jsonText !== '[]') {
        variants = JSON.parse(jsonText);
      }
    } catch(e) {
      console.error('Variant parse error:', e);
    }
    
    const matchingVariant = variants.find(v => 
      v.size_value == size && (!color || v.color_value == color)
    );
    
    if (matchingVariant && quantity > matchingVariant.stock) {
      window.showMessage('error', `Cannot order ${quantity}. Only ${matchingVariant.stock} available!`);
      return;
    }

    // Show spinner
    document.getElementById('saveSpinner').classList.remove('d-none');
    this.disabled = true;

    // Order data
    const orderData = {
      product_item_id: parseInt(document.getElementById('product_item_id').value),
      quantity: quantity,
      size: parseInt(size),
      color: color ? parseInt(color) : null,
      address: [
        document.getElementById('stateSelect').value,
        document.getElementById('citySelect').value,
        document.getElementById('locality').value,
        document.getElementById('road').value,
        document.getElementById('pinCode').value
      ].filter(Boolean).join(', '),
      phone: document.getElementById('phoneNumber').value
    };

    console.log('Order data:', orderData); // Debug

    // Submit order
    fetch('', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify(orderData)
    })
    .then(response => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.json();
      }
    })
    .then(data => {
      if (data && data.success) {
        window.showMessage('success', data.message || 'Order placed successfully!');
        setTimeout(() => {
          window.location.href = `/track_order/${data.order_id}/`;
        }, 1500);
      } else {
        window.showMessage('error', data?.error || 'Order failed');
        document.getElementById('saveSpinner').classList.add('d-none');
        saveAddressBtn.disabled = false;
      }
    })
    .catch(error => {
      console.error('Order error:', error);
      window.showMessage('error', 'Network error - please try again');
      document.getElementById('saveSpinner').classList.add('d-none');
      saveAddressBtn.disabled = false;
    });
  });

  initStateCityDropdowns();
});

function validateAddressForm() {
  const fields = ['stateSelect', 'citySelect', 'pinCode', 'locality', 'road', 'phoneNumber'];
  let isValid = true;
  
  fields.forEach(id => {
    const field = document.getElementById(id);
    if (!field.value.trim()) {
      field.classList.add('is-invalid');
      isValid = false;
    } else {
      field.classList.remove('is-invalid');
    }
  });
  
  if (!isValid) window.showMessage('error', 'Please fill all fields');
  return isValid;
}

function initStateCityDropdowns() {
  const states = ['West Bengal', 'Delhi', 'Maharashtra', 'Uttar Pradesh', 'Kerala'];
  const stateSelect = document.getElementById('stateSelect');
  
  // Populate states
  states.forEach(state => {
    const option = document.createElement('option');
    option.value = state; 
    option.textContent = state;
    stateSelect.appendChild(option);
  });

  // State → City logic
  stateSelect.addEventListener('change', function() {
    const citySelect = document.getElementById('citySelect');
    citySelect.innerHTML = '<option value="">Select City</option>';
    citySelect.disabled = false;
    
    const cities = {
      'West Bengal': ['Kolkata', 'Siliguri', 'Durgapur', 'Asansol'],
      'Delhi': ['New Delhi', 'Delhi'],
      'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik'],
      'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra'],
      'Kerala': ['Kochi', 'Thiruvananthapuram', 'Kozhikode']
    };
    
    if (cities[this.value]) {
      cities[this.value].forEach(city => {
        const option = document.createElement('option');
        option.value = city; 
        option.textContent = city;
        citySelect.appendChild(option);
      });
    }
  });
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
