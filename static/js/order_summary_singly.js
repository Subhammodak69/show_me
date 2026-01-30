function getCurrentLocation() {
  const textarea = document.getElementById('delivery-address');
  textarea.placeholder = "Fetching location...";
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const { latitude, longitude } = position.coords;
        fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`)
          .then(res => res.json())
          .then(data => {
            const addr = data.address;
            const address = [
              addr.house_number, addr.road, addr.suburb, addr.village,
              addr.town, addr.city, addr.state, addr.postcode, addr.country
            ].filter(Boolean).join('\n');
            textarea.value = address.length > 20 ? address : data.display_name;
            textarea.placeholder = "Location fetched.";
          })
          .catch(() => { textarea.placeholder = "Failed to fetch location."; });
      },
      () => { textarea.placeholder = "Permission denied or location unavailable."; }
    );
  } else {
    textarea.placeholder = "Geolocation not supported.";
  }
}

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
          'X-CSRFToken': 'csrfToken'
        },
        body: JSON.stringify(data)
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.order_id) {
          window.location.href = `/orders/`;
        } else {
          alert("Error: " + (data.error || "Unknown error"));
        }
      })
      .catch(() => {
        alert("Network or server error. Please try again.");
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
