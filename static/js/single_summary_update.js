// update.js - Price updates and API calls
function updateOrder() {
  const quantity = parseInt(document.getElementById('quantity').value) || 1;
  const size = document.getElementById('size').value;
  const productItemId = document.getElementById('product_item_id').value;
  
  if (!size || !productItemId) return;
  
  fetch('/api/single-order/update/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      product_item_id: parseInt(productItemId),
      quantity: quantity,
      size: parseInt(size),
      color: document.getElementById('color')?.value ? parseInt(document.getElementById('color').value) : null
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success && data.summary) {
      window.showMessage('success', data.message);
      window.updateOrderSummary(data.summary);
    } else {
      window.showMessage('error', data.error);
    }
  })
  .catch(console.error);
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
