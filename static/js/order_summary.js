function getCurrentLocation() {
  const textarea = document.getElementById('delivery-address');
  textarea.placeholder = "Fetching location...";
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const { latitude, longitude } = position.coords;
        fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`)
          .then(response => response.json())
          .then(data => {
            const addr = data.address;
            let addressParts = [
              addr.house_number, addr.road, addr.suburb, addr.village,
              addr.town, addr.city, addr.state, addr.postcode, addr.country
            ].filter(Boolean);
            let address = addressParts.join('\n');
            if (addressParts.length < 4) address = data.display_name;
            textarea.value = address;
            textarea.placeholder = "Location fetched successfully.";
          })
          .catch(() => { textarea.placeholder = "Failed to retrieve address."; });
      },
      function () {
        textarea.placeholder = "Permission denied or location unavailable.";
      }
    );
  } else {
    textarea.placeholder = "Geolocation not supported.";
  }
}

function removeItem(itemId) {
  fetch(`/cart/remove/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
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
          'X-CSRFToken': '{{ csrf_token }}'
        }
      })
        .then(res => res.json())
        .then(data => {
          if (data.success && data.order_id) {
            window.location.href = `/payment/create/${data.order_id}/`;
          } else {
            alert("Order not placed: " + (data.error || "Unknown error"));
          }
        })
        .catch(() => {
          alert("Order request failed. Please try again.");
        });
    });
  }
});
