
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('direct-order-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = {
        product_item_id: document.getElementById('product_id')?.value,
        quantity: document.getElementById('quantity').value,
        size: document.getElementById('size').value,
        color: document.getElementById('color')?.value,
        address: document.getElementById('delivery-address').value,
        phone: document.getElementById('phone').value
      };
      
      fetch("", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')  // ✅ Fixed
        },
        body: JSON.stringify(data)
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


// Get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
