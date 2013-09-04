/**
 * $ZMI: Register functions to be executed on document.ready 
 */
ZMI = function() { this.readyFn = []};
ZMI.prototype.registerReady = function(fn) {this.readyFn.push(fn)};
ZMI.prototype.runReady = function() {while (this.readyFn.length > 0) this.readyFn.pop()()};
var $ZMI = new ZMI();
