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
document.addEventListener('htmx:afterRequest', function(evt) {
	var ts = performance.now();
	console.log("BO htmx:afterRequest " + ts);
	$ZMI.runReady();
	console.log("EO htmx:afterRequest " + ts + "->" + (performance.now()-ts) + "msec");
});
