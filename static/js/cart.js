document.addEventListener('DOMContentLoaded', function() {
    var updateBtns = document.getElementsByClassName('update-cart');
    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function() {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            var stock = parseInt(this.dataset.quntity);
            var currentQuantity = 1;  // Always set to 1 for 'add' and 'remove' actions

            // Only get the actual quantity for 'remove-all' action
            if (action === 'remove-all') {
                var quantityInput = this.closest('.card-body') ? 
                    this.closest('.card-body').querySelector('.cart-quantity') : 
                    document.getElementById('cart-quantity');
                
                if (quantityInput) {
                    currentQuantity = parseInt(quantityInput.value) || 1;
                }
            }

            console.log('productId:', productId, 'Action:', action, 'stock:', stock, 'currentQuantity:', currentQuantity);
            console.log('USER:', user);

            if (user === 'AnonymousUser') {
                addCookieItem(productId, action, stock, currentQuantity);
            } else {
                updateUserOrder(productId, action, currentQuantity);
            }
        });
    }
});

function updateUserOrder(productId, action, currentQuantity = NaN) {
    console.log('User is authenticated, sending data...');
    var url = '/update_item/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action, 'currentQuantity': currentQuantity })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data:', data);
        if (data.added == false) {
            showWarningAlert(data.message, () => {
                // Code to execute if the user confirms the alert
            });
            return;
        } else {
            updateCartCount(data.cartItems);
            if (action === 'remove-all') {
                removeCartItem(productId);
            } else {
                updateCartItemQuantity(productId, data.cartItems);
            }
        }
    });
}

function addCookieItem(productId, action, stock, currentQuantity = 1) {
    console.log('User is not authenticated');
    console.log('productId:', productId, 'Action:', action, 'stock:', stock, 'currentQuantity:', currentQuantity);

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 0};
        }
        // Change this line
        if (cart[productId]['quantity'] + 1 <= stock) {  // Always add 1, not currentQuantity
            cart[productId]['quantity'] += 1;
        } else {
            showWarningAlert('There is no more stock available. If you want more, please contact us.', () => {
                // Code to execute if the user confirms the alert
            });
            return;
        }
    }

    if (action == 'remove') {
        if (cart[productId] && cart[productId]['quantity'] > 0) {
            cart[productId]['quantity'] -= 1;
            if (cart[productId]['quantity'] <= 0) {
                console.log('Item should be deleted');
                delete cart[productId];
                removeCartItem(productId);
            }
        }
    }

    if (action == 'remove-all') {
        delete cart[productId];
        removeCartItem(productId);
    }

    console.log('CART:', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
    updateCartCount(getCartItemCount());
    updateCartItemQuantity(productId, cart[productId] ? cart[productId]['quantity'] : 0);
}

function updateCartCount(cartItems) {
    document.querySelector('.cart-count').textContent = cartItems;
    document.querySelector('.cart-count').dataset.cartItems = cartItems;
}

function getCartItemCount() {
    var totalItems = 0;
    for (var key in cart) {
        if (cart.hasOwnProperty(key)) {
            totalItems += cart[key].quantity;
        }
    }
    return totalItems;
}

function removeCartItem(productId) {
    var cartItem = document.querySelector(`[data-product="${productId}"]`).closest('.card');
    if (cartItem) {
        cartItem.remove();
    }
}

function updateCartItemQuantity(productId, quantity) {
    var quantityInput = document.querySelector(`[data-product="${productId}"] .cart-quantity`);
    if (quantityInput) {
        quantityInput.value = quantity;
    }
}

function showWarningAlert(message, callback) {
    Swal.fire({
        icon: "warning",
        title: "Warning...",
        text: message,
    }).then((result) => {
        if (result.isConfirmed) {
            callback();
        }
    });
}
