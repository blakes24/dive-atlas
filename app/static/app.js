// sends request to server to call API for dive sites near current coordinates
async function getSites(lng, lat) {
	let res = await axios.post(`/sites/search`, { mode: 'sites', lat: lat, lng: lng, dist: 100 });
	const sites = res.data.sites;

	if (sites.length > 0) {
		$('#results').html('');
		makeList(sites);
		setMarkers(sites);
		map.setZoom(6);

		if ($('#list-collapse').hasClass('show')) {
			$('#show-list').text('Hide List');
		} else {
			$('#show-list').text('Show List');
		}
	} else {
		$('#show-list').text('No sites found near pin');
		$('#results').html('<p>No sites found within 100 miles of dropped pin.</p>');
	}
}

// sends request to API for dive sites matching search input
async function getSearchResults(str) {
	if (str.length < 2) {
		$('#results').html('<p>Search must contain at least 2 letters.</p>');
		return;
	}

	let res = await axios.post(`/sites/search`, { mode: 'search', str: str });
	const sites = res.data.matches;

	if (sites.length > 0) {
		$('#results').html('');
		makeList(sites);
		setMarkers(sites);
		map.setZoom(1);

		if ($('#list-collapse').hasClass('show')) {
			$('#show-list').text('Hide List');
		} else {
			$('#show-list').text('Show List');
		}
	} else {
		$('#show-list').text('No sites found');
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
			scale : 0.8
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
		const li = $(`<li class="list-group-item sl"><a href="/sites/${site.id}">${site.name}</a></li>`);
		$('#site-list').append(li);
	}
}

// removes current markers from the map
function clearMarkers() {
	for (let marker of currentMarkers) {
		marker.remove();
	}
	$('#site-list').html('');
}

// adds current dive site to user's bucket list
$('#bucket-list-add').on('click', async function addToList() {
	// get site id
	const id = $(this).attr('data-id');
	// send to server
	let res = await axios.post('/bucketlist', { id: id });
	// add alert
	const alert = $(`<div class="alert alert-info alert-dismissible fade show" role="alert"> ${res.data
		.message} <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button> </div>`);
	$('#msg').append(alert);
});

// deletes dive site from user's bucket list
$('.delete').on('click', async function deleteSite() {
	// get site id
	const id = $(this).attr('data-id');
	// send to server
	let res = await axios.post(`/bucketlist/${id}/delete`);
	// add alert
	const alert = $(`<div class="alert alert-info alert-dismissible fade show" role="alert"> ${res.data
		.message} <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button> </div>`);
	$(this).closest('li').remove();
	$('#msg').append(alert);
});

const mapToken = 'pk.eyJ1IjoiYmxha2VzMjQiLCJhIjoiY2toeHh3eXZsMDYzdDJzbDI5cnU3b2YwciJ9.YPfioQRftDU9m5783jldxA';
