/*
 * Defaults
 */

String.prototype.removeWhiteSpaces = function() {return(this.replace(/\s+/g,""));};
String.prototype.leftTrim = function() {return(this.replace(/^\s+/,""));};
String.prototype.rightTrim = function() {return(this.replace(/\s+$/,""));};
String.prototype.basicTrim = function() {return(this.replace(/\s+$/,"").replace(/^\s+/,""));};
String.prototype.superTrim = function() {return(this.replace(/\s+/g," ").replace(/\s+$/,"").replace(/^\s+/,""));};
String.prototype.startsWith = function(str) {return (this.match("^"+str)==str)};
String.prototype.endsWith = function(str) {return (this.match(str+"$")==str)};
Array.prototype.indexOf = function(obj) {var i,idx=-1;for(i=0;i<this.length;i++){if(this[i]==obj){idx=i;break;}}return idx;};
Array.prototype.lastIndexOf = function(obj) {this.reverse();var i,idx=-1;for(i=0;i<this.length;i++){if(this[i]==obj){idx=(this.length-1-i);break;}}this.reverse();return idx;};
Array.prototype.contains = function(obj) {var i,listed=false;for(i=0;i<this.length;i++){if(this[i]==obj){listed=true;break;}}return listed;};

/*
 * Plugins
 */
function pluginLanguage() {
	return getZMILangStr('LOCALE',{'nocache':""+new Date()});
}

function pluginUIDatepicker(s, c) {
	var lang = pluginLanguage();
	$.plugin('ui_datepicker',{
		files: [
				'/++resource++zms_/jquery/ui/i18n/jquery.ui.datepicker-'+lang+'.js'
		]});
	$.plugin('ui_datepicker').get(s,c);
}

