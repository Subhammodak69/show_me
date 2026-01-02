function removeCartItem(itemId) {
    if (!confirm("Are you sure you want to remove this item?")) return;

    fetch(`/cart/remove/${itemId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemElement = document.getElementById(`cart-item-${itemId}`);
            if (itemElement) {
                itemElement.remove();
            }
        } else {
            alert(data.error || "Failed to remove item.");
        }
    })
    .catch(() => alert("Something went wrong."));
}
