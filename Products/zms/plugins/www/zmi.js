/**
 * $ZMI: Register functions to be executed on document.ready 
 */
ZMI = function() { this.readyFn = []};
ZMI.prototype.registerReady = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.ready = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.runReady = function() {while (this.readyFn.length > 0) this.readyFn.pop()()};
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

