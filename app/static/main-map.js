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

//touch screen: place marker on point where map is touched
map.on('touchstart', (e) => {
	setTimeout(() => {
		dropPin.setLngLat(e.lngLat).addTo(map);
	}, 100);
});

// gets location of dropPin and returns nearby dive sites
$('#map-search').on('click', async function search() {
	// check for pin
	if (dropPin.getLngLat() === undefined) {
		$('#results').html('<p>Add a pin to map.</p>');
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
	// clear previous search results
	$('#site-list').html('');
	clearMarkers();
	// get new search input
	let str = $('#search-text').val();

	// check if input is blank
	if (str.trim().length > 0) {
		await getSearchResults(str);
	} else {
		$('#search-text').val('Enter a search term');
	}
});
