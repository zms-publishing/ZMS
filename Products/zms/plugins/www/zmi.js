/**
 * $ZMI: Register functions to be executed on document.ready 
 */
ZMI = function() { this.readyFn = []};
ZMI.prototype.registerReady = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.ready = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.runReady = function() {this.readyFn.map(x=>x())};
$ZMI = new ZMI();

/**
 * Turbolinks
 */
document.addEventListener("turbolinks:load", function() {
	var ts = performance.now();
	console.log("BO turbolinks:load ");
	$ZMI.runReady();
	console.log("EO turbolinks:load " + (performance.now()-ts)+"msec");
});
