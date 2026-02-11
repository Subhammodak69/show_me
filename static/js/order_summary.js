

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


