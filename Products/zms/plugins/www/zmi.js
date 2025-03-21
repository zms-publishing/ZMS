/**
 * $ZMI: Register functions to be executed on document.ready 
 */
ZMI = function() { this.readyFn = {}};
ZMI.prototype.generateUUID = function() { // Public Domain/MIT
    var d = new Date().getTime();//Timestamp
    var d2 = ((typeof performance !== 'undefined') && performance.now && (performance.now()*1000)) || 0;//Time in microseconds since page-load or 0 if unsupported
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16;//random number between 0 and 16
        if(d > 0){//Use timestamp until depleted
            r = (d + r)%16 | 0;
            d = Math.floor(d/16);
        } else {//Use microseconds since page-load if supported
            r = (d2 + r)%16 | 0;
            d2 = Math.floor(d2/16);
        }
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}
ZMI.prototype.registerReady = function(fn, key) {
	key = typeof key == 'undefined' ? this.generateUUID() : key;
	if (typeof this.readyFn[key] == 'undefined') {
		this.readyFn[key] = fn;
	}
};
ZMI.prototype.runReady = function() {Object.entries(this.readyFn).map(([k, v], i)=>v())};
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
 * be renewed after htmx request. That is why the classList has to be added again the <body> 
 * element after request
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
	});
	// Listen for the htmx response error event
	if (window.parent.manage_main && window.parent.manage_main.htmx) {
		window.parent.manage_main.htmx.on('htmx:beforeSwap', (evt) => { 
			if (evt.detail.xhr.status === 404) {
				// Remove html body and wtrite error message
				window.parent.manage_main.document.querySelector('body').innerHTML = `
						<header class="navbar navbar-nav p-1" style="height:2.65rem;">
							<div class="navbar-brand text-white">
								404: Page not found!
							</div>
						</header>`;
			}
		});
	};
	document.addEventListener('htmx:sendError', (evt) => {
		const manage_main_href = evt.detail.pathInfo.finalRequestPath;
		if ( confirm(getZMILangStr('MSG_CONFIRM_RELOAD'))) {
			const topWindow = window.parent.manage_main || window;
			topWindow.location.assign(manage_main_href);
		}
	});
	document.addEventListener('htmx:afterSettle', (evt) => {
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
	});
	window.onload = function() {
		$ZMI.runReady();
	};
	// https://htmx.org/quirks/#history-can-be-tricky
	document.addEventListener('htmx:historyRestore', (e) => {
		$ZMI.runReady();
	});
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
