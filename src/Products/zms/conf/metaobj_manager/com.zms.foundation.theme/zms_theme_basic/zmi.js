// CUSTOMISATION EXAMPLE: 
// Add a trashcan icon to the header if there are objects in the trashcan

$ZMI.registerReady(function() {
	// First read the ZMS-clients localstorage trashcan key to see if the number of trashcan children is already stored
	// If not, fetch the data from the REST API /get_child_nodes/count
	// If the number of trashcan children is greater than 0, show the trashcan icon in the header
	// If the user is in the trashcan gui, any request will refresh the localstorage trashcan key and icon is not shown

	let client_id = document.body.getAttribute('data-root');
	let trashcan_key = `ZMS.trashcan.${client_id}`;
	let trashcan_data = localStorage.getItem(trashcan_key);

	let has_client_id = client_id !== null && client_id !== undefined && client_id !== '';
	let no_trashcan_icon = $('header #trashrestore').length === 0;

	if (has_client_id) {
		if (window.location.href.includes('trashcan')) {
			localStorage.removeItem(trashcan_key);
		} else if (no_trashcan_icon) {
			if (trashcan_data) {
				if (parseInt(trashcan_data, 10) > 0) {
					const sanitized_data = parseInt(trashcan_data, 10);
					const trashcan_title = `${sanitized_data} Object(s) in Trashcan`;
					const trashcan_url = `${$ZMI.getBaseUrl()}/trashcan/manage?lang=${getZMILang()}`;
					$('header #toggle_menu').after(`
						<li id="trashrestore" class="form-inline desktop hidden-xs" title="${trashcan_title}">
							<a target="_top" href="${trashcan_url}">
								<i class="fas fa-trash-restore"></i>
							</a>
						</li>`);
				};
			} else {
				fetch($ZMI.getBaseUrl() + '/++rest_api/trashcan/get_child_nodes/count')
				.then(
					response => response.text())
					.then(data => {
						if (parseInt(data,10) > 0) {
							const sanitized_data = parseInt(data, 10);
							const trashcan_title = `${sanitized_data} Object(s) in Trashcan`;
							const trashcan_url = `${$ZMI.getBaseUrl()}/trashcan/manage?lang=${getZMILang()}`;
							$('header #toggle_menu').after(`
								<li id="trashrestore" class="form-inline desktop hidden-xs" title="${trashcan_title}">
									<a target="_top" href="${trashcan_url}">
										<i class="fas fa-trash-restore"></i>
									</a>
								</li>`);
							localStorage.setItem(trashcan_key, data);
						};
					})
				.catch(error => console.error('Error ++rest_api:', error));
			};
		}
	}
})