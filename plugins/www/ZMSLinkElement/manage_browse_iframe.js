/**
 * Select object.
 */
function selectObject(physical_path,anchor,is_page,titlealt) {
	$ZMI.writeDebug('BO selectObject: physical_path='+physical_path+',anchor='+anchor);
	var fm;
	var url = physical_path;
	var title = titlealt;
	if (typeof zmiParams['fmName'] != 'undefined' && zmiParams['fmName'] != ''
			&& typeof zmiParams['elName'] != 'undefined' && zmiParams['elName'] != '') {
		fm = self.window.parent.document.forms[zmiParams['fmName']];
	}
	if ( fm) {
		var path = getInternalUrl(url);
		self.window.parent.zmiBrowseObjsApplyUrlValue(zmiParams['fmName'],zmiParams['elName'],path);
	}
	else {
		url = $ZMI.relativateUrl(url,anchor);
		self.window.parent.selectObject(url,title);
	}
	self.window.parent.zmiModal("hide");
	$ZMI.writeDebug('EO selectObject: url='+url+',title='+title);
}

/**
 * Select URL.
 */
function selectUrl(url) {
	$ZMI.writeDebug('BO selectUrl: url='+url);
	var fm;
	var title = '';
	if (typeof zmiParams['fmName'] != 'undefined' && zmiParams['fmName'] != ''
			&& typeof zmiParams['elName'] != 'undefined' && zmiParams['elName'] != '') {
		fm = self.window.parent.document.forms[zmiParams['fmName']];
	}
	if ( fm) {
		self.window.parent.zmiBrowseObjsApplyUrlValue(zmiParams['fmName'],zmiParams['elName'],url);
	}
	else {
		self.window.parent.selectObject(url,title);
	}
	self.window.parent.zmiModal("hide");
	$ZMI.writeDebug('EO selectUrl');
}

/**
 * Returns internal url in {$...}-notation.
 */
function getInternalUrl(physical_path) {
	$ZMI.writeDebug('BO getInternalUrl: physical_path='+physical_path);
	var content = "/content";
	var currntPath = $ZMI.getPhysicalPath();
	var currntHome = currntPath.substr(1,currntPath.indexOf(content)-1);
	currntPath = currntPath.substr(currntPath.indexOf(content)+content.length+1);
	var targetPath = physical_path;
	var targetHome = targetPath.substr(1,targetPath.indexOf(content)-1);
	targetPath = targetPath.substr(targetPath.indexOf(content)+content.length+1);
	while (true) {
		var cid = currntHome.indexOf('/')>0?currntHome.substr(0,currntHome.indexOf('/')):currntHome;
		var tid = targetHome.indexOf('/')>0?targetHome.substr(0,targetHome.indexOf('/')):targetHome;
		if (cid.length == 0 || tid.length == 0 || cid != tid) {
			break;
		}
		currntHome = currntHome.substr(cid.length+1);
		targetHome = targetHome.substr(tid.length+1);
	}
	var path = targetPath;
	if ( currntHome != targetHome) {
		path = targetHome + "@" + path;
	}
	path = "{$" + path + "}";
	$ZMI.writeDebug('EO getInternalUrl: path='+path);
	return path;
}

/**
 * Click toggle.
 */
