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
 */
if (typeof htmx != "undefined") {
	document.addEventListener('htmx:beforeRequest', (evt) => {
		document.querySelector('body').classList.add('loading');
	});
	document.addEventListener('htmx:afterRequest', (evt) => {
		var bodyClass = evt.detail.xhr.responseText;
		bodyClass = bodyClass.substr(bodyClass.indexOf("<body"));
		bodyClass = bodyClass.substr(bodyClass.indexOf("class=\"")+"class=\"".length);
		bodyClass = bodyClass.substr(0,bodyClass.indexOf("\""));
		document.querySelector('body').classList = bodyClass;
		document.querySelector('body').classList.remove('loading')
		document.querySelector('body').classList.add('loaded');
		$ZMI.runReady();
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
