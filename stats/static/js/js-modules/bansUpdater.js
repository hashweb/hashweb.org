define(function() {
	function BansUpdater() {
		this.fetchLatestList();
	}


	BansUpdater.prototype.fetchLatestList = function() {
		fetch('/api/stats/bans').then(response => {
			if(response.ok) {
				return response.json().then(json => {
					this.updatePage(json);
				})
			}
		});
	}

	BansUpdater.prototype.updatePage = function(jsonResponse) {
		
	}

	bansUpdater = new BansUpdater();
})