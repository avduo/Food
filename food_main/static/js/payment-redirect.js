function startStripeCheckout() {
    const orderNumber = window.paymentData.orderNumber;
    fetch('/orders/create-stripe-session/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            order_number: orderNumber,
        }),
    })
    .then(response => response.json())
    .then(data => {
        const stripe = Stripe(window.stripeData.publicKey);
        return stripe.redirectToCheckout({ sessionId: data.sessionId });
    })
    .catch(error => {
        console.error('Stripe Checkout error:', error);
    });
}


function sendTransaction(transaction_id, status, payment_method){
    const { url, order_number, order_complete } = window.paymentData;
    const csrftoken = getCookie('csrftoken');
    return $.ajax({
        url: url,
        type: 'POST',
        data: {
            'order_number': order_number,
            'transaction_id': transaction_id,
            'status': status,
            'payment_method': payment_method,
            'csrfmiddlewaretoken': csrftoken,
        },
        success: function(response){
            console.log('response===>', response);
        //     window.location.href = order_complete +'?order_no='+response.order_number+'&trans_id='+response.transaction_id;
        // }
        if(payment_method === 'Stripe') {
            // window.location.href = `${cart}?order_no=${response.order_number}&trans_id=${response.transaction_id}`;
        } else {
            // Original PayPal handling
            window.location.href = order_complete +'?order_no='+response.order_number+'&trans_id='+response.transaction_id;
        }

    },
    error: function(xhr, status, error) {
        console.error('Payment processing failed:', error);
        // Handle error case appropriately
        alert('Payment processing failed. Please try again or contact support.');
    }
    });
}