function $(x) { return document.getElementById(x)}

let connected = false;
const button = $('join_leave');
const container = $('chat_container');
const count = $('count');
const username = $('username').innerHTML;
const token = $('token').innerHTML;
let room;
const connect_string = 'Start Video Chat'
const disconnect_string = 'Leave Video'


function addLocalVideo() {
    Twilio.Video.createLocalVideoTrack().then(track => {
        let video = document.getElementById('local').firstChild;
        video.appendChild(track.attach());
    });
};

function connectButtonHandler(event) {
    event.preventDefault();
    if (!connected) {
        button.disabled = true;
        button.innerHTML = 'Connecting...';
        connect(username).then(() => {
            button.innerHTML = disconnect_string;
            button.disabled = false;
        }).catch(() => {
            alert('Connection failed. Please contact info@easyconnectmd.net');
            button.innerHTML = connect_string;
            button.disabled = false;
        });
    }
    else {
        disconnect();
        button.innerHTML = connect_string;
        connected = false;
    }
};

function connect(username) {

    let twilio_promise = new Promise((resolve, reject) => {
        twilio_video_connect(token).then(_room => {
            room = _room;
            room.participants.forEach(participantConnected);
            room.on('participantConnected', participantConnected);
            room.on('participantDisconnected', participantDisconnected);
            connected = true;
            updateParticipantCount();
            resolve();
        }).catch(() => {
            reject();
        });
    });

    return twilio_promise;
};

function room_setup(_room) {

};

function twilio_video_connect(token) {
    let connection;
    try {
        connection =  Twilio.Video.connect(token)
    } catch (error) {
        console.error('error in twilio connection')
    }
    console.log(connection)

    return connection
};

function disconnect() {
    console.log('disconnect');
    room.disconnect();
    while (container.lastChild.id != 'local')
        container.removeChild(container.lastChild);
    button.innerHTML = connect_string;
    connected = false;
    updateParticipantCount();
};

function updateParticipantCount() {
    console.log(connected)
    if (!connected)
        count.innerHTML = 'Disconnected.';
    else
        count.innerHTML = (room.participants.size + 1) + ' participants online.';
};

function participantConnected(participant) {
    let participantDiv = document.createElement('div');
    participantDiv.setAttribute('id', participant.sid);
    participantDiv.setAttribute('class', 'participant');

    let tracksDiv = document.createElement('div');
    participantDiv.appendChild(tracksDiv);

    let labelDiv = document.createElement('div');
    labelDiv.innerHTML = participant.identity;
    participantDiv.appendChild(labelDiv);

    container.appendChild(participantDiv);

    participant.tracks.forEach(publication => {
        if (publication.isSubscribed)
            trackSubscribed(tracksDiv, publication.track);
    });
    participant.on('trackSubscribed', track => trackSubscribed(tracksDiv, track));
    participant.on('trackUnsubscribed', trackUnsubscribed);

    updateParticipantCount();
};

function participantDisconnected(participant) {
    document.getElementById(participant.sid).remove();
    updateParticipantCount();
};

function trackSubscribed(div, track) {
    div.appendChild(track.attach());
};

function trackUnsubscribed(track) {
    track.detach().forEach(element => element.remove());
};

addLocalVideo();
button.addEventListener('click', connectButtonHandler);
