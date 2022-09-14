// Functions for advanced ZMSGraphic-editing

var ZMSGraphic_elName = null;
var ZMSGraphic_params = null;
var ZMSGraphic_lang = null;
var ZMSGraphic_pil = null;
var $ZMSGraphic_img = null;
var $ZMSGraphic_cropper = null;
var $ZMSGraphic_buttons = null;
var ZMSGraphic_cropcoords = null;
var ZMSGraphic_action = null;
var ZMSGraphic_act_width = null;
var ZMSGraphic_act_height = null;
var ZMSGraphic_extEdit_slider = false;

function ZMSGraphic_extEdit_initialize() {
	$("body").append("<style>div.jcrop-holder input {display:none;visibility:hidden;}</style>");
	$("#zmiModalZMSGraphic_extEdit_actions #ZMSGraphic_extEdit_crop").click(function() {
		if ( $(this).prop('disabled') == undefined || $(this).prop('disabled') == false ) {
			$(this).prop("disabled",true);
			$(this).removeClass('btn-secondary').addClass('btn-dark');
			$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_slider").prop("disabled",true);
			$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_width").prop("disabled",true);
			$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_height").prop("disabled",true);
			$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_proportional").prop("disabled",true);
			ZMSGraphic_action = 'crop';
			changeCropperAvailability(true,true);
		} else {
			if ($ZMSGraphic_cropper != null) {
				// $ZMSGraphic_cropper.clear();
				$ZMSGraphic_cropper.cropper('clear');
				$ZMSGraphic_cropper.cropper('destroy');
				$ZMSGraphic_cropper = null;
				$(this).prop("disabled",false);
				$(this).removeClass('btn-dark').addClass('btn-secondary');
				$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_slider").prop("disabled",false);
				$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_width").prop("disabled",false);
				$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_height").prop("disabled",false);
				$("#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_proportional").prop("disabled",false);
			}
			ZMSGraphic_action = null;
		}
	});
	$("#zmiModalZMSGraphic_extEdit_actions #ZMSGraphic_extEdit_preview").click(function() {
		ZMSGraphic_action = 'preview';
		if (confirm($(this).attr('title')+'?')) {
			ZMSGraphic_extEdit_apply();
		}
		ZMSGraphic_action = null;
	});
}

/**
 * Start image-editor.
 */
function ZMSGraphic_extEdit_action( elName, elParams, pil) {
	$ZMI.setCursorWait("ZMSGraphic_extEdit_action");
	if (typeof pil != 'undefined') {
		ZMSGraphic_pil = pil;
	}
	ZMSGraphic_elName = elName;
	ZMSGraphic_params = {lang:$("#lang").val(),preview:$("#preview").val(),form_id:$("#form_id").val()};
	var elParamsSplit = elParams.split('&');
	for (var i = 0; i < elParamsSplit.length; i++) {
		var s = elParamsSplit[i];
		var k = s.substr(0,s.indexOf('='));
		var v = s.substr(s.indexOf('=')+1);
		ZMSGraphic_params[k] = v;
	}
	zmiRegisterParams(elName,ZMSGraphic_params);
	if (!ZMSGraphic_pil) {
		var $elCrop = $($('#ZMSGraphic_extEdit_crop').parents('div')[0]);
		$elCrop.hide();
	}
	var $elPreview = $($('#ZMSGraphic_extEdit_preview').parents('div')[0]);
	var togglePreview = $('input:checkbox#generate_preview_'+elName).length > 0;
	if (togglePreview) {
		$elPreview.show();
	}
	else {
		$elPreview.hide();
	}
	zmiModal("#ZMSGraphic_extEdit_actions",{
			title:getZMILangStr('ATTR_IMAGE')+': '+getZMILangStr('BTN_EDIT'),
			width:800,
			open:function() {
				console.log("BO ZMSGraphic_extEdit_actions.open");
				$.get('getTempBlobjPropertyUrl',ZMSGraphic_params,
					function(data) {
						console.log("BO getTempBlobjPropertyUrl");
						var result = eval('('+data+')');
						ZMSGraphic_act_width = result['width'];
						ZMSGraphic_act_height = result['height'];
						// Dimensions
						var w = $(`input#width_${ZMSGraphic_elName}`).val();
						var h = $(`input#height_${ZMSGraphic_elName}`).val();
						$('input#ZMSGraphic_extEdit_width').val(w)
							.keyup(function(){
									var w = parseInt($(this).val());
									if (!(isNaN(w))) {
									$('input#ZMSGraphic_extEdit_width').val(w);
									if ($("#ZMSGraphic_extEdit_proportional").prop("checked")) {
										var v = w/ZMSGraphic_act_width;
										var h = Math.round(v*ZMSGraphic_act_height);
										$("input#ZMSGraphic_extEdit_height").val(h);
									}
									var h = $("#ZMSGraphic_extEdit_height").val();
									$ZMSGraphic_img.attr({'width':w,'height':h});
									}
								});
						$('input#ZMSGraphic_extEdit_height').val(h)
							.keyup(function(){
									var h = parseInt($(this).val());
									if (!(isNaN(h))) {
									$('input#ZMSGraphic_extEdit_height').val(h);
									if ($("#ZMSGraphic_extEdit_proportional").prop("checked")) {
										var v = h/ZMSGraphic_act_height;
										var w = Math.round(v*ZMSGraphic_act_width);
										$("input#ZMSGraphic_extEdit_width").val(w);
									}
									var w = $("input#ZMSGraphic_extEdit_width").val();
									$ZMSGraphic_img.attr({'width':w,'height':h});
									}
								});
						var v = Math.round(100*w/ZMSGraphic_act_width);
						// Image
						var canvasMax = 600;
						var canvasHeight = ZMSGraphic_act_height;
						var canvasWidth = ZMSGraphic_act_width;
						if (canvasWidth > canvasMax || canvasHeight > canvasMax) {
							if (canvasWidth > canvasMax) {
								canvasHeight = Math.round(canvasHeight*canvasMax/canvasWidth);
								canvasWidth = canvasMax;
							}
							else {
								canvasWidth = Math.round(canvasWidth*canvasMax/canvasHeight);
								canvasHeight = canvasMax;
							}
						}
						$('.modal-body div#ZMSGraphic_extEdit_image').css({width:canvasWidth,height:canvasHeight});
						$('.modal-body div#ZMSGraphic_extEdit_image').html('<img src="'+result['src']+'" width="'+v+'%"/>');
						$ZMSGraphic_img = $('.modal-body div#ZMSGraphic_extEdit_image img');
						// Slider

						$(".modal-body #ZMSGraphic_extEdit_slider").on("input", function() {
							$(this).trigger('change');
						})
						$(".modal-body #ZMSGraphic_extEdit_slider").on("change", function() {
									var v = parseInt($(this).val());
									var w = Math.round(v*ZMSGraphic_act_width/100);
									var h = Math.round(v*ZMSGraphic_act_height/100);
									$('input#ZMSGraphic_extEdit_width').val(w);
									$('input#ZMSGraphic_extEdit_height').val(h);
									$ZMSGraphic_img.attr({width:v+'%'});
								});
						ZMSGraphic_extEdit_initialize();
						$ZMI.setCursorAuto("ZMSGraphic_extEdit_action");
					});
					console.log("EO ZMSGraphic_extEdit_actions.open");
				},
				beforeClose:function() {
					$('div#ZMSGraphic_extEdit_image').html('');
					changeCropperAvailability(false);
				},
		});
}


/**
 * Apply changes to image.
 */
function ZMSGraphic_extEdit_set(elName, src, filename, width, height, elParams, pil) {
	var img = $('img#img_'+elName);
	if (img.length == 0) {
		var html = '';
		html += '<input type="hidden" id="width_'+elName+'" name="width_'+elName+':int" value="'+width+'"/>';
		html += '<input type="hidden" id="height_'+elName+'" name="height_'+elName+':int" value="'+height+'"/>';
		html += '<a href="javascript:ZMSGraphic_extEdit_action(';
		html += '\''+elName+'\'';
		html += ',\''+elParams+'\'';
		if (typeof pil != 'undefined') {
			html += ','+pil;
		}
		html += ')" class="ZMSGraphic_extEdit_action">';
		html += '<img id="img_'+elName+'">';
		html += '</a>';
		$('#ZMSGraphic_extEdit_preview_'+elName).html(html);
	}
	else {
		zmiUndoBlobDelete(elName);
	}
	img = $('img#img_'+elName);
	img.attr("src",src);
	img.css({maxHeight:80,maxWidth:80});
	img.parent().addClass('changed');
	$('input#width_'+elName).val(width);
	$('input#height_'+elName).val(height);
	$('span#filename_'+elName).html(filename);
	$('span#size_'+elName).html("");
	var $label = $('#zmi-image-' + ZMSGraphic_elName + ' label.custom-file-label');
	$label.text($label.text().replace(/\(([^)]+)\)/g,'('+width+'x'+height+'px)'));
	zmiSwitchBlobButtons(elName);
}

