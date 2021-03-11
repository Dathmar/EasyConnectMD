function $(x) { return document.getElementById(x)}

let coupon = $('id_code');
let cost_field = $('cost')

function applyCoupon(event) {
    event.preventDefault();
    let coupon_response = fetchCoupon();
}

function fetchCoupon(){
    let promise = new Promise((resolve, reject) => {
        fetch('/apply-coupon/', {
                method: 'POST',
                headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
                body: JSON.stringify({'coupon_code': coupon.value, 'patient_id': patient_id})
            })
            .then(
                response => response.json()
            )
            .then(data => {
                if(data.status_msg == "Success"){
                    if(data.patient_cost <= 0) {
                        cost_field.innerHTML = "<strike>$"+ data.default_cost / 100 +
                        "</strike> Free" ;
                        $('card-container').classList.add('hidden')
                    }
                    else {
                        cost_field.innerHTML = "<strike>$"+ data.default_cost / 100 +
                        "</strike> $" + data.patient_cost / 100;
                        $('card-container').classList.remove('hidden')
                    }


                }

            })
            .catch(() => {
                // can add error catching
                reject();
        })
    });

    return promise;
}

function getCookie(c_name)
{
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