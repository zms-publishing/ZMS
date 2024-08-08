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
 * Turbolinks
 */
$ZMI.ready(function() {
	if (document.querySelector('body') != null && document.querySelector('body').classList.contains("loading")) {
		document.querySelector('body').classList.remove('loading');
	}
})
document.addEventListener('htmx:beforeRequest', function(evt) {
	document.querySelector('body').classList.add('loading');
});
document.addEventListener('htmx:afterRequest', function(evt) {
	document.querySelector('body').classList.remove('loading')
	document.querySelector('body').classList.add('loaded');
	var ts = performance.now();
	console.log("BO htmx:afterRequest ", ts, evt);
	$ZMI.runReady();
	console.log("EO htmx:afterRequest ", ts, "->" + (performance.now()-ts) + "ms");
});
