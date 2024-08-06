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
        body: JSON.stringify({
            'productId': productId,
            'action': action,
            'currentQuantity': currentQuantity
        })
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
            updateCartTotal(data.cartTotal);
            updateTotalPriceDifference(data.totalPriceDifference);
            updateCartTotalWithShipping(data.cartTotal);
            if (data.itemQuantity <= 0) {
                removeCartItem(productId);
            } else {
                updateCartItemQuantity(productId, data.itemQuantity);
                updateCartItemTotal(productId, data.itemTotal);
            }
        }
    });
}

function updateCartTotal(total) {
    const cartTotalElements = document.querySelectorAll('.cart-total');
    cartTotalElements.forEach(el => {
        el.textContent = '₹ ' + parseFloat(total).toFixed(2);
    });
}

function updateTotalPriceDifference(difference) {
    const savingsElement = document.querySelector('.total-price-difference');
    if (savingsElement) {
        savingsElement.textContent = '₹ ' + parseFloat(difference).toFixed(2);
    }
}

function updateCartItemTotal(productId, total) {
    const totalElement = document.querySelector(`[data-product-id="${productId}"] .item-total`);
    if (totalElement) {
        totalElement.textContent = '₹ ' + parseFloat(total).toFixed(2);
    }
}

function updateCartTotalWithShipping(total) {
    const shippingCost = 60; // Assuming shipping cost is always 60
    const totalWithShipping = parseFloat(total) + shippingCost;
    const totalWithShippingElement = document.querySelector('.cart-total-with-shipping');
    if (totalWithShippingElement) {
        totalWithShippingElement.textContent = '₹ ' + totalWithShipping.toFixed(2);
    }
}

function updateCartDataForUnauthorizedUser() {
    let cartItems = getCartItemCount();
    updateCartCount(cartItems);
    updateCartTotals();
}

function getProductDetails(productId) {
    const productCard = document.querySelector(`.card[data-product-id="${productId}"]`);
    if (productCard) {
        return {
            id: productId,
            name: productCard.dataset.productName,
            new_price: parseFloat(productCard.dataset.productNewPrice),
            old_price: parseFloat(productCard.dataset.productOldPrice),
            stock: parseInt(productCard.dataset.productStock)
        };
    }
    return null;
}

function addCookieItem(productId, action, stock, currentQuantity = 1) {
    console.log('User is not authenticated');
    console.log('productId:', productId, 'Action:', action, 'stock:', stock, 'currentQuantity:', currentQuantity);

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 0};
        }
        if (cart[productId]['quantity'] + 1 <= stock) {
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
    updateCartDataForUnauthorizedUser();
    updateCartItemQuantity(productId, cart[productId] ? cart[productId]['quantity'] : 0);

    // Update cart totals
    updateCartTotals();
}

function updateCartTotals() {
    let cartTotal = 0;
    let totalPriceDifference = 0;

    for (let productId in cart) {
        const product = getProductDetails(productId);
        if (product) {
            const quantity = cart[productId]['quantity'];
            cartTotal += quantity * product.new_price;
            totalPriceDifference += quantity * (product.old_price - product.new_price);
        }
    }

    updateCartTotal(cartTotal);
    updateTotalPriceDifference(totalPriceDifference);
    updateCartTotalWithShipping(cartTotal);
}

// Make sure to call updateCartDataForUnauthorizedUser on page load for unauthorized users
document.addEventListener('DOMContentLoaded', function() {
    if (user === 'AnonymousUser' && (
        document.querySelector('.cart-count') ||
        document.querySelector('.cart-total') ||
        document.querySelector('.total-price-difference') ||
        document.querySelector('.cart-total-with-shipping')
    )) {
        updateCartDataForUnauthorizedUser();
    }
});


function updateCartCount(cartItems) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(el => {
        el.textContent = cartItems;
        el.dataset.cartItems = cartItems;
    });
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
    var quantityInput = document.querySelector(`[data-product-id="${productId}"] .cart-quantity`);
    if (quantityInput) {
        quantityInput.value = quantity;
    }

    // Update item total
    const product = getProductDetails(productId);
    if (product) {
        const itemTotal = quantity * product.new_price;
        updateCartItemTotal(productId, itemTotal);
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
