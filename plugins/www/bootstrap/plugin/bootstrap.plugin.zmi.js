function onFormSubmit() {
	return true;
}

$(function(){

	// Sitemap
	var $icon_sitemap = $('#zmi-header a i.icon-sitemap');
	if ($icon_sitemap.length > 0) {
		var $a = $icon_sitemap.closest("a");
		if (self.window.parent.frames.length > 1 && typeof self.window.parent != "undefined" && (self.window.parent.location+"").indexOf('dtpref_sitemap=1') > 0) {
			$a.attr('target','_parent');
		}
		else {
			$a.attr('href',$a.attr('href')+'&dtpref_sitemap=1');
		}
	}

	// Textarea:
	// single-line
	$('div.single-line').each(function() {
			var $textarea = $('textarea',this);
			$textarea.prop({rows:1,wrap:'off'});
			if ($(this).hasClass("zmi-nodes")) {
				$textarea.prop({title:getZMILangStr('ATTR_NODE')});
			}
			if ($("span.add-on",this).length==0) {
				$(this).addClass("input-append");
				$(this).append('<span class="add-on">...</span>');
				$('span.add-on',this).click(function() {
						var html = '';
						html = html
							+ '<div id="zmi-single-line-edit">'
								+ '<form class="form-horizontal" name="zmi-single-line-form">';
						if ($(this).closest("div.single-line").hasClass("zmi-nodes")) {
							html = html
									+ '<div class="controls">'
										+ '<div class="input-append">'
											+ '<input type="text" name="zmi-nodespicker-url-input" class="url-input">'
											+ '<span class="add-on" onclick="zmiBrowseObjs(\'zmi-single-line-form\',\'zmi-nodespicker-url-input\',getZMILang())">...</span>'
										+ '</div><!-- .input-append -->'
									+ '</div><!-- .controls -->';
						}
						html = html
									+ '<textarea style="width:98%" rows="10" wrap="off" style="overflow:scroll">' + $textarea.val() + '</textarea>'
								+ '</form>'
							+ '</div><!-- #zmi-single-line-edit -->';
						$('#zmi-single-line-edit').remove();
						$('body').append(html);
						$('#zmi-single-line-edit').dialog({
							modal:true,
							resizable:true,
							title:getZMILangStr('BTN_EDIT')+': '+$textarea.attr('title'),
							resize: function( event, ui ) {
								var $container = $('#zmi-single-line-edit');
								var $ta = $('textarea',$container);
								var taCoords = zmiGetCoords($ta[0],"relative");
								$ta.css({height:Math.max(20,$container.innerHeight()-taCoords.y-20)+'px'});
							},
							close: function( event, ui ) {
								$textarea.val($('#zmi-single-line-edit textarea').val());
							}});
					});
			}
		});

	// Accordion:
	// highlight default collapse item
	$("a.accordion-toggle").click(function(){this.blur()});
	$("i:first",$(".accordion-body.collapse").prev('.accordion-heading')).removeClass("icon-caret-down").addClass("icon-caret-right");
	$("i:first",$(".accordion-body.collapse.in").prev('.accordion-heading')).removeClass("icon-caret-right").addClass("icon-caret-down");
	$(".accordion-body.collapse").on("hide", function() {
			$("i:first",$(this).prev(".accordion-heading")).removeClass("icon-caret-down").addClass("icon-caret-right");
		}).on("show", function() {
			$("i:first",$(this).prev(".accordion-heading")).removeClass("icon-caret-right").addClass("icon-caret-down");
		});

	// Double-Clickable
	$('table.table-hover tbody tr')
		.dblclick( function(evt) {
			var href = null;
			if ((href==null || typeof href=="undefined") && $('a i.icon-edit',this).length > 0) {
				href = $('a i.icon-edit',this).parents("a:first").attr('href');
			}
			else if ((href==null || typeof href=="undefined")) {
				href = $('a[target=]',this).attr('href');
			}
			if (!(href==null || typeof href=="undefined")) {
				self.location.href = href;
			} 
		})
		.attr( "title", "Double-click to edit!");

	// Sortable
	$("ul.zmi-container.zmi-sortable").sortable({
		delay:500,
		forcePlaceholderSize:true,
		handle:'img.grippy',
		placeholder: "ui-state-highlight",
		revert: true,
		start: function(event, ui) {
				var el = $(".zmi-container .zmi-item");
				$(el).removeClass("highlight");
				self.zmiSortableRownum = false;
				var c = 1;
				$(".zmi-sortable > li").each(function() {
						if ($(this).attr("id") == ui.item.attr("id")) {
							self.zmiSortableRownum = c;
						}
						c++;
					});
			},
		stop: function(event, ui) {
				var pos = $(this).position();
				if (self.zmiSortableRownum) {
					var c = 1;
					$(".zmi-sortable > li").each(function() {
							if ($(this).attr("id") == ui.item.attr("id")) {
								if(self.zmiSortableRownum != c) {
									var id = ui.item.attr("id");
									var href = id+'/manage_moveObjToPos?lang='+getZMILang()+'&pos:int='+c+'&fmt=json';
									$.get(href,function(result){
											var message = eval('('+result+')');
											zmiShowMessage(pos,message,"alert-success");
										});
								}
							}
							c++;
						});
				}
				self.zmiSortableRownum = false;
			}
		});
	// Checkboxes
	$(".zmi-container .right input[name='ids:list']")
		.change(zmiActionButtonsRefresh)
		;
	// Action-Lists
	$(".zmi-container .zmi-item .zmi-action .btn.split-right")
		.each( function() {
				var $div = $(this).parent("div").siblings("div.zmi-manage-main-change:first");
				var title = $div.html();
				if (typeof title != "undefined") {
					title = title.replace(/<span([^<]*?)>(\r|\n|\t|\s)*?<\/span>/gi,'');
					$(this).attr("title",title).tooltip({html:true,placement:"right",delay:{show:0,hide:1000}});
				}
			})
		;
	$(".zmi-container .zmi-item .zmi-action")
		.focus( function(evt) { zmiActionOver(this,"focus"); })
		.mouseover( function(evt) {
				zmiActionOver(this,"mouseover");
				var $button = $('button.btn.split-right.dropdown-toggle i',this);
				$button.data("clazz",$button.prop("class")).removeClass($button.prop("class")).addClass("icon-chevron-down");
				$(this).parents(".accordion-body.collapse").css({overflow:"visible"});
			})
		.mouseout( function(evt) {
				zmiActionOut(this,"mouseout");
				var $button = $('button.btn.split-right.dropdown-toggle i',this);
				$button.removeClass($button.prop("class")).addClass($button.data("clazz"));
				$(this).parents(".accordion-body.collapse").css({overflow:"hidden"});
			})
		;
	// Inputs
	zmiInitInputFields($("body"));
	$(".zmi-image,.zmi-file").each(function() {
			$(this).addClass("span5");
			var elName = $(this).attr("id");
			elName = elName.substr(elName.lastIndexOf("-")+1);
			zmiRegisterBlob(elName);
			$("li#delete_btn_"+elName+" a",this).attr("href","javascript:zmiDelBlobBtnClick('"+elName+"')");
			$("li#undo_btn_"+elName+" a",this).attr("href","javascript:zmiUndoBlobBtnClick('"+elName+"')");
			zmiSwitchBlobButtons(elName);
		});
});

