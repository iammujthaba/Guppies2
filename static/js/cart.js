var updateBtns = document.getElementsByClassName('update-cart');

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        var stock = parseInt(this.dataset.quntity);

        var quantityInput = document.getElementById('cart-quantity');
        var currentQuantity = 1; // Default to 1 if quantity input is not present

        if (quantityInput) {
            currentQuantity = parseInt(quantityInput.value);
            stock = parseInt(quantityInput.getAttribute('max'));
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
            location.reload();
        }
    });
}

function addCookieItem(productId, action, stock, currentQuantity = NaN) {
    console.log('User is not authenticated');
    console.log('productId:', productId, 'Action:', action, 'stock:', stock, 'currentQuantity:', currentQuantity);

    if (action == 'add') {
        if (currentQuantity > 1) {
            if (cart[productId] == undefined) {
                cart[productId] = {'quantity': currentQuantity};
            } else {
                if ((cart[productId]['quantity'] + currentQuantity) < stock) {
                    cart[productId]['quantity'] += currentQuantity;
                } else {
                    showWarningAlert('There is no more stock available. If you want more, please contact us.', () => {
                        // Code to execute if the user confirms the alert
                    });
                    return;
                }
            }
        } else {
            if (cart[productId] == undefined) {
                cart[productId] = {'quantity': 1};
            } else {
                if (cart[productId]['quantity'] < stock) {
                    cart[productId]['quantity'] += 1;
                } else {
                    showWarningAlert('There is no more stock available. If you want more, please contact us.', () => {
                        // Code to execute if the user confirms the alert
                    });
                    return;
                }
            }
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1;

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted');
            delete cart[productId];
        }
    }

    if (action == 'remove-all') {
        delete cart[productId];
    }

    console.log('CART:', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

    location.reload();
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
