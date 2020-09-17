function $(x) { return document.getElementById(x)}

let connected = false;
const button = $('join_leave');
const container = $('chatSection');
const username = $('username').innerHTML;
const patient_id = $('patient_id').innerHTML;
let room;
const connect_string = 'Start Video Chat'
const disconnect_string = 'Leave Video'
let videoTrack = null;

function addLocalVideo() {
    Twilio.Video.createLocalVideoTrack().then(track => {
        videoTrack = track;
        let video = $('local').firstChild;
        video.appendChild(track.attach());
    });
}

function connectButtonHandler(event) {
    event.preventDefault();
    if (!connected) {
        button.disabled = true;
        button.innerHTML = 'Connecting...';
        connect().then(() => {
            button.innerHTML = disconnect_string;
            button.disabled = false;
        }).catch(() => {
            alert('Connection failed. Please make sure you have allowed access to your camera and microphone.');
            button.innerHTML = connect_string;
            button.disabled = false;
        });
    }
    else {
        disconnect();
        button.innerHTML = connect_string;
        connected = false;
    }
}

function connect() {
    let promise = new Promise((resolve, reject) => {
        // get a token from the back end
        console.log(patient_id)
        fetch('/video-token/', {
            method: 'POST',
            headers: {"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken")},
            body: JSON.stringify({'username': username, 'patient_id': patient_id})
        }).then(res => res.json()).then(data => {
            // join video call
            console.log('joining chat')
            return Twilio.Video.connect(data.token);
        }).then(_room => {
            console.log('setting room')
            room = _room;
            room.participants.forEach(participantConnected);
            room.on('participantConnected', participantConnected);
            room.on('participantDisconnected', participantDisconnected);
            connected = true;
            videoTrack.restart();
            resolve();
        }).catch(() => {
            // can add error catching for incorrect device, or no access.
            console.log('error connecting')
            reject();
        });
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

function disconnect() {
    room.disconnect();
    while (container.lastChild.id !== 'local')
        container.removeChild(container.lastChild);
    button.innerHTML = connect_string;

    // when disconnecting change to local only
    let video = $('local')
    video.classList.remove('participant-overlay')
    video.classList.add('participant')
    videoTrack.restart();
    connected = false;
}

function participantConnected(participant) {
    console.log('test participantConnected')
    let participantDiv = document.createElement('div');
    participantDiv.setAttribute('id', participant.sid);
    participantDiv.setAttribute('class', 'remote');

    let tracksDiv = document.createElement('div');
    participantDiv.appendChild(tracksDiv);

    container.appendChild(participantDiv);

    // update local video to show in upper left corner of remote video
    let local_overlay = document.getElementsByClassName('participant-overlay');
    if (local_overlay.length === 0) {
        let video = $('local');
        video.classList.remove('participant');
        video.classList.add('participant-overlay');
        videoTrack.restart();
    }

    participant.tracks.forEach(publication => {
        if (publication.isSubscribed)
            trackSubscribed(tracksDiv, publication.track);
    });
    participant.on('trackSubscribed', track => trackSubscribed(tracksDiv, track));
    participant.on('trackUnsubscribed', trackUnsubscribed);
}

function participantDisconnected(participant) {
    //change local back to full if this is the last participant
    document.getElementById(participant.sid).remove();
    let remote_div = document.getElementsByClassName('remote');
    let local_overlay = document.getElementsByClassName('participant-overlay');

    if (remote_div.length === 0 && local_overlay.length !== 0) {
        let video = $('local');
        video.classList.remove('participant-overlay');
        video.classList.add('participant');
        videoTrack.restart();
    }
}

function trackSubscribed(div, track) {
    div.appendChild(track.attach());
}

function trackUnsubscribed(track) {
    track.detach().forEach(element => element.remove());
}

addLocalVideo();
button.addEventListener('click', connectButtonHandler);
// Listen to the "beforeunload" event on window to leave the Room
// when the tab/browser is being closed.
window.addEventListener('beforeunload', () => room.disconnect());

// iOS Safari does not emit the "beforeunload" event on window.
// Use "pagehide" instead.
window.addEventListener('pagehide', () => room.disconnect());
