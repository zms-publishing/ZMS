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
		document.querySelector('body').classList.add('loading');
	});
	document.addEventListener('htmx:afterRequest', (evt) => {
		var bodyClass = evt.detail.xhr.responseText;
		bodyClass = bodyClass.substr(bodyClass.indexOf("<body"));
		if ( bodyClass.indexOf("<body") > -1 ) {
			bodyClass = bodyClass.substr(bodyClass.indexOf("class=\"")+"class=\"".length);
			bodyClass = bodyClass.substr(0,bodyClass.indexOf("\""));
			document.querySelector('body').classList = bodyClass;
			$ZMI.runReady();
		};
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
