function $(x) { return document.getElementById(x)}

const patient_id = $('patient_id').innerHTML;

async function initializeCard(payments) {
    const card = await payments.card();
    await card.attach('#card-container');
    return card;
}

document.addEventListener('DOMContentLoaded', async function () {
    if (!window.Square) {
        throw new Error('Square.js failed to load properly');
    }
    let fetch_response = await fetchSquareAppId();
    const payments = window.Square.payments(fetch_response.square_app_id, fetch_response.square_location_id);
    let card;
    try {
        card = await initializeCard(payments);
    } catch (e) {
        console.error('Initializing Card failed', e);
        return;
    }

    // Checkpoint 2.
    async function handlePaymentMethodSubmission(event, paymentMethod) {
        event.preventDefault();
        try {
            // disable the submit button as we await tokenization and make a
            // payment request.
            cardButton.disabled = true;
            const token = await tokenize(paymentMethod);
            await nce(token);
            console.log('token id')
            console.log(token)
            document.forms[0].submit();
        } catch (e) {
            cardButton.disabled = false;
            displayPaymentResults('FAILURE');
            console.error(e.message);
        }
    }

    const cardButton = document.getElementById(
        'card-button'
    );
    cardButton.addEventListener('click', async function (event) {
        let patient_cost = await get_patient_cost();
        console.log(patient_cost)
        if ( patient_cost <= 0 ) {
            event.preventDefault();
            document.forms[0].submit();
        } else {
            await handlePaymentMethodSubmission(event, card);
        }
    });
});

async function tokenize(paymentMethod) {
    const tokenResult = await paymentMethod.tokenize();
    if (tokenResult.status === 'OK') {
        return tokenResult.token;
    } else {
        let errorMessage = `Tokenization failed-status: ${tokenResult.status}`;
        if (tokenResult.errors) {
            errorMessage += ` and errors: ${JSON.stringify(
                tokenResult.errors
            )}`;
        }
        throw new Error(errorMessage);
    }
}

async function nce(nonce) {
    return await fetch('/order-nonce/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'nonce': nonce})
    }).catch(err => console.log(err))
}

function fetchSquareAppId() {
    let sq_id = fetch('/square-app-id/').then(
        response => {
            return response.json()
        })
    return sq_id;
};

function get_patient_cost() {
    let patient_cost = fetch('/patient-cost/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'patient_id': patient_id})
    }).then(
        response => {
            return response.json();
        }).then( data => {
            return data.patient_cost;
    })
    return patient_cost;
}
