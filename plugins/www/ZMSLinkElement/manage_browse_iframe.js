function selectObject(physical_path,anchor,is_page,titlealt) {
	$ZMI.writeDebug('selectObject: physical_path='+physical_path+',anchor='+anchor);
	var url = physical_path;
	var title = titlealt;
	if (typeof zmiParams['fmName'] != 'undefined' && zmiParams['fmName'] != '') {
		if (typeof zmiParams['elName'] != 'undefined' && zmiParams['elName'] != '') {
			var fm = self.parent.document.forms[zmiParams['fmName']];
			if ( fm) {
				var path = getInternalUrl(url);
				self.parent.zmiBrowseObjsApplyUrlValue(zmiParams['fmName'],zmiParams['elName'],path);
			}
			else {
				self.parent.selectObject(url,title);
			}
		}
	}
	else {
		if ((''+$('#type').val()).indexOf('dtml')==0) {
			url = "<" + "dtml-var \"getLinkUrl('" + getInternalUrl(url) + "',REQUEST)\">";
		}
		else {
			url = getRelativeUrl(url,anchor);
		}
		self.parent.selectObject(url,title);
	}
	self.parent.zmiDialogClose('zmiDialog');
}

/**
 * Returns internal url in {$...}-notation.
 */
function getInternalUrl(url) {
	var content = "/content";
	var base_url = $('#BASE0').text();
	var currntPath = $('#absolute_url').text();
	var targetPath = url;
	currntPath = currntPath.substring( base_url.length);
	targetPath = targetPath.substring( base_url.length);
	var currntHome = currntPath;
	if ( currntHome.indexOf( content) >= 0) {
		currntHome = currntHome.substring( 0, currntHome.indexOf( content));
	}
	else {
		currntPath = content + currntPath;
		currntHome = "";
	}
	var targetHome = targetPath;
	if ( targetHome.indexOf( content) >= 0) {
		targetHome = targetHome.substring( 0, targetHome.indexOf( content));
	}
	else {
		targetPath = content + targetPath;
		targetHome = "";
	}
	var j = targetHome.indexOf( "/");
	if ( currntHome.indexOf( targetHome + "/") == 0) {
		targetHome = targetHome.substring( j+1);
	}
	else {
		if ( j == 0)
			targetHome = targetHome.substring( j+1);
		while ( currntHome.length > 0 && targetHome.length > 0) {
			var i = currntHome.indexOf( "/");
			var j = targetHome.indexOf( "/");
			if ( i < 0) {
				currntElmnt = currntHome;
			}
			else {
				currntElmnt = currntHome.substring( 0, i);
			}
			if ( j < 0) {
				targetElmnt = targetHome;
			}
			else {
				targetElmnt = targetHome.substring( 0, j);
			}
			if ( currntElmnt != targetElmnt) {
				break;
			}
			if ( i < 0) {
				currntHome = '';
			}
			else {
				currntHome = currntHome.substring( i+1);
			}
			if ( j < 0) {
				targetHome = '';
			}
			else {
				targetHome = targetHome.substring( j+1);
			}
		}
	}
	var path = targetPath.substring( targetPath.indexOf( content) + content.length);
	if (path.indexOf("/")==0) {
		path = path.substring(1);
	}
	if ( currntHome != targetHome) {
		path = targetHome + "@" + path;
	}
	path = "{$" + path + "}";
	return path;
}

/**
 * Returns relative url.
 */