/**
 * Unlock form
 */
function zmiUnlockForm(form_id) {
	var $form = $('input[name="form_id"][value="'+form_id+'"]').parents("form");
	if ($('input[name="form_unlock"]',$form).length==0) {
		$form.append('<input type="hidden" name="form_unlock" value="1">');
	}
	$form.submit();
}

/**
 * Init input_fields
 */ 
function zmiInitInputFields(container) {
	$('form.form-horizontal',container)
		.submit(function() {
				var b = true;
				// Button
				if(self.btnClicked==getZMILangStr("BTN_BACK") ||
						self.btnClicked==getZMILangStr("BTN_CANCEL")) {
					return b;
				}
				// Multiple-Selects
				$('select[multiple="multiple"]',this).each(function() {
						var name = $(this).attr("name");
						var form = $(this).parents("form");
						if ($('select[name="zms_mms_src_'+name+'"]',form).length > 0) {
							$("option",this).prop("selected","selected");
						}
					});
				// Mandatory
				$(".zmi-input-error",this).removeClass("zmi-input-error");
				$(".control-group label.control-label.mandatory",this).each(function() {
						var $label = $(this);
						var labelText = $label.text().trim();
						var $controlGroup = $label.parents(".control-group");
						var $controls = $(".controls",$controlGroup);
						var $control = $('input:text,input:file,select:not([name^="zms_mms_src_"])',$controls);
						$label.attr("title","");
						$control.attr("title","");
						if ($control.length==1) {
							var isBlank = false;
							var nodeName = $control.prop("nodeName").toLowerCase();
							if (nodeName=="input") {
								isBlank = $control.val().trim().length==0;
							}
							else if (nodeName=="select") {
								isBlank = ($("option:selected",$control).length==0) 
									|| ($("option:selected",$control).length==1 && $("option:selected",$control).attr("value")=="");
							}
							if (isBlank) {
								$controlGroup.addClass("zmi-input-error");
								$label.attr("title",getZMILangStr("MSG_REQUIRED").replace(/%s/,labelText));
								$control.attr("title",getZMILangStr("MSG_REQUIRED").replace(/%s/,labelText));
								if (b) {
									$control.focus();
								}
								b = false;
							}
						}
					});
				// Lock
				if (b && $('input[name="form_unlock"]',this).length==0) {
					var result = $.ajax({
						url: 'ajaxGetNode',
						data:{lang:getZMILang()},
						datatype:'text',
						async: false
						}).responseText;
					var xmlDoc = $.parseXML(result);
					var $xml = $(xmlDoc);
					var change_dt = $('change_dt',$xml).text();
					var change_uid = $('change_uid',$xml).text();
					var form_id = $('input[name=form_id]').val();
					var form_dt = new Date(parseFloat(form_id)*1000);
					var checkLock = new Date(change_dt).getTime() > form_dt.getTime();
					if (checkLock) {
						if ($('#zmiDialog').length==0) {
							$('body').append('<div id="zmiDialog"></div>');
						}
						$('#zmiDialog').dialog({
								autoOpen: false,
								title: getZMILangStr('CAPTION_WARNING'),
								height: 'auto',
								width: 'auto'
							}).html(''
								+ '<div class="alert alert-error">'
									+ '<h4><i class="icon-warning-sign"></i> '+getZMILangStr('ACTION_MANAGE_CHANGEPROPERTIES')+'</h4>'
									+ '<div>'+change_dt+' '+getZMILangStr('BY')+' '+change_uid+'</div>'
								+ '</div>'
								+ '<div class="control-group">'
									+ '<button class="btn btn-primary" value="'+getZMILangStr('BTN_OVERWRITE')+'" onclick="zmiUnlockForm(\''+form_id+'\')">'+getZMILangStr('BTN_OVERWRITE')+'</button> '
									+ '<button class="btn" value="'+getZMILangStr('BTN_DISPLAY')+'" onclick="window.open(self.location.href);">'+getZMILangStr('BTN_DISPLAY')+'</button> '
								+ '</div>'
							).dialog('open');
					}
				}
				return b;
			})
		.each(function() {
			var context = this;
			$('input[type="submit"],button[type="submit"]',context)
				.click(function() {
						self.btnClicked = $(this).attr("value");
					});
			// Date-Picker
			pluginUIDatepicker('input.datepicker,input.datetimepicker',function(){
				$.datepicker.setDefaults( $.datepicker.regional[ pluginLanguage()]);
				$('input.datepicker',context).datepicker({
						showWeek: true
					});
				$('input.datetimepicker',context).datepicker({
						constrainInput: false,
						showWeek: true,
						beforeShow: function(input, inst) {
								var v = $(input).val();
								var e = '';
								var i = v.indexOf(' ');
								if ( i > 0) {
									e = v.substr(i+1);
									v = v.substr(0,i);
								}
								$(inst).data("inputfield",input);
								$(inst).data("extra",e);
							},
						onClose: function(dateText, inst) {
								if (dateText) {
									var input = $(inst).data("inputfield");
									var e = $(inst).data("extra");
									if (e && !dateText.endsWith(" "+e)) {
										$(input).val(dateText+" "+e);
									}
								}
							}
					});
			});
			$("input.datepicker,input.datetimepicker",this).each(function() {
					$($(this).parents("span")[0]).addClass("input-prepend");
					$(this).before('<span class="add-on"><i class="icon-calendar"></i></span>');
				});
			if ($("div.zmi-richtext",this).length > 0) {
				$(this).submit(function() {
						zmiRichtextOnSubmitEventHandler();
					});
			}
		});
}

