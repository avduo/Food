// static/js/stripe-integration.js (original version)

document.addEventListener("DOMContentLoaded", function() {
    const stripe = Stripe(window.stripeData.publicKey, {
        locale: 'en' // Force English to prevent './en' error
    });
    const stripeButton = document.getElementById('stripe-payment-button');

    stripeButton.addEventListener('click', async function() {
        stripeButton.disabled = true;
        const originalText = stripeButton.innerHTML;
        stripeButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing...';

        try {
            const response = await fetch(window.stripeData.createSessionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.stripeData.csrfToken
                },
                body: JSON.stringify({
                    order_number: window.paymentData.order_number
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || 'Payment failed');
            }

            const { sessionId, transaction_id } = await response.json();

            // Store transaction_id for webhook handling
            window.stripeTransactionId = transaction_id;

            // Redirect to Stripe
            const { error } = await stripe.redirectToCheckout({
                sessionId: sessionId
            });
            var status = orderData.status
            var payment_method = 'Stripe'
            sendTransaction(transaction_id, status, payment_method);

            if (error) throw error;

        } catch (error) {
            console.error('Stripe Error:', error);
            stripeButton.disabled = false;
            stripeButton.innerHTML = originalText;
            alert('Payment failed: ' + error.message);
        }
    });
});