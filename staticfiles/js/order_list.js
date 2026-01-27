document.addEventListener('DOMContentLoaded', function () {
  let deleteOrderId = null;

  function confirmDelete(orderId) {
    deleteOrderId = orderId;
    var myModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    myModal.show();
  }

  document.getElementById('confirmDeleteBtn').addEventListener('click', function () {
    if (!deleteOrderId) return;

    fetch(`/order/delete/${deleteOrderId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': 'csrfToken',
        'Content-Type': 'application/json'
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById(`order-card-${deleteOrderId}`).remove();
      } else {
        alert(data.error || "Something went wrong.");
      }
      bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
    })
    .catch(err => {
      alert("Error: " + err);
    });
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

  // Expose confirmDelete globally, so inline onclick calls in template can access it
  window.confirmDelete = confirmDelete;
});
