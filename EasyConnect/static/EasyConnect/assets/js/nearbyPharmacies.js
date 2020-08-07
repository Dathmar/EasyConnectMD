let latlng;
let map;
let bounds;
let infoWindow;
let currentInfoWindow;
let service;
let infoPane;

function initMap() {
    // Initialize variables
    geocoder = new google.maps.Geocoder();
    bounds = new google.maps.LatLngBounds();
    infoWindow = new google.maps.InfoWindow;
    currentInfoWindow = infoWindow;
    infoPane = document.getElementById('panel');

    // Try HTML5 geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            latlng = position.coords

            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: latlng.latitude, lng: latlng.longitude},
                zoom: 12
            });
            bounds.extend({lat: latlng.latitude, lng: latlng.longitude});

            infoWindow.setPosition({lat: latlng.latitude, lng: latlng.longitude});
            map.setCenter({lat: latlng.latitude, lng: latlng.longitude});

            getNearbyPlaces({lat: latlng.latitude, lng: latlng.longitude});
        }, () => {
            // Browser supports geolocation, but user has denied permission
            handleLocationError(true, infoWindow);
        });
    } else {
        // Browser doesn't support geolocation
        handleLocationError(false, infoWindow);
    }
}

// Handle a geolocation error
function handleLocationError(browserHasGeolocation, infoWindow) {
    var zipDiv = document.getElementById("zipcode");
    var zip = zipDiv.innerHTML

    geocoder.geocode( { 'address': zip}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            latlng = results[0].geometry.location;
            map = new google.maps.Map(document.getElementById('map'), {
                center: latlng,
                zoom: 12
            });
            getNearbyPlaces(latlng);
        } else {
            latlng = new google.maps.LatLng(29.4241, 98.4936);
            map = new google.maps.Map(document.getElementById('map'), {
                center: latlng,
                zoom: 12
            });
            getNearbyPlaces(latlng);
        };
    });
}

// Perform a Places Nearby Search Request
function getNearbyPlaces(latlng) {
    let request = {
    location: latlng,
    rankBy: google.maps.places.RankBy.DISTANCE,
    keyword: 'pharmacy'
    };

    service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, nearbyCallback);
}

// Handle the results (up to 20) of the Nearby Search
function nearbyCallback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
      createMarkers(results);
    }
}

// Set markers at the location of each place result
function createMarkers(places) {
    places.forEach(place => {
    let marker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: place.name
    });

    // Add click listener to each marker
    google.maps.event.addListener(marker, 'click', () => {
        let request = {
        placeId: place.place_id,
        fields: ['name', 'formatted_address', 'geometry', 'business_status', 'formatted_phone_number']
        };

        /* Only fetch the details of a place when the user clicks on a marker.
        * If we fetch the details for all place results as soon as we get
        * the search response, we will hit API rate limits. */
        service.getDetails(request, (placeResult, status) => {
            if (status == google.maps.places.PlacesServiceStatus.OK) {
                showDetails(placeResult, marker);
            }
        });
    });

    // Adjust the map bounds to include the location of this marker
    bounds.extend(place.geometry.location);
    });
    /* Once all the markers have been placed, adjust the bounds of the map to
    * show all the markers within the visible area. */
    map.fitBounds(bounds);
}

// Builds an InfoWindow to display details above the marker
function showDetails(placeResult, marker) {
    if (placeResult.business_status = "OPERATIONAL" ) {
        let placeInfowindow = new google.maps.InfoWindow();
        placeInfowindow.setContent('<div><strong>' + placeResult.name + '</strong><br>'
            + 'Address: ' + placeResult.formatted_address + '<br>'
            + 'Phone: ' + placeResult.formatted_phone_number + '</div>');
        placeInfowindow.open(marker.map, marker);
        currentInfoWindow.close();
        currentInfoWindow = placeInfowindow;
        showPanel(placeResult);
    }
}

// Displays place details in a sidebar
function showPanel(placeResult) {
    let name = document.getElementById('id_pharmacy_name');
    name.value = placeResult.name;

    let address = document.getElementById('id_pharmacy_address');
    address.value = placeResult.formatted_address;

    let phone = document.getElementById('id_pharmacy_phone');
    phone.value = placeResult.formatted_phone_number;

}

// Code for allowing a custom pharmacy:
function allowCustomPharmacy() {
    let checkBox = document.getElementById("custom_pharmacy");
    let name = document.getElementById('id_pharmacy_name');
    let address = document.getElementById('id_pharmacy_address');
    let phone = document.getElementById('id_pharmacy_phone');
    name.value = "";
    address.value = "";
    phone.value = "";

    if (checkBox.checked == true ) {
        // code for check box checked
        name.readOnly = false;
        address.readOnly = false;
        phone.readOnly = false;
    } else {
        // code for check box unchecked
        name.readOnly = true;
        address.readOnly = true;
        phone.readOnly = true;
    }
}

// Code for removing checks from diagnoses
function removeChecks(event) {
    let previous_diagnosis = document.getElementsByName('previous_diagnosis');

    if (event.id == 'id_previous_diagnosis_7') {
        for (var i = 0; i < previous_diagnosis.length - 1; i++) {
            previous_diagnosis[i].checked = false;
        }
    } else {
        previous_diagnosis[previous_diagnosis.length-1].checked = false;
    }

}