/**
 * Apply changes.
 */
function ZMSGraphic_extEdit_apply() {
	console.log("ZMSGraphic_extEdit_apply:"+ZMSGraphic_action);
	// Preview
	if (ZMSGraphic_action == 'preview') {
		var params = {'action':ZMSGraphic_action};
		for (var i in ZMSGraphic_params) {
			params[i] = ZMSGraphic_params[i];
		}
		$.get('manage_changeTempBlobjProperty',params,
				function(data){
					if (data.length==0) return;
					var result = eval('('+data+')');
					var elName = result['elName'];
					var elParams = 'lang='+escape(result['lang'])+'&key='+escape(result['key'])+'&form_id='+escape(result['form_id']);
					ZMSGraphic_extEdit_set(elName,result['src'],result['filename'],result['width'],result['height'],elParams);
				});
	}
	// Crop
	else if (ZMSGraphic_action == 'crop') {
		var w = parseInt($('input#ZMSGraphic_extEdit_width').val());
		var w_orig = parseInt($('input#width_'+ZMSGraphic_elName).val());
		var h = parseInt($('input#ZMSGraphic_extEdit_height').val());
		var h_orig = parseInt($('input#height_'+ZMSGraphic_elName).val());
		var c = ZMSGraphic_cropcoords;
		if ( w != w_orig || h != h_orig) {
			ZMSGraphic_action = 'resize,crop';
		}
		var params = {'action':ZMSGraphic_action,'width:int':w,'height:int':h,'x0:int':Math.round(c.x),'y0:int':Math.round(c.y),'x1:int':Math.round(c.x+c.width),'y2:int':Math.round(c.y+c.height)};
		for (var i in ZMSGraphic_params) {
			params[i] = ZMSGraphic_params[i];
		}
		$.get('manage_changeTempBlobjProperty',params,
				function(data){
					if (data.length==0) return;
					var result = eval('('+data+')');
					console.log(result);
					ZMSGraphic_extEdit_set(ZMSGraphic_elName,result['src'],result['filename'],result['width'],result['height']);
				});
	}
	// Resize
	else {
		var w = parseInt($('input#ZMSGraphic_extEdit_width').val());
		var w_orig = parseInt($('input#width_'+ZMSGraphic_elName).val());
		var h = parseInt($('input#ZMSGraphic_extEdit_height').val());
		var h_orig = parseInt($('input#height_'+ZMSGraphic_elName).val());
		var v = Math.round(100*w/ZMSGraphic_act_width);
		if ( w != w_orig || h != h_orig) {
			if (ZMSGraphic_pil) {
				var params = {'action':'resize','width:int':w,'height:int':h};
				for (var i in ZMSGraphic_params) {
					params[i] = ZMSGraphic_params[i];
				}
				$.get('manage_changeTempBlobjProperty',params,
						function(data){
							if (data.length==0) return;
							var result = eval('('+data+')');
							ZMSGraphic_extEdit_set(ZMSGraphic_elName,result['src'],result['filename'],result['width'],result['height']);
						});
				v = 100;
			}
			else {
				$('input#width_'+ZMSGraphic_elName).val(w);
				$('input#height_'+ZMSGraphic_elName).val(h)
			}
			dims = `(${w}x${h}px)`;
			new_label = $(`.custom-file label[for="${ZMSGraphic_elName}"]`).text().replace(/\(.*\)/g, dims);
			$(`.custom-file label[for="${ZMSGraphic_elName}"]`)
				.text(new_label)
				.addClass('new_label');

		}
	}
	// Close dialog.
	zmiModal("hide");
	return false;
}

function changeCropperAvailability(available, cropping) {
	if (available) {
		runPluginCropper(function() {
			$ZMSGraphic_img.cropper({
				allowSelect	: false,
				setSelect	: [ 0, 0, 25, 25 ],
				minSize		: [25, 25],
				maxSize		: [ZMSGraphic_act_width, ZMSGraphic_act_height],
				handles		: true,
				crop		: function(e) {
					if (ZMSGraphic_action == 'crop') {
						ZMSGraphic_cropcoords = e.detail;
						$('#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_width').val( Math.round(ZMSGraphic_cropcoords.width) );
						$('#zmiModalZMSGraphic_extEdit_actions input#ZMSGraphic_extEdit_height').val( Math.round(ZMSGraphic_cropcoords.height) );
					}
				}
			});
			$ZMSGraphic_cropper = $ZMSGraphic_img;
		});
	}
}
