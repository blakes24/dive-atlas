mapboxgl.accessToken = mapToken;

// create new map
let map = new mapboxgl.Map({
	container : 'detail-map',
	style     : 'mapbox://styles/blakes24/ckjoq7xhd1bgc19lljdhgtpod'
});

const lat = parseFloat($('.lat').text());
const lng = parseFloat($('.lng').text());

// Set zoom and center of map.
map.setZoom(5);
map.setCenter([ lng, lat ]);

// create marker to be placed by user to indicate search location
const siteMarker = new mapboxgl.Marker({
	color : '#F78154'
})
	.setLngLat([ lng, lat ])
	.addTo(map);
