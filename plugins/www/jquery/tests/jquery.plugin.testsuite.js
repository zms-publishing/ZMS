//
// <script>
// $(function(){runPluginTestsuite()});
// </script>
// 

function zmiTestSetUp() {
	$('#zmi-debug').show();
}

function zmiTestAssertEquals(category, expectedResult, result) {
	zmiWriteDebug("[zmiTestAssertEquals]: " + category + " '" + expectedResult + "' --> '" + result + "'");
	if (expectedResult != result) {
		alert("AssertionError: " + category + " '" + expectedResult + "' does not match '" + result + "'!");
	}
}

function zmiTestRun() {
	zmiTestSetUp();
	zmiTestAssertEquals( "zmiRelativateUrl", "./e10", zmiRelativateUrl("http://localhost:8080/e8", "http://localhost:8080/e8/e10"));
	zmiTestAssertEquals( "zmiRelativateUrl", "./../e9/e28/e23", zmiRelativateUrl("http://localhost:8080/e8", "http://localhost:8080/e9/e28/e23"));
	zmiTestAssertEquals( "zmiRelativateUrl", "http://www.python.org/pypi", zmiRelativateUrl("http://localhost:8080/e8", "http://www.python.org/pypi"));
	zmiTestTearDown();
}

function zmiTestTearDown() {
}