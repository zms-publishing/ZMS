/**
 * $ZMI: Register functions to be executed on document.ready 
 */
ZMI = function() { this.readyFn = []};
ZMI.prototype.registerReady = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.ready = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.runReady = function() {this.readyFn.map(x=>x())};
$ZMI = new ZMI();

/**
 * $: Register 
 */
if (typeof $ == "undefined") {
	$ = function(arg0, arg1) {
		if (typeof arg0 == "function") {
			$ZMI.registerReady(arg0);
		}
		return $ZMI;
	}
}

/**
 * HTMX: Add loading class to body on htmx:beforeRequest and remove it on htmx:afterRequest
 * Hint: Due to DOM limitations, it’s not possible to use the outerHTML method on the <body> 
 * element. htmx will change outerHTML on <body> to use innerHTML. So, the classList will not 
 * be renewed after htmx request. To fix this, we have to add the classList to the <body> element
 * Source: https://htmx.org/attributes/hx-swap/
 */
if (typeof htmx != "undefined") {
	document.addEventListener('htmx:beforeRequest', (evt) => {
		const body = document.querySelector('body');
		// If not send from SAVE button, check if form is modified
		if ( ! evt.target.classList.contains('btn-primary') && ! evt.currentTarget.activeElement.classList.contains('btn-primary')) {
			if (body.classList.contains("form-modified") && ! confirm(getZMILangStr('MSG_CONFIRM_DISCARD_CHANGES'))) {
				return evt.preventDefault();
			}
		}
		body.classList.add('loading');
	});
	document.addEventListener('htmx:afterRequest', (evt) => {
		var resp_text = evt.detail.xhr.responseText;
		var parser = new DOMParser();
		var resp_doc = parser.parseFromString(resp_text , 'text/html');
		var newBody = resp_doc.querySelector('body');
		// Check if response is a full HTML page or just a message
		if ( resp_text.indexOf("<body") > -1 && newBody.childNodes[0].id!='zmi_manage_tabs_message') {
			var currentBody = document.querySelector('body');
			// Copy all attributes from newBody to currentBody
			Array.from(newBody.attributes).forEach(attr => {
				currentBody.setAttribute(attr.name, attr.value);
			});
			// Remove attributes that are not in newBody
			Array.from(currentBody.attributes).forEach(attr => {
				if (!newBody.hasAttribute(attr.name)) {
					currentBody.removeAttribute(attr.name);
				}
			});
			// Trigger Ready Event
			$ZMI.runReady();
		};
		// Remove form-modified class from
		Array.from(document.getElementsByClassName('form-modified')).forEach(
			e => { e.classList.remove('form-modified') }
		);
		document.querySelector('body').classList.remove('loading');
		document.querySelector('body').classList.add('loaded');
	});
	window.onload = function() {
		$ZMI.runReady();
	};
}

/**
 * jQuery: Run $ZMI.ready() on document.ready
 */
$ZMI.registerReady(function() {
		// Remove loading class from body
	if (document.querySelector('body') != null && document.querySelector('body').classList.contains("loading")) {
		document.querySelector('body').classList.remove('loading');
	};
});

$ZMI.runReady();