/**
 * Show message
 */
function zmiShowMessage(pos, message, context) {
	$(".alert").remove();
	var html = ''
		+ '<div class="alert'+(typeof context=='undefined'?'':' '+context)+'" style="position:absolute;left:'+pos.left+'px;top:'+pos.top+'px;">'
			+ '<button type="button" class="close" data-dismiss="alert">&times;</button>'
			+ message
		+ '</div>';
	$('body').append(html);
	window.setTimeout('$(".alert").hide("slow")',2000);
}

/**
 * Un-/select checkboxes.
 * @see jquery.plugin.zmi.js
 */
function selectCheckboxes(fm, v) {
	if (typeof v == 'undefined') {
		v = !$(':checkbox:not([name~=active])',fm).prop('checked');
	}
	$(':checkbox:not([name~=active])',fm).prop('checked',v).change();
}

/**
 * @see jquery.plugin.zmi.js
 */
function zmiWriteDebug(s) {
	var $div = $("div#zmi-debug");
	if ($div.css("display")!="none") {
		$div.html("["+(new Date())+"] "+s+'<br/>'+$div.html());
	}
}


// #############################################################################
// ### ZMI Pathcropping
// #############################################################################

/**
 * @see jquery.plugin.zmi.js
 */
function zmiRelativateUrl(path, url) {
	var protocol = self.location.href;
	protocol = protocol.substr(0,protocol.indexOf(":")+3);
	var server_url = self.location.href;
	server_url = server_url.substr(protocol.length);
	server_url = protocol + server_url.substr(0,server_url.indexOf("/"));
	var currntPath = null;
	if (path.indexOf(server_url)==0) {
		currntPath = path.substr(server_url.length+1);
	}
	else if (path.indexOf('/')==0) {
		currntPath = path.substr(1);
	}
	var targetPath = null;
	if (url.indexOf(server_url)==0) {
		targetPath = url.substr(server_url.length+1);
	}
	else if (url.indexOf('/')==0) {
		targetPath = url.substr(1);
	}
	if (currntPath == null || targetPath == null) {
		return url;
	}
	while ( currntPath.length > 0 && targetPath.length > 0) {
		var i = currntPath.indexOf( '/');
		var j = targetPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
		}
		if ( j < 0) {
			targetElmnt = targetPath;
		}
		else {
			targetElmnt = targetPath.substring( 0, j);
		}
		if ( currntElmnt != targetElmnt) {
			break;
		}
		if ( i < 0) {
			currntPath = '';
		}
		else {
			currntPath = currntPath.substring( i + 1);
		}
		if ( j < 0) {
			targetPath = '';
		}
		else {
			targetPath = targetPath.substring( j + 1);
		}
	}
	while ( currntPath.length > 0) {
		var i = currntPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
			currntPath = '';
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
			currntPath = currntPath.substring( i + 1);
		}
		targetPath = '../' + targetPath;
	}
	url = './' + targetPath;
	return url;
}

/**
 * @see jquery.plugin.zmi.js
 */
function zmiRelativateUrls(s,page_url) {
	var splitTags = ['<a href="','<img src="'];
	for ( var h = 0; h < splitTags.length; h++) {
	var splitTag = splitTags[h];
		var vSplit = s.split(splitTag);
		var v = vSplit[0];
		for ( var i = 1; i < vSplit.length; i++) {
			var j = vSplit[i].indexOf('"');
			var url = vSplit[i].substring(0,j);
			if (url.indexOf('./')<0) {
				url = zmiRelativateUrl(page_url,url);
			}
			v += splitTag + url + vSplit[i].substring(j);
		}
		s = v;
	}
	return s;
}

/**
 * Open link in iframe (jQuery UI Dialog).
 */
function zmiIframe(href, data, opt) {
	if ($('#zmiIframe').length==0) {
		$('body').append('<div id="zmiIframe"></div>');
	}
	// Debug
	var url = href + "?";
	for (var k in data) {
		url += k + "=" + data[k] + "&";
	}
	// Iframe
	if (typeof opt['iframe'] != 'undefined') {
		$('#zmiIframe').append('<iframe src="' + url + '" width="' + opt['width'] + '" height="' + opt['height'] + '" frameBorder="0"></iframe>');
		opt["modal"] = true;
		opt["height"] = "auto";
		opt["width"] = "auto";
		$('#zmiIframe').dialog(opt);
	}
	else {
		$.get( href, data, function(result) {
				var $result = $(result);
				if ($("div#system_msg",$result).length>0) {
					var manage_tabs_message = $("div#system_msg",$result).text();
					manage_tabs_message = manage_tabs_message.substr(0,manage_tabs_message.lastIndexOf("("));
					var href = self.location.href;
					href = href.substr(0,href.indexOf("?"))+"?lang="+getZMILang()+"&manage_tabs_message="+manage_tabs_message;
					self.location.href = href;
				}
				else {
					opt["modal"] = true;
					opt["height"] = "auto";
					opt["width"] = "auto";
					$('#zmiIframe').html(result);
					var title = $('#zmiIframe div.zmi').attr("title");
					if (typeof title != "undefined" && title) {
						opt["title"] = title;
					}
					$('#zmiIframe').dialog(opt);
				}
			});
	}
}

