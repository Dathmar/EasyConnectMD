function $(x) { return document.getElementById(x)}

let is_eighteen;
const age_section = $("underage");
const submit_button = $("submit");
const age_check = $("age");

function checkAge(dob){
    let promise = fetch('/age-verification/', {
        method: 'POST',
        headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({'dob': dob})
    }).then(
        response => response.json()
    ).then(data => {
        is_eighteen = data['is_eighteen']
        if (is_eighteen === false) {
            age_section.classList.remove("d-none");
            if (age_check.checked == false) {
                submit_button.disabled = true;
            }
        } else {
            age_section.classList.add("d-none");
            submit_button.disabled = false;
        }
    });

    return promise;
}

function enableButton() {
    if (age_check.checked){
        submit_button.disabled = false;
    } else {
        submit_button.disabled = true;
    }
}

function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1)
        {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }