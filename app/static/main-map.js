mapboxgl.accessToken = mapToken;

// create new map
let map = new mapboxgl.Map({
	container       : 'map',
	style           : 'mapbox://styles/blakes24/ckjoq7xhd1bgc19lljdhgtpod',
	doubleClickZoom : false
});

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
map.setZoom(1);
map.setCenter([ -170, 20 ]);

const center = map.getCenter();
const currentMarkers = [];

// create marker to be placed by user to indicate search location
const dropPin = new mapboxgl.Marker({
	color : '#8FC0A9'
});

let pinOnMap = false;

//place marker on point where map is double-clicked and clear search field
map.on('dblclick', (e) => {
	dropPin.setLngLat(e.lngLat).addTo(map);
	$('#search-text').val('');
	pinOnMap = true;
});

$('#search-text').on('keyup', () => {
	dropPin.remove();
	pinOnMap = false;
});

//touch screen: place marker on point where map is touched and held
let pressTimer;

map
	.on('touchend', (e) => {
		clearTimeout(pressTimer);
		// Clear timeout
		return false;
	})
	.on('touchstart', (e) => {
		// Set timeout
		pressTimer = window.setTimeout(function() {
			dropPin.setLngLat(e.lngLat).addTo(map);
			$('#search-text').val('');
			pinOnMap = true;
		}, 500);
		return false;
	});

$('#show-list').on('click', () => {
	if ($('#show-list').text() === 'Hide List') {
		$('#show-list').text('Show List');
	} else {
		$('#show-list').text('Hide List');
	}
});

// use pin location or search form data to find matching dive sites
$('#search-form').on('submit', async function textSearch(e) {
	e.preventDefault();
	//clear previous search results
	clearMarkers();
	$('#show-list').text('Searching...');

	// check for pin
	if (pinOnMap === true) {
		// get coords of dropped pin
		const lng = dropPin.getLngLat().lng;
		const lat = dropPin.getLngLat().lat;
		// add search results
		await getSites(lng, lat);
	} else {
		// get search input
		let str = $('#search-text').val();
		// check if input is blank
		if (str.trim().length > 0) {
			// populate search results
			await getSearchResults(str);
		} else {
			$('#show-list').text('Enter a search term or add a pin');
			$('#results').html('<p>Enter a search term or add a pin to the map</p>');
		}
	}
});