// #############################################################################
// ### ZMI Action-Lists
// #############################################################################

/**
 * Populate action-list.
 *
 * @param el
 */
function zmiActionOver(el, evt) {
	$("button.split-left",el).css({visibility:"visible"});
	// Exit.
	if($("button.split-left",el).length==0 || $("ul.dropdown-menu",el).length>0) return;
	// Set wait-cursor.
	$(document.body).css( "cursor", "wait");
	// Build action and params.
	var context_id = $(el).parents("li.zmi-item").attr("id");
	var action = self.location.href;
	action = action.substr(0,action.lastIndexOf("/"));
	action += "/manage_ajaxZMIActions";
	var params = {};
	params['lang'] = getZMILang();
	params['context_id'] = typeof context_id == "undefined" || context_id == ""?"":context_id;
	// JQuery.AJAX.get
	$.get( action, params, function(data) {
		// Reset wait-cursor.
		$(document.body).css( "cursor", "auto");
		// Exit.
		if($("ul.dropdown-menu",el).length>0) return;
		// Get object-id.
		var value = eval('('+data+')');
		var id = value['id'].replace(/\./,"_");
		var actions = value['actions'];
		$(el).append('<ul class="dropdown-menu"></ul>');
		var $baseul = $("ul.dropdown-menu",el);
		var $ul = $baseul;
		var startsWithSubmenu = actions.length > 1 && actions[1][0].indexOf("-----") == 0 && actions[1][0].lastIndexOf("-----") > 0;
		if (startsWithSubmenu) {
			var html = '';
			var opticon = '';
			if (actions[1].length > 2) {
				if (actions[1][2].indexOf('<i')==0) {
					opticon = actions[1][2];
				}
				else {
					opticon = '<i class="' + actions[1][2] +'"></i>';
				}
			}
			var optlabel = actions[1][0];
			optlabel = optlabel.substr("-----".length);
			optlabel = optlabel.substr(0,optlabel.lastIndexOf("-----"));
			optlabel = optlabel.trim();
			$("button.split-left",el).html(opticon+optlabel).click(function(){
					return false;
				});
		}
		else {
			// Edit action
			$("button.split-left",el).click(function() {
					var context_id = $(this).parents("li.zmi-item").attr("id");
					var action = self.location.href;
					action = action.substr(0,action.lastIndexOf("/"));
					action += typeof context_id == "undefined" || context_id == ""?"/manage_properties":"/"+context_id+"/manage_main";
					action += "?lang=" + getZMILang();
					self.location.href = action;
					return false;
				});
			//
			$ul.append('<li><a href="javascript:zmiToggleSelectionButtonClick($(\'li.zmi-item' + (id==''?':first':'#'+id) + '\'))"><i class="icon-check"></i>'+getZMILangStr('BTN_SLCTALL')+'/'+getZMILangStr('BTN_SLCTNONE')+'</a></li>');
		}
		for (var i = 2; i < actions.length; i++) {
			var optlabel = actions[i][0];
			var optvalue = actions[i][1];
			if (optlabel.indexOf("-----") == 0 && optlabel.lastIndexOf("-----") > 0) {
				var opticon = '';
				if (actions[i].length > 2) {
					if (actions[i][2].indexOf('<i')==0) {
						opticon = actions[i][2];
					}
					else {
						opticon = '<i class="' + actions[i][2] +'"></i>';
					}
				}
				optlabel = optlabel.substr("-----".length);
				optlabel = optlabel.substr(0,optlabel.lastIndexOf("-----"));
				optlabel = optlabel.trim();
				var html = '';
				html += '<li class="dropdown-submenu">';
				html += '<a tabindex="-1" href="#">';
				html += opticon + optlabel;
				html += '</a>';
				html += '<ul class="dropdown-menu">';
				html += '</ul><!-- .dropdown-menu -->';
				html += '</li><!-- .dropdown-submenu -->';
				$baseul.append(html);
				var $ul = $("ul.dropdown-menu:last",$baseul);
			}
			else {
				var opticon = '';
				if (actions[i].length > 2) {
					if (actions[i][2].indexOf('<i')==0) {
						opticon = actions[i][2];
					}
					else {
						opticon = '<i class="' + actions[i][2] +'"></i>';
					}
				}
				else if (optvalue.indexOf('manage_del') >= 0 || optvalue.indexOf('manage_erase') >= 0) {
					opticon = '<i class="icon-trash"></i>';
				}
				else if (optvalue.indexOf('manage_main') >= 0) {
					opticon = '<i class="icon-edit"></i>';
				}
				else if (optvalue.indexOf('manage_undo') >= 0) {
					opticon = '<i class="icon-undo"></i>';
				}
				else if (optvalue.indexOf('manage_cut') >= 0) {
					opticon = '<i class="icon-cut"></i>';
				}
				else if (optvalue.indexOf('manage_copy') >= 0) {
					opticon = '<i class="icon-copy"></i>';
				}
				else if (optvalue.indexOf('manage_paste') >= 0) {
					opticon = '<i class="icon-paste"></i>';
				}
				else if (optvalue.indexOf('manage_moveObjUp') >= 0) {
					opticon = '<i class=" icon-sort-up"></i>';
				}
				else if (optvalue.indexOf('manage_moveObjDown') >= 0) {
					opticon = '<i class=" icon-sort-down"></i>';
				}
				var html = '';
				html += '<li><a href="javascript:zmiActionExecute($(\'li.zmi-item' + (id==''?':first':'#'+id) + '\'),\'' + optlabel + '\',\'' + optvalue + '\')">';
				html += opticon + optlabel;
				html += '</a></li>';
				$ul.append(html);
			}
		}
	});
}

