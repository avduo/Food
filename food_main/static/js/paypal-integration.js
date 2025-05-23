document.addEventListener("DOMContentLoaded", function() {
    const csrftoken = getCookie('csrftoken');
    console.log('csrftoken===>', csrftoken);

// Render the PayPal button into #paypal-button-container
        paypal.Buttons({

            // Call your server to set up the transaction
            createOrder: function(data, actions) {
                return actions.order.create({
                    purchase_units: [{
                        amount:{
                            value: window.paypalData.grand_total
                        }
                    }]
                })
            },

            // Call your server to finalize the transaction
            onApprove: function(data, actions) {
                return actions.order.capture().then(function(orderData){

                    // Successful capture! For demo purposes:
                    //console.log(orderData);
                    var transaction = orderData.purchase_units[0].payments.captures[0];
                    var transaction_id = transaction.id
                    var status = orderData.status
                    var payment_method = 'PayPal'
                    sendTransaction(transaction_id, status, payment_method);

                    //alert('Payment Successful');

                    // Replace the above to show a success message within this page, e.g.
                        const element = document.getElementById('paypal-button-container');
                        element.innerHTML = '';
                        element.innerHTML = '<h4 class="text-center text-warning"><i class="fa fa-spinner fa-spin"></i> Please wait your payment is being processed</h4>';

                });

            }

        }).render('#paypal-button-container');

});