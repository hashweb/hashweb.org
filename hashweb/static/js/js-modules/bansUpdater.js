define(function() {
	function fetchLatestList() {
		fetch('/api/stats/bans').then(function(response) {
			if(response.ok) {
				console.log(response);
				return response.json().then(function(json) {
					console.log(json);
				})
			}
		});

		setTimeout(fetchLatestList, 3000);
	}

	fetchLatestList();
})