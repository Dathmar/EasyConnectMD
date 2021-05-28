function $(x) { return document.getElementById(x)}
const patient_id = $('patient_id').innerHTML;
let paymentForm;
function fetchSquareAppId() {
    let sq_id = fetch('/square-app-id/').then(
            response => {
                return response.json()
            }
        )
    return sq_id;
};

async function setSquareAppID() {
    let app_id = await fetchSquareAppId();
    paymentForm = new SqPaymentForm(
        {
        // Initialize the payment form elements
        applicationId: app_id.square_app_id,
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
}

setSquareAppID();

 // onGetCardNonce is triggered when the "Pay $1.00" button is clicked
async function onGetCardNonce(event) {
    // Don't submit the form until SqPaymentForm returns with a nonce
    event.preventDefault();
    let cost_val = await fetchCost();

    if(parseInt(cost_val.patient_cost) > 0){
        // Request a nonce from the SqPaymentForm object
        paymentForm.requestCardNonce();
    } else {
        document.forms[0].submit();
    }

}

function fetchCost() {
    let cst = fetch('/patient-cost/', {
            method: 'POST',
            headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
            body: JSON.stringify({'patient_id': patient_id})
        }).then(response => {
        return response.json()
    })
    return cst
}

function getCookie(c_name) {
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }