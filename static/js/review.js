// review.js - Order summary, price display, user details
document.addEventListener('DOMContentLoaded', function() {
  // Update order summary display
  function updateOrderSummary(summary) {
    const formatPrice = (value) => (parseFloat(value) || 0).toFixed(2);
    document.getElementById('summary-price').textContent = formatPrice(summary.original_price);
    document.getElementById('summary-discount').textContent = `-${formatPrice(summary.discount)}`;
    document.getElementById('summary-total').textContent = formatPrice(summary.total);
  }



  // Expose globally for other modules
  window.updateOrderSummary = updateOrderSummary;
});