function getRelativeUrl(physical_path, anchor) {
	$ZMI.writeDebug('BO getRelativeUrl: physical_path='+physical_path+',anchor='+anchor);
	var currntPath = $ZMI.getPhysicalPath();
	var targetPath = physical_path;
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
	if ( targetPath.length > 0) {
		targetPath = targetPath + '/';
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
	if ( anchor.length > 1 && anchor.indexOf('#') == 0) {
		url = url.substring(0,url.substring(0,url.length-2).lastIndexOf( '/')+1);
	}
	if ( anchor.indexOf( '/') == 0) {
		url += anchor.substring( 1);
	}
	else {
		url += 'index_'+getZMILang()+'.html' + anchor;
	}
	$ZMI.writeDebug('EO getRelativeUrl: url='+url);
	return url;
}

function zmiToggleClick(toggle, callback) {
	$ZMI.writeDebug('zmiToggleClick: '+toggle+'['+($(toggle).length)+'];callback='+(typeof callback));
	var $container = $(toggle).parents("ol:first");
	$container.children(".zmi-page").remove();
	if ($(toggle).hasClass(zmi_icon_clazz("icon-caret-right"))) {
		$(toggle).removeClass(zmi_icon_clazz("icon-caret-right")).addClass(zmi_icon_clazz("icon-caret-down")).attr({title:'-'});
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
		$.get(base+href+'/manage_ajaxGetChildNodes',{lang:getZMILang(),meta_types:'0,ZMSTrashcan',get_permissions:'True',get_restricted:'True'},function(data){
				// Reset wait-cursor.
				$("#loading").remove();
				// Get and iterate pages.
				var pages = $("pages",data).children("page");
				if ( pages.length == 0) {
					$(toggle).removeClass(zmi_icon_clazz("icon-caret-down")).attr({title:''});
				}
				else {
					for (var i = 0; i < pages.length; i++) {
						var page = pages[i];
						var page_home_id = $(page).attr("home_id");
						var page_id = $(page).attr("id").substr(page_home_id.length+1);
						var page_absolute_url = $(page).attr("absolute_url");
						var page_physical_path = $(page).attr("physical_path");
						var page_is_page = $(page).attr("is_page");
						var page_is_pageelement = $(page).attr("is_pageelement");
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
						html += zmi_icon("icon-caret-right toggle",'title="+" onclick="zmiToggleClick(this)"')+' ';
						html += '<'+'input type="radio" value=\''+page_absolute_url+'\' onclick="selectObject(\''+page_physical_path+'\',\''+anchor+'\',\''+page_is_page+'\',\''+page_titlealt.replace(/"/g,'\\"').replace(/'/g,"\\'")+'\')"/> ';
						html += '<'+'a href="'+page_absolute_url+'/manage_main?lang='+getZMILang()+'" onclick="return zmiFollowHref(this)">';
						html += page_display_icon+' ';
						html += page_titlealt;
						html += '<'+'/a> ';
						html += '<'+'/div>';
						html += '<'+'/ol>';
						$container.append(html);
					}
				}
				if (typeof callback == 'function') {
					$ZMI.writeDebug('zmiToggleClick: callback()');
					callback();
				}
			});
	}
	else if ($(toggle).hasClass(zmi_icon_clazz("icon-caret-down"))) {
		$(toggle).removeClass(zmi_icon_clazz("icon-caret-down")).addClass(zmi_icon_clazz("icon-caret-right")).attr({title:'+'});
		if (typeof callback == 'function') {
			$ZMI.writeDebug('zmiToggleClick: callback()');
			callback();
		}
	}
}
function zmiFollowHref(anchor) {
	self.window.parent.manage_main.location.href=$(anchor).attr("href");
	return false;
}
function zmiRefresh() {
	$("ol:not(:first)").remove();
	$('.toggle').removeClass(zmi_icon_clazz("icon-caret-down")).addClass(zmi_icon_clazz("icon-caret-right"))
	var $ol = $("ol:first");
	var id = $ol.attr("data-id");
	var homeId = $ol.attr("data-home-id");
	$ZMI.writeDebug('zmiRefresh: id='+id+'; homeId='+homeId);
	var physical_path = $('span[name=physical_path]').text();
	var href = physical_path;
	if (typeof href == "undefined") {
		href = $ZMI.getPhysicalPath();
	}
	$ZMI.writeDebug('zmiRefresh: href.0='+href);
	href = href.substr(href.indexOf(homeId));
	$ZMI.writeDebug('zmiRefresh: href.1='+href);
	var ids = href.split('/');
	var fn = function() {
			if (ids.length > 0) {
				var id = ids[0];
				$ZMI.writeDebug("zmiRefesh.id= "+id);
				ids = ids.slice(1,ids.length);
				$ZMI.writeDebug("zmiRefesh.ids= "+ids.length);
				$ZMI.writeDebug("zmiRefesh.fn.1: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
				if (id == homeId) {
					id = 'content'
					if (ids.length > 0 && ids[0] == id) {
						ids = ids.slice(1,ids.length);
					}
				}
				$ZMI.writeDebug("zmiRefesh.fn.2: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
				if ($('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length==0) {
					homeId = id;
					id = ids[0];
					ids = ids.slice(1,ids.length);
				}
				$ZMI.writeDebug("zmiRefesh.fn.3: $'*[data-id="+id+"][data-home-id="+homeId+"]')="+$('*[data-id="'+id+'"][data-home-id="'+homeId+'"]').length);
				zmiToggleClick($('*[data-id="'+id+'"][data-home-id="'+homeId+'"] .toggle'),arguments.callee);
			}
			else if (typeof physical_path != 'undefined') {
				var id = physical_path.split('/').pop();
				$('*[data-id="'+id+'"][data-home-id="'+homeId+'"] input').prop('checked','checked');
			}
		};
	fn();
}

$ZMI.registerReady(function(){
	zmiRefresh();
});

