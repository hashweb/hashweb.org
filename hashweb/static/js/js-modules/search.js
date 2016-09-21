require([], function() {
	$(document).ready(function() {
		// highlight the searched text
		var dataRef = $('.results-wrapper').data('ref');
		if (dataRef) {
			$('li[data-ref="'+ dataRef +'"]').addClass('highlight')
			console.log($('li[data-ref="'+ dataRef +'"]'))
		}

	});
});