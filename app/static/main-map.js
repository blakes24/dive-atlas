mapboxgl.accessToken = mapToken;

// create new map
let map = new mapboxgl.Map({
	container : 'map',
	style     : 'mapbox://styles/blakes24/ckjoq7xhd1bgc19lljdhgtpod'
});

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());
map.setZoom(1);
map.setCenter([ -170, 20 ]);

const center = map.getCenter();
const currentMarkers = [];

// create marker to be placed by user to indicate search location
const dropPin = new mapboxgl.Marker({
	color : '#8FC0A9'
});

//place marker on point where map is double-clicked
map.on('dblclick', (e) => {
	dropPin.setLngLat(e.lngLat).addTo(map);
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
		}, 500);
		return false;
	});

// gets location of dropPin and returns nearby dive sites
$('#map-search').on('click', async function search() {
	document.getElementById('map-search').scrollIntoView({ behavior: 'smooth' });
	$('#results').html('<p>Searching...</p>');
	// check for pin
	if (dropPin.getLngLat() === undefined) {
		$('#site-list').html('');
		clearMarkers();
		$('#results').html('<p>Place a pin on the map to search the area.</p>');
		return;
	}
	// get coords of dropped pin
	const lng = dropPin.getLngLat().lng;
	const lat = dropPin.getLngLat().lat;

	//clear previous search results
	$('#site-list').html('');
	clearMarkers();

	await getSites(lng, lat);
});

// gets search form data snd returns matching dive sites
$('#search-form').on('submit', async function textSearch(e) {
	e.preventDefault();
	$('#results').html('<p>Searching...</p>');
	// clear previous search results
	$('#site-list').html('');
	clearMarkers();
	// get new search input
	let str = $('#search-text').val();

	// check if input is blank
	if (str.trim().length > 0) {
		await getSearchResults(str);
		document.getElementById('map-search').scrollIntoView({ behavior: 'smooth' });
	} else {
		$('#search-text').val('Enter a search term');
	}
});
