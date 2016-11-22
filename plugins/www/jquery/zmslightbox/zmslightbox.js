// JavaScript Document
// MODAL CONSTRUCTOR
function add_zmslightbox(hiurl) {
	$('body').append('<div id="zmslightbox-bg" onclick="remove_zmslightbox()"></div>\
		<div id="zmslightbox-controls" onclick="remove_zmslightbox()"><span id="close-zmslightbox">Close Lightbox</span></div>\
		<div id="zmslightbox-wrapper"><img src="'+hiurl+'" /></div>');
	$('#zmslightbox-wrapper img').on('click', function() {
			$(this).toggleClass('fullimage');
			$(this).parent().toggleClass('fullimage');
			if ( $(this).width() > $(window).width()) {
				$(this).parent().removeClass('fullscreen');
				$(this).parent().scrollLeft($(window).width()/2);
			} else {
				$(this).parent().addClass('fullscreen');
			};
			center_zmslightbox($('#zmslightbox-wrapper img'));
	});
	$('#zmslightbox-wrapper img').hide();
	$('#zmslightbox-bg').css('height',$('body').height()+'px');
	$('body').addClass('zmslightbox');
};

function remove_zmslightbox() {
	$('#zmslightbox-controls').remove();
	$('#zmslightbox-wrapper').remove();
	$('#zmslightbox-bg').remove();
	$('body').removeClass('zmslightbox');
};

function center_zmslightbox(imgobj) {
	var ww = $(window).width();
	var wh = $(window).height();
	var wt = $(window).scrollTop();
	var cx = ww/2;
	var cy = wt + wh/2;
	var iw = imgobj.width();
	var ih = imgobj.height();
	console.log('imgobj.height: ' + ih);
	if ( ih > wh && !( imgobj.parent().hasClass('fullimage') ) ) {
		imgobj.css('height',$(window).height() + 'px');
		iw = imgobj.width();
		ih = imgobj.height();
	} else {
		imgobj.css('height','auto');
	};
	var c_il = cx-(0.5*iw);
	var c_it = cy-(0.5*ih);
	$('#zmslightbox-wrapper').css('top',c_it + 'px');
	$('#zmslightbox-wrapper img').show('slow');
};

// On Window Resize
$(window).resize(function() {
	try {
		center_zmslightbox($('#zmslightbox-wrapper img'))
	} catch(err) {
		return false;
	}
});
// On ESCPAE button
$(document).on('keyup',function(evt) {
	if (evt.keyCode ==27) {
		remove_zmslightbox();
	};
});

// EXECUTE
function show_zmslightbox(img) {
	add_zmslightbox(img.attr('data-hiresimg'));
	$('#zmslightbox-wrapper img').load( function() {
		center_zmslightbox($('#zmslightbox-wrapper img'));
	});
};
