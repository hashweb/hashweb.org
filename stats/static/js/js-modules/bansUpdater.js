define(function() {
	function BansUpdater() {
		this.init();
		this.setListeners();
		this.csrf = null;
        this.updatePaused = false;
	}

    BansUpdater.prototype.init = function() {
        if (!this.updatePaused) {
            this.fetchLatestList();
        }

        setTimeout(() => { this.init() } , 2000);
    }


	BansUpdater.prototype.fetchLatestList = function() {
		fetch('/api/stats/bans').then(response => {
			if(response.ok) {
				return response.json().then(json => {
                    if (!this.updatePaused) {
					   this.updatePage(json);
                    }
				})
			}
		});
	}

	BansUpdater.prototype.updatePage = function(jsonResponse) {
		for (item of jsonResponse) {
			var row = document.querySelector('tr[data-id="' + item.id + '"]');
				banLength = row.querySelector('.bans-table__td--ban-length input'),
				unbanDate = row.querySelector('.bans-table__td--unban-date input'),
				banReason = row.querySelector('.bans-table__td--ban-reason input');
                lastModified = row.querySelector('.bans-table__td--last-modified');


			if (item.ban_length) banLength.value = item.ban_length;
			if (item.unban_date && item.unban_date !== "None") unbanDate.value = item.unban_date;
			if (item.reason) banReason.value     = item.reason;
            if (item.last_modified) lastModified.textContent = item.last_modified;
		}
	}

	BansUpdater.prototype.setListeners = function() {
		$('.bans-table__td--ban-length input, .bans-table__td--unban-date input, .bans-table__td--ban-reason input').on('keyup change', data => {
			var obj = {}
			var id = data.target.dataset.id;
			obj['val'] = data.target.value;
			obj['name'] = data.target.dataset.name;
			// Now get CSRF Token and store it
			this.csrf = (this.csrf) ? this.csrf : document.querySelector('tr[data-id="'+ id +'"] input[name="csrfmiddlewaretoken"]').value;
			this.sendData(id, obj);
		});

        $('.bans-table__td--ban-length input, .bans-table__td--unban-date input, .bans-table__td--ban-reason input').on('focus', data => {
            console.log('focusing on form element');
            this.updatePaused = true;
        });

        $('.bans-table__td--ban-length input, .bans-table__td--unban-date input, .bans-table__td--ban-reason input').on('blur', data => {
            console.log('blur from element');
            this.updatePaused = false;
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