/**
 * Populate action-list.
 *
 * @param el
 */
function zmiActionOut(el, evt) {
	$("button.split-left",el).css({visibility:"hidden"});
}


function zmiActionExecute(sender, label, target) {
	var $el = $(".zmi-action",sender);
	var $fm = $el.parents("form");
	$("input[name='custom']").val(label);
	$("input[name='_sort_id:int']").val($(".zmi-sort-id",$el).text());
	if (target.toLowerCase().indexOf('manage_addproduct/')==0 && target.toLowerCase().indexOf('form')>0) {
		// Parameters
		var inputs = $("input:hidden",$fm);
		var data = {};
		for ( var i = 0; i < inputs.length; i++) {
			var $input = $(inputs[i]);
			var id = $input.attr("id");
			if (jQuery.inArray(id,['form_id','id_prefix','_sort_id','custom','lang','preview'])>=0) {
				data[$input.attr('name')] = $input.val();
			}
		}
		var id_prefix = $(sender).attr("id");
		if (typeof id_prefix != 'undefined' && id_prefix != '') {
			data['id_prefix'] = id_prefix.replace(/\d/gi,'');
		}
		$('<li id="manage_addProduct" class="zmi-item zmi-selected"><div class="center"><div class="zmiRenderShort">' + getZMILangStr('BTN_INSERT')+': '+label + '</div></div></li>').insertAfter($el.parents(".zmi-item"));
		// Show add-dialog.
		zmiIframe(target,data,{
				title:getZMILangStr('BTN_INSERT')+': '+label,
				open:function(event,ui) {
					zmiInitInputFields($('#zmiIframe'));
				},
				close:function(event,ui) {
					$('#manage_addProduct').remove();
				}
		});
	}
	else {
		var $div = $el.parents("div.right");
		$("input[name='ids:list']",$div).prop("checked",true);
		zmiActionButtonsRefresh(sender);
		if (zmiConfirmAction($fm,target,label)) {
			$fm.attr("action",target);
			$fm.attr("method","POST");
			$fm.submit();
		}
		else {
			$("input[name='ids:list']",$div).prop("checked",false);
			zmiActionButtonsRefresh(sender);
		}
	}
}

