// payment.js

document.addEventListener('DOMContentLoaded', function () {
  // Field toggling
  const methodField = document.getElementById('method');
  if (methodField) {
    methodField.addEventListener('change', function () {
      ['cardFields', 'upiFields', 'netbankingFields'].forEach(id => {
        const field = document.getElementById(id);
        if (field) field.style.display = 'none';
      });
      switch (this.value) {
        case '1': document.getElementById('cardFields').style.display = 'block'; break;
        case '2': document.getElementById('upiFields').style.display = 'block'; break;
        case '3': document.getElementById('netbankingFields').style.display = 'block'; break;
      }
    });
  }

  // Caution modal
  const openModalBtn = document.querySelector('.btn-warning');
  const modal = document.getElementById("modalbody");
  const noBtn = document.getElementById('noBtn');
  const yesBtn = document.getElementById('yesBtn');

  if (openModalBtn && modal) {
    openModalBtn.addEventListener('click', () => modal.style.display = "flex");
    if (noBtn) noBtn.onclick = () => modal.style.display = "none";
    if (yesBtn) yesBtn.onclick = () => window.location.href = '/';
  }

  // Form submission
  const form = document.getElementById('paymentForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      createPayment();
    });
  }

  async function createPayment() {
    const method = document.getElementById('method').value;
    if (!method) return alert('Please select a payment method.');

    const data = {
      method,
      amount: document.getElementById('amount').value,
      order_id: document.getElementById('order_id').value
    };

    if (method === '1') {
      const cardNumber = document.getElementById('cardNumber').value.trim();
      const expiry = document.getElementById('expiry').value;
      const cvv = document.getElementById('cvv').value.trim();
      if (!cardNumber || !expiry || !cvv) return alert('Please fill all card details.');
      Object.assign(data, { cardNumber, expiry, cvv });
    }

    if (method === '2') {
      const upiId = document.getElementById('upiId').value.trim();
      if (!upiId) return alert('Please enter your UPI ID.');
      data.upiId = upiId;
    }

    if (method === '3') {
      const bank = document.getElementById('bank').value;
      if (!bank) return alert('Please select your bank.');
      data.bank = bank;
    }

    try {
      const resp = await fetch(`/payment/create/${data.order_id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': 'csrfToken'
        },
        body: JSON.stringify(data)
      });
      const result = await resp.json();

      if (result.success) {
        document.getElementById('payStatus').textContent = 'Success';
        document.getElementById('payTime').textContent = new Date().toLocaleString();
        document.getElementById('payMethod').textContent = 'Cash On Delivery';
        document.getElementById('payAmount').textContent = data.amount;
        document.getElementById('successMessage').textContent = 'Your payment has been processed successfully!';

        document.querySelector('.loading').style.display = 'block';

        setTimeout(() => {
          document.querySelector('.loading').style.display = 'none';
          const sm = document.getElementById('successModal');
          sm.style.display = 'flex';
          document.getElementById('homeBtn').onclick = () => window.location.href = '/';
        }, 2000);
      } else {
        document.querySelector('.loading').style.display = 'none';
      }
    } catch (err) {
      alert('An error occurred: ' + err.message);
    }
  }

  function getCookie(name) {
    let value = null;
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) value = decodeURIComponent(c.slice(name.length + 1));
    });
    return value;
  }
});
