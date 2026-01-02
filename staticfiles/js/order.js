function saveAddress() {
  const address = document.getElementById("address-textarea").value.trim();
  const inputField = document.getElementById("addressInput");

  if (address.length === 0) {
    alert("Please enter a valid address.");
    return;
  }

  inputField.value = address;
  inputField.focus();

  const modalEl = document.getElementById('addressModal');
  const modal = bootstrap.Modal.getInstance(modalEl);
  modal.hide();

  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }, 300);
}

function getLiveLocation() {
  const status = document.getElementById('locationStatus');
  status.textContent = '⏳ Getting your current location...';

  if (!navigator.geolocation) {
    alert("❌ Geolocation not supported.");
    return;
  }

  navigator.geolocation.getCurrentPosition(success, geoError, {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0
  });
}

function success(position) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;
  const status = document.getElementById('locationStatus');

  const apiKey = '1691222b1b6a469f8390a7b90e4225e8';
  const url = `https://api.opencagedata.com/geocode/v1/json?q=${lat}+${lon}&key=${apiKey}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data && data.results && data.results.length > 0) {
        const address = data.results[0].formatted;
        document.getElementById('addressInput').value = address;
        status.textContent = '✅ Address added successfully.';
      } else {
        throw new Error("No address found");
      }
    })
    .catch(error => {
      console.error('Geocoding error:', error);
      alert("❌ Error: Unable to convert location to address.");
      status.textContent = '';
    });
}

function geoError(error) {
  console.error("Geolocation error:", error);
  alert("❌ Location access failed.");
  document.getElementById('locationStatus').textContent = '';
}
