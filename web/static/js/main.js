(() => {
	'use strict';

	const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
	const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl, {trigger: "hover"}));

	$('.delete-btn').on('click', function (evt) {
		let text = "Cette action est irréversible!";
		let title = 'Supprimer cet élément?';
		Swal.fire({
			title: title,
			text: text,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Confirmer'
		}).then((result) => {
			if (result.value) {
				let url = $(this).data('url');
				window.location.href = url;
			}
		});
	});
	$('.action-btn').on('click', function (evt) {
		const text = $(this).data("message");
		const title = $(this).data("title");

		Swal.fire({
			title: title,
			text: text,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Confirmer'
		}).then((result) => {
			if (result.value) {
				let url = $(this).data('url');
				console.log(url);
				window.location.href = url;
			}
		});
	});
})();
