mapboxgl.accessToken = mapToken;

// create new map
let map = new mapboxgl.Map({
	container : 'map',
	style     : 'mapbox://styles/blakes24/cki20buzh0okk19pqhm3v6qa2'
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
	dropPin.setLngLat(e.lngLat).addTo(map);
});

// sends request to server to call API for dive sites near current coordinates
async function getSites(lng, lat) {
	$('#results').html('');

	let res = await axios.post(`/sites/search`, { mode: 'sites', lat: lat, lng: lng, dist: 100 });

	const sites = res.data.sites;
	if (sites.length > 0) {
		makeList(sites);
		setMarkers(sites);
	} else {
		$('#results').html('<p>No sites found within 100 miles of dropped pin.</p>');
	}
}

// sends request to API for dive sites matching search input
async function getSearchResults(str) {
	$('#results').html('');

	if (str.length < 2) {
		$('#results').html('<p>Search must contain at least 2 letters.</p>');
		return;
	}

	let res = await axios.post(`/sites/search`, { mode: 'search', str: str });

	const sites = res.data.matches;
	if (sites.length > 0) {
		makeList(sites);
		setMarkers(sites);
	} else {
		$('#results').html('<p>No sites found. Try another search.</p>');
	}
}

// adds dive site markers to map
function setMarkers(sites) {
	map.setCenter([ parseFloat(sites[0].lng), parseFloat(sites[0].lat) ]);
	for (let site of sites) {
		let myLatlng = new mapboxgl.LngLat(parseFloat(site.lng), parseFloat(site.lat));
		let marker = new mapboxgl.Marker({
			color : '#F78154',
			scale : 0.6
		})
			.setLngLat(myLatlng)
			.setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(`<a href="/sites/${site.id}">${site.name}</a>`))
			.addTo(map);

		currentMarkers.push(marker);
	}
}

// adds dive sites to list
function makeList(sites) {
	for (let site of sites) {
		const li = $(`<li><a href="/sites/${site.id}">${site.name}</a></li>`);
		$('#site-list').append(li);
	}
}

// removes current markers from the map
function clearMarkers() {
	for (let marker of currentMarkers) {
		marker.remove();
	}
}

// gets location of dropPin and returns nearby dive sites
$('#map-search').on('click', async function search() {
	// get coords of dropped pin
	const lng = dropPin.getLngLat().lng;
	const lat = dropPin.getLngLat().lat;
	// clear previous search results
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

	await getSearchResults(str);
});