function zmiToggleClick(toggle, callback) {
	$ZMI.writeDebug('zmiToggleClick: '+toggle+'['+($(toggle).length)+'];callback='+(typeof callback));
	var $container = $(toggle).parents("ol:first");
	var checked = $('input:radio:checked').val(); 
	$container.children(".zmi-page").remove();
	if ($(toggle).hasClass($ZMI.icon_clazz("icon-caret-right"))) {
		$(toggle).removeClass($ZMI.icon_clazz("icon-caret-right")).addClass($ZMI.icon_clazz("icon-caret-down")).attr({title:'-'});
		var href = '';
		var homeId = null;
		$(toggle).parents(".zmi-page").each(function(){
				var dataId = $(this).attr("data-id");
				var dataHomeId = $(this).attr("data-home-id");
				if (homeId == null) {
					homeId = dataHomeId;
				}
				if (homeId != dataHomeId) {
					href = '/'+dataHomeId+'/'+homeId+href;
					homeId = dataHomeId;
				}
				else {
					href = '/'+dataId+href;
				}
			});
		if (!href.indexOf('/'+homeId)==0) {
			href = '/'+homeId+href;
		}
		var base = $ZMI.getPhysicalPath();
		base = base.substr(0,base.indexOf('/'+homeId));
		// Set wait-cursor.
		$container.append( '<div id="loading" class="zmi-page"><i class="icon-spinner icon-spin"></i>&nbsp;&nbsp;'+getZMILangStr('MSG_LOADING')+'<'+'/div>');
		// JQuery.AJAX.get
		$ZMI.writeDebug('zmiToggleClick:'+base+href+'/manage_ajaxGetChildNodes?lang='+getZMILang());
		$.get(base+href+'/manage_ajaxGetChildNodes',{lang:getZMILang()},function(data){
				// Reset wait-cursor.
				$("#loading").remove();
				// Get and iterate pages.
				var pages = $("pages",data).children("page");
				if ( pages.length == 0) {
					$(toggle).removeClass($ZMI.icon_clazz("icon-caret-down")).attr({title:''});
				}
				else {
					for (var i = 0; i < pages.length; i++) {
						var page = pages[i];
						var page_home_id = $(page).attr("home_id");
						var page_id = $(page).attr("id").substr(page_home_id.length+1);
						var page_absolute_url = $(page).attr("absolute_url");
						var page_physical_path = $(page).attr("physical_path");
						var page_is_page = $(page).attr("is_page")=='1' || $(page).attr("is_page")=='True';
						var page_is_pageelement = $(page).attr("is_pageelement")=='1' || $(page).attr("is_pageelement")=='True';
						var page_meta_type = $(page).attr("meta_id");
						var page_titlealt = $(page).attr("titlealt");
						var page_display_icon = $(page).attr("display_icon");
						var anchor = "";
						if ( page_is_pageelement) {
							var file_filename = $("file>filename",page);
							if (file_filename.length) {
								anchor = "/" + file_filename.text();
							}
						}
						var html = '';
						html += '<'+'ol data-id="'+page_id+'" data-home-id="'+page_home_id+'" class="zmi-page '+page_meta_type+'">';
						html += '<'+'div class="';
						/*
						if ($(page).attr("permissions")) {
							html += 'restricted ';
						}
						*/
						if ($(page).attr("active")== "0") {
							html += 'inactive ';
						} else {
							html += 'active ';
						}
						html += '">';
						html += $ZMI.icon("icon-caret-right toggle",'title="+" onclick="zmiToggleClick(this)"')+' ';
						html += '<'+'input type="radio" name="id" value=\''+page_absolute_url+'\' onclick="selectObject(\''+page_physical_path+'\',\''+anchor+'\',\''+page_is_page+'\',\''+page_titlealt.replace(/"/g,'\\"').replace(/'/g,"\\'")+'\')"/> ';
						if (page_is_pageelement) {
							html += '<span onclick="zmiPreview(this)">'+page_display_icon+'</span> ';
						}
						html += '<'+'a href="'+page_absolute_url+'/manage_main?lang='+getZMILang()+'" onclick="return zmiFollowHref(this)">';
						if (!page_is_pageelement) {
							html += page_display_icon+' ';
						}
						html += page_titlealt;
						html += '<'+'/a> ';
						html += '<'+'/div>';
						html += '<'+'/ol>';
						$container.append(html);
					}
				}
				if (typeof checked != "undefined") { 
					$('input:radio[value="'+checked+'"]').prop("checked","checked"); 
				} 
				if (typeof callback == 'function') {
					callback();
				}
			});
	}
	else if ($(toggle).hasClass($ZMI.icon_clazz("icon-caret-down"))) {
		$(toggle).removeClass($ZMI.icon_clazz("icon-caret-down")).addClass($ZMI.icon_clazz("icon-caret-right")).attr({title:'+'});
		if (typeof callback == 'function') {
			callback();
		}
	}
}

