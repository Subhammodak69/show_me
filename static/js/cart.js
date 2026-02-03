function removeCartItem(itemId) {
    if (!confirm("Are you sure you want to remove this item?")) return;
    const loader = document.querySelector('.loading');
    if (loader) {
        loader.style.display = 'flex';
    }
    fetch(`/cart/remove/${itemId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loader.style.display = 'none';
            window.location.reload();           
        } else {
            loader.style.display = 'none';
            alert(data.error || "Failed to remove item.");
        }
    })
    .catch(() => {
        loader.style.display = 'none';
        alert("Something went wrong.")
    });
}
