// ############################################################################
// ### Highlight
// ############################################################################

/**
 * Scroll to given element.
 * 
 * @see http://radio.javaranch.com/pascarello/2005/01/09/1105293729000.html
 */
function zmiScrollToElement(theElement) {
	var selectedPosX = 0;
	var selectedPosY = 0;
	while(theElement != null){
		selectedPosX += theElement.offsetLeft;
		selectedPosY += theElement.offsetTop;
		theElement = theElement.offsetParent;
	}
	window.scrollTo(selectedPosX,selectedPosY);
}

/**
 * Highlight all occurences of given text.
 */
function zmiDoHighlight(text) {
	var exp = text.replace(/\W/g,'');
	var regexp = new RegExp( "(" + exp + ")", "gi");
	var el = $('body');
	$('*',el)
		.andSelf()
		.contents()
		.filter(function(){
			return this.nodeType === 3;
		})
		.filter(function(){
			// Only match when contains 'simple string' anywhere in the text
			return this.nodeValue.match(regexp);
		})
		.each(function(){
			// Do something with this.nodeValue
			$(this).parent().html($(this).parent().html().replace( regexp, "<span class=\"highlight\">$1</span>"));
		});
}

/**
 * Init highlight.
 */
function zmiInitHighlight(s) {
	var raw = s.split(" ");
	var text1st = null;
	for (var i = 0; i < raw.length; i++) {
		var text = raw[i].basicTrim();
		if (text.length > 0) {
			if (text1st == null) {
				text1st = text;
			}
			zmiDoHighlight( text);
		}
	}
	if (text1st!=null) {
		var spans_highlight = $('span.highlight');
		if ( spans_highlight.length>0) {
			zmiScrollToElement(spans_highlight[0]);
		}
	}
}


$(function() {
	zmiInitHighlight(zmiParams[zmiParams['ZMS_HIGHLIGHT']]);
});

// ############################################################################