var zmiParams = {};
$(function(){
	var href = self.location.href;
	// Parse params (?) and pseudo-params (#).
	var delimiter_list = ['?','#'];
	for (var h = 0; h < delimiter_list.length; h++) {
		var delimiter = delimiter_list[h];
		var i = href.indexOf(delimiter);
		if (i > 0) {
			var query_string = href.substr(i+1);
			if (h < delimiter_list.length-1) {
				i = query_string.indexOf(delimiter_list[h+1]);
				if (i > 0) {
					query_string = query_string.substr(0,i);
				}
			}
			var l = query_string.split('&');
			for ( var j = 0; j < l.length; j++) {
				i = l[j].indexOf('=');
				if (i < 0) {
					break;
				}
				if (typeof zmiParams[l[j].substr(0,i)] == "undefined") {
					zmiParams[l[j].substr(0,i)] = unescape(l[j].substr(i+1));
				}
			}
		}
	}
	// Content-Editable ////////////////////////////////////////////////////////
	if (self.location.href.indexOf('/manage')>0 || self.location.href.indexOf('preview=preview')>0) {
		$('.contentEditable,.zmiRenderShort')
			.mouseover( function(evt) {
				$(this).addClass('preview').addClass('highlight'); 
			})
			.mouseout( function(evt) {
				$(this).removeClass('preview').removeClass('highlight'); 
			})
			.dblclick( function(evt) {
				evt.stopPropagation();
				var href = ""+self.location.href;
				if (href.indexOf('?')>0) {
					href = href.substr(0,href.indexOf('?'));
				}
				if (href.lastIndexOf('/')>0) {
					href = href.substr(0,href.lastIndexOf('/'));
				}
				var lang = null;
				var parents = $(this).parents('.contentEditable');
				for ( var i = 0; i <= parents.length; i++) {
					var pid;
					if ( i==parents.length) {
						pid = $(this).attr('id');
					}
					else {
						pid = $(parents[parents.length-i-1]).attr('id');
					}
					if (pid.length > 0) {
						if (lang == null) {
							lang = pid.substr(pid.lastIndexOf('_')+1);
						}
						pid = pid.substr(pid.indexOf('_')+1);
						if(pid.substr(pid.length-('_'+lang).length)==('_'+lang)) {
							pid = pid.substr(0,pid.length-('_'+lang).length);
						}
						if (!href.endsWith('/'+pid)) {
							href += '/'+pid;
						}
					}
				}
				if (self.location.href.indexOf(href+'/manage_main')==0) {
					href += '/manage_properties';
				}
				else {
					href += '/manage_main';
				}
				if (self.location.href.indexOf('/manage_translate')>0) {
					href += '_iframe';
					href += '?lang='+lang;
					href += '&ZMS_NO_BODY=1';
					zmiIframe(href,{},{});
				}
				else if (self.location.href.indexOf('/manage')>0) {
					href += '?lang='+lang;
					self.location.href = href;
				}
				else {
					href += '_iframe';
					href += '?lang='+lang;
					showFancybox({
						'autoDimensions':false,
						'hideOnOverlayClick':false,
						'href':href,
						'transitionIn':'fade',
						'transitionOut':'fade',
						'type':'iframe',
						'width':819
					});
				}
			})
		.attr( "title", "Double-click to edit!");
	}

	// ZMS plugins
	if (typeof zmiParams['ZMS_HIGHLIGHT'] != 'undefined' && typeof zmiParams[zmiParams['ZMS_HIGHLIGHT']] != 'undefined') {
		$.plugin('zmi_highlight',{
			files: ['/++resource++zms_/jquery/plugin/jquery.plugin.zmi_highlight.js']
			});
		$.plugin('zmi_highlight').get('body',function(){});
	}

	// Accordion:
	// highlight default collapse item
	$("a.accordion-toggle").click(function(){this.blur()});
	$("i",$(".accordion-body.collapse").prev('.accordion-heading')).removeClass("icon-caret-down").addClass("icon-caret-right");
	$("i",$(".accordion-body.collapse.in").prev('.accordion-heading')).removeClass("icon-caret-right").addClass("icon-caret-down");
	$(".accordion-body.collapse").on("hide", function() {
			$("i",$(this).prev(".accordion-heading")).removeClass("icon-caret-down").addClass("icon-caret-right");
		}).on("show", function() {
			$("i",$(this).prev(".accordion-heading")).removeClass("icon-caret-right").addClass("icon-caret-down");
		});

		// Form
	$("form.form-horizontal").each(function() {
			var context = this;
			pluginUIDatepicker('input.datepicker,input.datetimepicker',function(){
				// Date-Picker
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
	// Action-Lists
	$(".zmi-container.zmi-sortable").sortable({
		forcePlaceholderSize:true,
		placeholder: "ui-state-highlight",
		revert: true,
		start: function(event, ui) {
				$("#zmi-action-btn-group").remove();
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
	$(".zmi-container.zmi-sortable").disableSelection();
	$(".zmi-container .right input[name='ids:list']").change(zmiActionButtonsRefresh);
	$("div.btn-group.zmi-action")
		.focus( function(evt) { zmiActionOver(this,"focus"); })
		.mouseover( function(evt) { zmiActionOver(this,"mouseover"); })
		.mouseout( function(evt) { zmiActionOut(this,"mouseout"); })
		;
	// Inputs
	$(".zmi-image,.zmi-file").each(function() {
			$(this).addClass("span5");
			var elName = $(this).attr("id");
			elName = elName.substr(elName.lastIndexOf("-")+1);
			zmiRegisterBlob(elName);
			$("li#delete_btn_"+elName+" a",this).attr("href","javascript:zmiDelBlobBtnClick('"+elName+"')");
			$("li#undo_btn_"+elName+" a",this).attr("href","javascript:zmiUndoBlobBtnClick('"+elName+"')");
			zmiSwitchBlobButtons(elName);
			$(".zmi-image-preview img",this)
					.attr({title:getZMILangStr('ATTR_IMAGE')+': '+getZMILangStr('BTN_EDIT')})
					.click(function() {
							var html = '<img src="' + $(this).attr("src") + '"/>';
							zmiIframe(html,{},{title:$(this).attr("title")});
						})
					;
		});
});

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
	$(':checkbox:not([name~=active])',fm).prop('checked',v)
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
	if ($("#myModal").length==0) {
		var html = ''
			+ '<div class="modal" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
				+ '<div class="modal-header">'
					+ '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
					+ '<h3 id="myModalLabel"></h3>'
				+ '</div>'
			+ '</div>';
		$('body').append(html);
	}
	else {
		$("#myModal .modal-body, #myModal .modal-footer").remove();
	}
	if (typeof opt["title"] != "undefined") {
		$("#myModal #myModalLabel").html(opt["title"]);
	}
	if (href.indexOf("<")==0) {
		var html = ''
				+ '<div class="modal-body">'
					+ href
				+ '</div>'
				+ '<div class="modal-footer">'
					+ '<button class="btn btn-primary" data-dismiss="modal" aria-hidden="true" onclick="$(\'#myModal\').modal(\'hide\')">' + getZMILangStr('BTN_CLOSE') + '</button>'
				+ '</div>';
		$("#myModal").append(html);
		$("#myModal").modal();
	}
	else {
		var s = href + "?";
		for (var k in data) {
			s += k + "=" + data[k] + "&";
		}
		s = s.substr(0, s.length);
		//confirm(s);
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
					$("#myModal").append(result);
					$("#myModal").modal();
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
	$(".split-left",el).css({visibility:"visible"});
	// Populate action-list.
	if($("ul.dropdown-menu",el).length==0) {
		// Set wait-cursor.
		$(document.body).css( "cursor", "wait");
		// Edit action
		$("button.split-left",el).click(function() {
				var btn_group = $(this).parents("div.btn-group.zmi-action");
				var dropdown_menu = $("ul.dropdown-menu",btn_group);
				window.setTimeout($("li:eq(1) a",dropdown_menu).attr("href"),1);
			});
		// Build action and params.
		var action = self.location.href;
		action = action.substr(0,action.lastIndexOf("/"));
		action += "/manage_ajaxZMIActions";
		var params = {};
		params['lang'] = getZMILang();
		params['context_id'] = typeof $(el).parents("li.zmi-item").attr("id") == "undefined"?"":$(el).parents("li.zmi-item").attr("id");
		// JQuery.AJAX.get
		$.get( action, params, function(data) {
			// Reset wait-cursor.
			$(document.body).css( "cursor", "auto");
			// Get object-id.
			var value = eval('('+data+')');
			var id = value['id'].replace(/\./,"_");
			var actions = value['actions'];
			$(el).append('<ul class="dropdown-menu"></ul>');
			var $baseul = $("ul.dropdown-menu",el);
			var $ul = $baseul;
			$ul.append('<li><a href="javascript:zmiToggleSelectionButtonClick($(\'li.zmi-item' + (id==''?':first':'#'+id) + '\'))"><i class="icon-check"></i>'+getZMILangStr('BTN_SLCTALL')+'/'+getZMILangStr('BTN_SLCTNONE')+'</a></li>');
			for (var i = 1; i < actions.length; i++) {
				var optlabel = actions[i][0];
				var optvalue = actions[i][1];
				if (optlabel.indexOf("-----")==0 && optlabel.lastIndexOf("-----")>0) {
					var opticon = '';
					if (actions[i].length > 2) {
						opticon = '<i class="' + actions[i][2] +'"></i>';
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
						opticon = '<img src="' + actions[i][2] +'"/>';
					}
					else if (optvalue.indexOf('manage_del') >= 0 || optvalue.indexOf('manage_erase') >= 0) {
						opticon = '<i class="icon-trash"></i>';
					}
					else if (optvalue.indexOf('manage_main') >= 0) {
						opticon = '<i class="icon-edit"></i>';
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
}

function zmiActionOut(el, evt) {
	$(".split-left",el).css({visibility:"hidden"});
}

function zmiActionExecute(sender, label, target) {
	var $el = $(".zmi-action",sender);
	var $fm = $el.parents("form");
	$("input[name=custom]").val(label);
	$("input[name=_sort_id]").val($(".zmi-sort-id",$el).text());
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
		// Show add-dialog.
		zmiIframe(target,data,{
				title:getZMILangStr('BTN_INSERT'),
				close:function(event,ui) {
					// @todo
					$('tr#tr_manage_addProduct').remove();
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
	var fm = $(sender).parents('form');
	$("li.zmi-item").each(function() {
			if ($("input[name='ids:list']:checked",this).length > 0) {
				$(this).addClass("zmi-selected");
			}
			else {
				$(this).removeClass("zmi-selected");
			}
		});
}