/**
 * @param sender
 * @param evt
 */
function zmiActionButtonsRefresh(sender,evt) {
	$(".zmi-selectable").each(function() {
			if ($("input[name='ids:list']:checked",this).length > 0) {
				$(this).addClass("zmi-selected");
			}
			else {
				$(this).removeClass("zmi-selected");
			}
		});
}

// ############################################################################
// ### Url-Input
// ############################################################################

$(function() {
	$("input.url-input").each(function() {
			var enabled = true; // @TODO
			var fmName = $(this).parents("form").attr("name");
			var elName = $(this).attr("name");
			$(this).closest('span.url-input').addClass("input-append");
			$(this).next('div.zmi-icon').remove();
			$(this).after(''
					+ '<span class="add-on ui-helper-clickable" onclick="return zmiBrowseObjs(\'' + fmName + '\',\'' + elName + '\',getZMILang())">'
						+ '<i class="icon-link"></i>'
					+ '</span>'
				);
		});
});

/**
 * zmiBrowseObjs
 */
function zmiBrowseObjs(fmName, elName, lang) {
	var elValue = '';
	if (fmName.length>0 && elName.length>0) {
		elValue = $('form[name='+fmName+'] input[name='+elName+']').val();
	}
	var title = getZMILangStr('CAPTION_CHOOSEOBJ');
	var href = "manage_browse_iframe";
	href += '?lang='+lang;
	href += '&fmName='+fmName;
	href += '&elName='+elName;
	href += '&elValue='+escape(elValue);
	if ( selectedText) {
		href += '&selectedText=' + escape( selectedText);
	}
	if ($('#zmiDialog').length==0) {
		$('body').append('<div id="zmiDialog"></div>');
	}
	$('#zmiDialog').dialog({
			autoOpen: false,
			title: title,
			height: 'auto',
			width: 'auto'
		}).html('<iframe src="'+href+'" style="width:100%; min-width:'+getZMIConfProperty('zmiBrowseObjs.minWidth',200)+'px; height:100%; min-height: '+getZMIConfProperty('zmiBrowseObjs.minHeight',320)+'px; border:0;"></iframe>').dialog('open');
	return false;
}

function zmiBrowseObjsApplyUrlValue(fmName, elName, elValue) {
	$('form[name='+fmName+'] input[name='+elName+']').val(elValue);
}

