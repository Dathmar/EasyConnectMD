const paymentForm = new SqPaymentForm({
    // Initialize the payment form elements
    applicationId: "sandbox-sq0idb-tOPCaqqjNhHwoh3Vi_ihkg",
    autoBuild: false,
    // Initialize the credit card placeholders
    card: {
        elementId: 'sq-card',
    },
    // SqPaymentForm callback functions
    callbacks: {
        /*
        * callback function: cardNonceResponseReceived
        * Triggered when: SqPaymentForm completes a card nonce request
        */
        cardNonceResponseReceived: function (errors, nonce, cardData) {
        if (errors) {
            // Log errors from nonce generation to the browser developer console.
            console.error('Encountered errors:');
            errors.forEach(function (error) {
                console.error('  ' + error.message);
            });
            alert('Encountered errors, check browser developer console for more details');
            return;
        }

            let nonce_div = document.getElementById('id_nonce');
            nonce_div.value = nonce;
            document.forms[0].submit();


            return;
        }
    }
});
paymentForm.build();
 // onGetCardNonce is triggered when the "Pay $1.00" button is clicked
function onGetCardNonce(event) {
   // Don't submit the form until SqPaymentForm returns with a nonce
   event.preventDefault();
   // Request a nonce from the SqPaymentForm object
   paymentForm.requestCardNonce();

}