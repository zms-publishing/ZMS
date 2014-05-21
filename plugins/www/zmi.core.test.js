test( "zmi.core.js::String.prototype", function() {
	equal( "  ab c  ".removeWhiteSpaces(), "abc", "removeWhiteSpaces passed!" );
	equal( "  ab c  ".leftTrim(), "ab c  ", "leftTrim passed!" );
	equal( "  ab c  ".rightTrim(), "  ab c", "rightTrim passed!" );
	equal( "  ab c  ".basicTrim(), "ab c", "basicTrim passed!" );
	equal( "  ab c  ".superTrim(), "ab c", "superTrim passed!" );
	ok( "abcdefghijk".startsWith("abc"), "startsWith passed!" );
	ok( !("abcdefghijk".startsWith("xyz")), "!startsWith passed!" );
	ok( "abcdefghijk".endsWith("ijk"), "endsWith passed!" );
	ok( !("abcdefghijk".endsWith("xyz")), "!endsWith passed!" );
});
