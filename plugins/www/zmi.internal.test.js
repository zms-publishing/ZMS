test( "zmi.internal.js::testRelativateUrl", function() {
	var relurl = $ZMI.relativateUrl("http://server/content/e2/e3","","http://server/content/e1");
	equal( relurl, "./../e2/e3", "Passed!" );
	var relurl = $ZMI.relativateUrl("http://server/content/e1/e3","","http://server/content/e1");
	equal( relurl, "./e3", "Passed!" );
	var relurl = $ZMI.relativateUrl("http://server/content/e2/e3","","http://server/content/e1/e4/e5");
	equal( relurl, "./../../../e2/e3", "Passed!" );
	var relurl = $ZMI.relativateUrl("http://server/content/e2/e3","#e6","http://server/content/e1/e4");
	equal( relurl, "./../../e2/e3#e6", "Passed!" );
});
