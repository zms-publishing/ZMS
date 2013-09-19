/**
 * Functions for advanced ZMSGraphic-editing.
 */

var ZMSGraphic_elName = null;
var ZMSGraphic_params = null;
var ZMSGraphic_lang = null;
var ZMSGraphic_pil = null;
var $ZMSGraphic_img = null;
var $ZMSGraphic_buttons = null;
var $ZMSGraphic_cropapi = null;
var ZMSGraphic_cropcoords = null;
var ZMSGraphic_action = null;
var ZMSGraphic_act_width = null;
var ZMSGraphic_act_height = null;
var ZMSGraphic_extEdit_initialized = false;

function ZMSGraphic_extEdit_initialize() {
	if (ZMSGraphic_extEdit_initialized) {
		return;
	}
	ZMSGraphic_extEdit_initialized = true;
	$ZMI.setCursorWait("ZMSGraphic_extEdit_initialize");  
	pluginUI("body",function() {
			$ZMSGraphic_buttons = $('span[id^=ZMSGraphic_extEdit_]');
			$ZMSGraphic_buttons.click(ZMSGraphic_extEdit_clickedAction);
			$ZMI.setCursorAuto("ZMSGraphic_extEdit_initialize");
	});
}

/**
 * Start image-editor.
 */
function ZMSGraphic_extEdit_action( elName, elParams, pil) {
	$ZMI.setCursorWait("ZMSGraphic_extEdit_action");
	ZMSGraphic_extEdit_initialize();
	if (typeof pil != 'undefined') {
		ZMSGraphic_pil = pil;
	}
	ZMSGraphic_elName = elName;
	ZMSGraphic_params = {preview:'preview'};
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
					$ZMI.writeDebug("BO open");
					$.get('getTempBlobjPropertyUrl',ZMSGraphic_params,
						function(data) {
							$ZMI.writeDebug("BO getTempBlobjPropertyUrl");
							var result = eval('('+data+')');
							ZMSGraphic_act_width = result['width'];
							ZMSGraphic_act_height = result['height'];
							pluginUI("body",function() {
									// Dimensions
									var w = $('input#width_'+ZMSGraphic_elName).val();
									var h = $('input#height_'+ZMSGraphic_elName).val();
									$('input#ZMSGraphic_extEdit_width').val(w)
										.keyup(function(){
												var w = parseInt($(this).val());
												if ($("#ZMSGraphic_extEdit_proportional").prop("checked")) {
													var v = w/ZMSGraphic_act_width;
													var h = Math.round(v*ZMSGraphic_act_height);
													$("input#ZMSGraphic_extEdit_height").val(h);
												}
												var h = $("#ZMSGraphic_extEdit_height").val();
												$ZMSGraphic_img.attr({'width':w,'height':h});
											});
									$('input#ZMSGraphic_extEdit_height').val(h)
										.keyup(function(){
												var h = parseInt($(this).val());
												if ($("#ZMSGraphic_extEdit_proportional").prop("checked")) {
													var v = h/ZMSGraphic_act_height;
													var w = Math.round(v*ZMSGraphic_act_width);
													$("input#ZMSGraphic_extEdit_width").val(w);
												}
												var w = $("input#ZMSGraphic_extEdit_width").val();
												$ZMSGraphic_img.attr({'width':w,'height':h});
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
									$('div#ZMSGraphic_extEdit_image').css({width:canvasWidth,height:canvasHeight});
									$('div#ZMSGraphic_extEdit_image').html('<img src="'+result['src']+'" width="'+v+'%"/>');
									$ZMSGraphic_img = $('div#ZMSGraphic_extEdit_image img');
									// Slider
									$(".slider").slider({
										orientation: "vertical",
										range: "min",
										min: 0,
										max: 100,
										slide: function(event, ui) {
												var v = ui.value;
												$(".perc").html(v+'%');
												var w = Math.round(v*ZMSGraphic_act_width/100);
												var h = Math.round(v*ZMSGraphic_act_height/100);
												$('input#ZMSGraphic_extEdit_width').val(w);
												$('input#ZMSGraphic_extEdit_height').val(h);
												$ZMSGraphic_img.attr({width:v+'%'});
										}
									}).slider("value",v);
									$(".perc").html(v+'%');
									$ZMI.setCursorAuto("ZMSGraphic_extEdit_action");
							});
					});
					$ZMI.writeDebug("EO open");
				},
				beforeClose:function() {
					$ZMI.writeDebug("BO beforeClose");
					$('div#ZMSGraphic_extEdit_image').html('');
					changeJcropAvailability(false);
					$ZMI.writeDebug("EO beforeClose");
				}
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
		html += '<img id="img_'+elName+'"';
		if (width > 80 || height > 80) {
			if ( width > height) {
				html += ' width="80"';
			}
			else {
				html += ' height="80"';
			}
		}
		html += '>';
		html += '</a>';
		$('#ZMSGraphic_extEdit_preview_'+elName).html(html);
	}
	else {
		zmiUndoBlobDelete(elName);
	}
	img = $('img#img_'+elName);
	img.attr('src',src).css('background-color','#FF9900');
	$('input#width_'+elName).val(width);
	$('input#height_'+elName).val(height);
	$('span#filename_'+elName).html(filename);
	$('span#size_'+elName).html("");
	$('span#dimensions_'+elName).html(width+'x'+height+'px');
	zmiSwitchBlobButtons(elName);
}

