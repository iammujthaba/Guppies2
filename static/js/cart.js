var updateBtns = document.getElementsByClassName('update-cart')
// give id for every button
for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)

		// checing button clicked user is authenticatec or not
		console.log('USER:', user)
		if (user == 'AnonymousUser'){
			// run this function to add or remove item into cart (if user is no't authenticated)
			addCookieItem(productId, action)
			
		}else{
			// run this function to add or remove item into cart (if user is authenticated)
			updateUserOrder(productId, action)
		}

	})
}

// run this function if user is authenticated (for add or remove item into cart)
function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'

		// sending data into backend
		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
                'X-CSRFToken':csrftoken,
			}, 
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    console.log('Data:', data)
            location.reload()
		});
}

// run this function if user is no't authenticated (to add or remove item into cart)
function addCookieItem(productId, action){
	console.log('User is not authenticated')

	if (action == 'add'){
		if (cart[productId] == undefined){
		cart[productId] = {'quantity':1}

		}else{
			cart[productId]['quantity'] += 1
		}
	}

	if (action == 'remove'){
		cart[productId]['quantity'] -= 1

		if (cart[productId]['quantity'] <= 0){
			console.log('Item should be deleted')
			delete cart[productId];
		}
	}
	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
	location.reload()
}