function $(x) { return document.getElementById(x)}

let coupon = $('id_code');
let cost_field = $('cost')
const patient_id_coupon = $('patient_id').innerHTML;

function applyCoupon(event) {
    event.preventDefault();
    let coupon_response = fetchCoupon();
}

function fetchCoupon(){
    let promise = fetch('/apply-coupon/', {
                method: 'POST',
                headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
                body: JSON.stringify({'coupon_code': coupon.value, 'patient_id': patient_id_coupon})
            })
            .then(
                response => response.json()
            )
            .then(data => {
                let coupon_status = $('coupon-status');
                coupon_status.classList.remove('d-none');
                coupon_status.innerHTML = data.status_msg;

                if(data.status_msg == "Success"){
                    if(data.patient_cost <= 0) {

                        cost_field.innerHTML = "<strike>$"+ data.default_cost / 100 +
                        "</strike> Free" ;
                        $('card-container').classList.add('d-none')
                    }
                    else {
                        cost_field.innerHTML = "<strike>$"+ data.default_cost / 100 +
                        "</strike> $" + data.patient_cost / 100;
                        $('card-container').classList.remove('d-none')
                    }
                }
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