function zmiDialogClose(id) {
	$('#'+id).dialog('close');
	$('body').remove('#'+id);
}

// ############################################################################
// ### Record-Sets
// ############################################################################

function zmiRecordSetMoveRow(el, qIndex) {
	var $form = $($(el).parents('form:first'));
	$form.append('<input type="hidden" name="pos:int" value="' + (qIndex+1) + '">');
	$form.append('<input type="hidden" name="newpos:int" value="' + $(el).val() + '">');
	$('input[name="action"]',$form).val('move');
	$form.submit();
}

function zmiRecordSetDeleteRow(fmName, qIndex) {
	var $form = $('form[name="'+fmName+'"]');
	if (typeof qIndex != "undefined") {
		var $input = $('input[value="'+qIndex+'"]',$form);
		$input.prop('checked',true).change();
	}
	if (confirm(getZMILangStr('MSG_CONFIRM_DELOBJ'))) {
		$('input[name="action"]',$form).val('delete');
		$form.submit();
	}
	else if (typeof qIndex != "undefined") {
		var $input = $('input[value="'+qIndex+'"]',$form);
		$input.prop('checked',false).change();
	}
	return false;
}

$(function() {
	// Sortable
	var fixHelper = function(e, ui) { // Return a helper with preserved width of cells
		ui.children().each(function() {
			$(this).width($(this).width());
		});
		return ui;
	};
	$("table.zmi-sortable tbody").sortable({
		delay:500,
		forcePlaceholderSize:true,
		handle:'img.grippy',
		helper:fixHelper,
		placeholder: "ui-state-highlight",
		revert: true,
		start: function(event, ui) {
				self.zmiSortableRownum = false;
				var c = 1;
				$("table.zmi-sortable > tbody > tr").each(function() {
						if ($(this).attr("id") == ui.item.attr("id")) {
							self.zmiSortableRownum = c;
						}
						c++;
					});
			},
		stop: function(event, ui) {
				var pos = $(this).position();
				if (self.zmiSortableRownum) {
					var c = 1;
					$("table.zmi-sortable > tbody > tr").each(function() {
							if ($(this).attr("id") == ui.item.attr("id")) {
								if(self.zmiSortableRownum != c) {
									var id = ui.item.attr("id");
									var pos = parseInt(id.substr(id.indexOf("_")+1))+1;
									var href = 'manage_changeRecordSet?lang='+getZMILang()+'&amp;action=move&amp;btn=&amp;pos:int='+pos+'&amp;newpos:int='+c;
									self.location.href = href;
								}
							}
							c++;
						});
				}
				self.zmiSortableRownum = false;
			}
		});
	});

// ############################################################################
// ### zmiDisableInteractions
// ############################################################################

var zmiDisableInteractionsAllowed = true;

$(function() {
	// preload image
	new Image().src = "/misc_/zms/loading_16x16.gif";
	// Disable
	$(window).unload(function() {zmiDisableInteractions(true)});
});

function zmiEnableInteractions(b) {
	// Set wait-cursor.
	$(document.body).css( 'cursor', 'auto');
	// Create semi-transparent overlay
	$("div#overlay").remove();
	// Create progress-box.
	$("div#progressbox").remove();
}
  
function zmiDisableInteractions(b) {
	if (!b || !zmiDisableInteractionsAllowed) {
		zmiDisableInteractionsAllowed = true;
		return;
	}
	// Set wait-cursor.
	$(document.body).css( 'cursor', 'wait');
	// Create semi-transparent overlay
	$(document.body).append('<div id="zmi-overlay"></div>');
	// Create progress-box.
	$(document.body).append('<div id="zmi-progressbox">'
			+ '<img src="/misc_/zms/loading_16x16.gif" border="0" align="absmiddle"> ' + getZMILangStr('MSG_LOADING')
		+ '</div>');
	var dims = getInnerDimensions();
	var $div = $("#zmi-progressbox");
	$div.css({top:(dims.height-$div.prop('offsetHeight'))/2,left:(dims.width-$div.prop('offsetWidth'))/2});
}