/**
 * Apply changes.
 */
function ZMSGraphic_extEdit_apply() {
	$ZMI.writeDebug("ZMSGraphic_extEdit_apply:"+ZMSGraphic_action);
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
		var c = ZMSGraphic_cropcoords;
		var canvasWidth = $('div#ZMSGraphic_extEdit_image').css('width');
		canvasWidth = parseInt(canvasWidth.substr(0,canvasWidth.length-2));
		var v = parseInt($('input#ZMSGraphic_extEdit_width').val())/canvasWidth;
		var params = {'action':ZMSGraphic_action,'x0:int':Math.round(v*c.x),'y0:int':Math.round(v*c.y),'x1:int':Math.round(v*c.x2),'y2:int':Math.round(v*c.y2)};
		for (var i in ZMSGraphic_params) {
			params[i] = ZMSGraphic_params[i];
		}
		$.get('manage_changeTempBlobjProperty',params,
				function(data){
					if (data.length==0) return;
					var result = eval('('+data+')');
					ZMSGraphic_extEdit_set(ZMSGraphic_elName,result['src'],result['filename'],result['width'],result['height']);
				});
	}
	// Resize
	else {
		var w  = $('input#ZMSGraphic_extEdit_width').val();
		var h = $('input#ZMSGraphic_extEdit_height').val();
		var v = Math.round(100*w/ZMSGraphic_act_width);
		if ( w != $('input#width_'+ZMSGraphic_elName).val() || h != $('input#height_'+ZMSGraphic_elName).val()) {
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
			$('span#dimensions_'+ZMSGraphic_elName).html(w+'x'+h+'px ['+v+'%]');
		}
	}
	// Close dialog.
	$ZMI.writeDebug("ZMSGraphic_extEdit_apply: Close dialog");
	zmiModal("hide");
	return false;
}

function changeJcropAvailability(available, cropping)
{
	if ($ZMSGraphic_cropapi != null) {
		$ZMSGraphic_cropapi.destroy();
	}
	if (available) {
		runPluginJcrop(function() {
			$ZMSGraphic_img.Jcrop({
					allowSelect	: false,
					setSelect: [ 0, 0, 25, 25 ],
					minSize		: [25, 25],
					maxSize		: [ZMSGraphic_act_width, ZMSGraphic_act_height],
					handles		: true,
					onChange	: ZMSGraphic_extEdit_changedSelection,
					onSelect	: ZMSGraphic_extEdit_changedSelection
				},function() {
					$ZMSGraphic_cropapi = this;
					$ZMSGraphic_cropapi.setOptions({ allowResize: true, allowMove: cropping});
					$ZMSGraphic_cropapi.focus();
				});
		});
	}
}

function ZMSGraphic_extEdit_clickedAction() {
	var temp_action = ZMSGraphic_action;
	ZMSGraphic_action = $(this).attr('id').toLowerCase().replace(/zmsgraphic_extedit_/g, '');
	if (ZMSGraphic_action == 'crop') {
		changeJcropAvailability(true,true);
	}
	else if (ZMSGraphic_action == 'preview') {
		if (confirm($(this).attr('title')+'?')) {
			ZMSGraphic_extEdit_apply();
		}
		ZMSGraphic_action = null;
	}
}

function ZMSGraphic_extEdit_changedSelection(c) {
	if (ZMSGraphic_action == 'crop') {
		ZMSGraphic_cropcoords = c;
	}
}