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
	var exp = text.replace(/\W/g,'.?');
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
			var raw = $(this).parent().html().split("<");
			var html = raw[0].replace( regexp, "<span class=\"highlight\">$1</span>");
			for (var i = 1; i < raw.length; i++) {
				var j = raw[i].indexOf(">");
				html += "<";
				if (j<0) {
					html = html
						+ raw[i].replace( regexp, "<span class=\"highlight\">$1</span>");
				}
				else {
					html = html
						+ raw[i].substr(0,j+1)
						+ raw[i].substr(j+1).replace( regexp, "<span class=\"highlight\">$1</span>");
				}
			}
			$(this).parent().html(html);
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
	try {
		zmiInitHighlight(zmiParams[zmiParams['ZMS_HIGHLIGHT']]);
	}
	catch (e) {
		// do nothing
	}
});

// ############################################################################