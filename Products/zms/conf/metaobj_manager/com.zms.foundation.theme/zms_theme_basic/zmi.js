// CUSTOMISATION EXAMPLE:
// This script uses the REST API to get the number of child nodes in the trashcan
// and shows the trashcan icon in the header if the number is greater than 0
$ZMI.registerReady(function() {
	fetch($ZMI.getBaseUrl() + '/++rest_api/trashcan/get_child_nodes/count')
	.then(
		response => response.text())
		.then(data => {
			if (parseInt(data) > 0) {
				$('header #toggle_menu').after(`
					<li id="trashrestore" class="form-inline desktop hidden-xs" title="${data} Object(s) in Trashcan">
						<a target="_top" href="${$ZMI.getBaseUrl()}/trashcan/manage?lang=ger">
							<i class="fas fa-trash-restore"></i>
						</a>
					</li>`)
			};
		})
	.catch(error => console.error('Error ++rest_api:', error));
})