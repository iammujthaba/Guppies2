function displayPopupMessage(message) {
    alert(message); // You can use other methods to display a more styled popup
}

function incrementQuantity(stock) {
    const quantityInput = document.getElementById('cart-quantity');
    let currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity < stock) {
        quantityInput.value = currentQuantity + 1;
    } else {
        displayPopupMessage('There is no more stock available. If you want more, please contact us.');
    }
    updateAddToCartLink(currentQuantity + 1);
}

function decrementQuantity() {
    const quantityInput = document.getElementById('cart-quantity');
    let currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity > 1) {
        quantityInput.value = currentQuantity - 1;
        updateAddToCartLink(currentQuantity - 1);
    }
}

function updateAddToCartLink(quantity) {
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    
    // {#{% url 'cart_app:add_cart' product.id %}#}
    const baseUrl = "#";
    addToCartBtn.href = `${baseUrl}?quantity=${quantity}`;
}