/**
 * Preview.
 */
function zmiPreview(sender) {
	var data_id = $(sender).parents('.zmi-page').attr('data-id');
	if($('#zmi_preview_'+data_id).length > 0) {
		$('#zmi_preview_'+data_id).remove();
	}
	else {
		var coords = $ZMI.getCoords(sender);
		var abs_url = $(sender).parent('div').children('input').val();
		$.get(abs_url+'/renderShort',{lang:getZMILang(),preview:'preview'},function(data){
				$('div.zmi-preview').remove();
				$('body').append('<div id="zmi_preview_'+data_id+'" class="zmi-preview">'+data+'</div><!-- #zmi-preview -->');
				$('div.zmi-preview').css({top:coords.y+$(sender).height(),left:coords.x+$(sender).width()});
			});
	}
}

/**
 * Follow link.
 */
function zmiFollowHref(anchor) {
	self.window.parent.manage_main.location.href=$(anchor).attr("href");
	return false;
}

/**
 * Refresh.
 */
function zmiRefresh() {
	$("ol:not(:first)").remove();
	$('.toggle').removeClass($ZMI.icon_clazz("icon-caret-down")).addClass($ZMI.icon_clazz("icon-caret-right"))
	var $ol = $("ol:first");
	var id = $ol.attr("data-id");
	var homeId = $ol.attr("data-home-id");
	$ZMI.writeDebug('zmiRefresh: id='+id+'; homeId='+homeId);
	var physical_path = $('span[name=physical_path]').text();
	var href = physical_path;
	if (typeof href == "undefined" || href == "") {
		href = $ZMI.getPhysicalPath();
	}
	$ZMI.writeDebug('zmiRefresh: href.0='+href);
	href = href.substr(href.indexOf(homeId));
	$ZMI.writeDebug('zmiRefresh: href.1='+href);
	var ids = href.split('/');
	var id = null;
	var fn = function() {
			if (ids.length > 0) {
				var old_id = id;
				var old_homeId = homeId;
				id = ids[0];
				$ZMI.writeDebug("zmiRefesh.id= "+id);
				ids = ids.slice(1,ids.length);
				$ZMI.writeDebug("zmiRefesh.ids= "+ids.length);
				if (id == homeId) {
					$ZMI.writeDebug("zmiRefesh.fn.1: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
					id = 'content'
					if (ids.length > 0 && ids[0] == id) {
						ids = ids.slice(1,ids.length);
					}
				}
				if ($('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length==0) {
					$ZMI.writeDebug("zmiRefesh.fn.2: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
					homeId = id;
					id = ids[0];
					ids = ids.slice(1,ids.length);
				}
				$ZMI.writeDebug("zmiRefesh.fn.3: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
				// Remove other than selected
				if (old_id != null) {
					$('*[data-id="'+old_id+'"][data-home-id="'+old_homeId+'"] *[data-id!="'+id+'"][data-home-id="'+homeId+'"]').remove();
					$('*[data-id="'+old_id+'"][data-home-id="'+old_homeId+'"] .toggle').removeClass($ZMI.icon_clazz("icon-caret-down")).addClass($ZMI.icon_clazz("icon-caret-right")).attr({title:'+'});
				}
				zmiToggleClick($('*[data-id="'+id+'"][data-home-id="'+homeId+'"] .toggle'),arguments.callee);
			}
			else if (typeof physical_path != "undefined" && physical_path != "") {
				$('*[data-id="'+id+'"][data-home-id="'+homeId+'"] input').prop('checked','checked');
			}
		};
	fn();
}

$(function(){
	$("button[name=btn]").click(function() {
			var type = $("select[name=type]").val();
			var url = $("input[name=url]").val();
			if (!url.indexOf(type)==0) {
				url = type + url;
			}
			selectUrl(url);
		});
	zmiRefresh();
});

