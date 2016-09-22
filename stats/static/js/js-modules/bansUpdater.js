define(function() {
	function BansUpdater() {
		this.fetchLatestList();
		this.setListeners();
		this.csrf = null;
	}


	BansUpdater.prototype.fetchLatestList = function() {
		fetch('/api/stats/bans').then(response => {
			if(response.ok) {
				return response.json().then(json => {
					this.updatePage(json);
				})
			}
		});

		setTimeout(() => { this.fetchLatestList() } , 2000);
	}

	BansUpdater.prototype.updatePage = function(jsonResponse) {
		for (item of jsonResponse) {
			var row = document.querySelector('tr[data-id="' + item.id + '"]');
				banLength = row.querySelector('.bans-table__td--ban-length input'),
				unbanDate = row.querySelector('.bans-table__td--unban-date input'),
				banReason = row.querySelector('.bans-table__td--ban-reason input');
                lastModified = row.querySelector('.bans-table__td--last-modified');


            console.log(lastModified);
			if (item.ban_length) banLength.value = item.ban_length;
			if (item.unban_date && item.unban_date !== "None") unbanDate.value = item.unban_date;
			if (item.reason) banReason.value     = item.reason;
            if (item.last_modified) lastModified.textContent = item.last_modified;
		}
	}

	BansUpdater.prototype.setListeners = function() {
		$('.bans-table__td--ban-length input, .bans-table__td--unban-date input, .bans-table__td--ban-reason input').change(data => {
			var obj = {}
			var id = data.target.dataset.id;
			obj['val'] = data.target.value;
			obj['name'] = data.target.dataset.name;
			// Now get CSRF Token and store it
			this.csrf = (this.csrf) ? this.csrf : document.querySelector('tr[data-id="'+ id +'"] input[name="csrfmiddlewaretoken"]').value;
			this.sendData(id, obj);
		});
	}

	BansUpdater.prototype.sendData = function(id, obj) {
		var headers = new Headers();
		headers.append('X-CSRFToken', this.csrf)

		fetch('/api/stats/bans/' + id, {
			method: 'POST',
			body: JSON.stringify(obj),
			credentials: 'include',
			headers: headers
		})
	}

	bansUpdater = new BansUpdater();
})
