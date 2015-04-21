/**
 * Select object.
 */
function zmiSelectObject(sender) {
	var absolute_url = $(sender).attr('href');
	var physical_path = $(sender).attr('data-page-physical-path');
	var id = physical_path.substr(physical_path.lastIndexOf('/')+1);
	var index_html = $(sender).attr('data-index-html');
	var anchor = $(sender).attr('data-anchor');
	var is_page = $(sender).attr('data-page-is-page');
	var titlealt = $(sender).attr('data-page-titlealt');
	$ZMI.writeDebug('BO zmiSelectObject: absolute_url='+absolute_url+'\nphysical_path='+physical_path+'\nindex_html='+index_html+'\nanchor='+anchor+'\ntitlealt='+titlealt);
	var fm;
	var url = physical_path;
	if (!(absolute_url.indexOf('/')==0) && !(index_html.indexOf('/')==0) && $ZMI.getServerUrl(absolute_url) != $ZMI.getServerUrl(index_html)) {
		//url = index_html;
	}
	var title = titlealt;
	if (typeof zmiParams['fmName'] != 'undefined' && zmiParams['fmName'] != ''
			&& typeof zmiParams['elName'] != 'undefined' && zmiParams['elName'] != '') {
		fm = self.window.parent.document.forms[zmiParams['fmName']];
	}
	if ( fm) {
		var path = getInternalUrl(url);
		self.window.parent.zmiBrowseObjsApplyUrlValue(zmiParams['fmName'],zmiParams['elName'],path,titlealt);
	}
	else {
		url = $ZMI.relativateUrl(url,anchor);
		self.window.parent.selectObject(url,title,id);
	}
	self.window.parent.zmiModal("hide");
	$ZMI.writeDebug('EO zmiSelectObject: url='+url+',title='+title);
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
	var targetHome;
	if (targetPath.indexOf(content)>0) {
		targetHome = targetPath.substr(1,targetPath.indexOf(content)-1);
		targetPath = targetPath.substr(targetPath.indexOf(content)+content.length+1);
	}
	else {
		targetHome = currntHome;
		targetPath = targetPath.substr(targetPath.indexOf('://')+'://'.length+1);
		targetPath = targetPath.substr(targetPath.indexOf('/'));
	}
	var home = targetHome;
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
	if ( $ZMI.getConfProperty('ZMS.internalLinks.home',1)==1 || currntHome != targetHome) {
		path = (targetHome.length>0?targetHome:home) + "@" + path;
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
		$.get(base+href+'/manage_ajaxGetChildNodes',{lang:getZMILang(),physical_path:$('meta[name=physical_path]').attr('content')},function(data){
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
						var page_index_html = $(page).attr("index_html");
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
						html += '<ol data-id="'+page_id+'" data-home-id="'+page_home_id+'" class="zmi-page '+page_meta_type+'">';
						html += '<div class="';
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
						html += '">'
							+ $ZMI.icon("icon-caret-right toggle",'title="+" onclick="zmiToggleClick(this)"')+' '
						if (!page_is_page) {
							html += '<span style="cursor:help" onclick="zmiPreview(this)">'+page_display_icon+'</span> ';
						}
						html += '<a href="'+page_absolute_url+'"'
                            + ' data-page-physical-path="'+page_physical_path+'"'
                            + ' data-index-html="'+page_index_html+'"'
                            + ' data-anchor="'+anchor+'"'
                            + ' data-page-is-page="'+page_is_page+'"'
                            + ' data-page-titlealt="'+page_titlealt.replace(/"/g,'\\"').replace(/'/g,"\\'")+'"'
                            + ' onclick="return zmiSelectObject(this)">';
						if (page_is_page) {
							html += page_display_icon+' ';
						}
						html += page_titlealt;
						html += '</a> ';
						html += '</div>';
						html += '</ol>';
						$container.append(html);
					}
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
		$.get(abs_url+'/ajaxGetBodyContent',{lang:getZMILang(),preview:'preview'},function(data){
				$('div.zmi-preview').remove();
				$('body').append(''
						+'<div id="zmi_preview_'+data_id+'">'
							+'<div class="zmi-preview">'
								+'<div class="bg-primary" style="margin:-1em -1em 0 -1em;padding:0 4px 2px 4px;cursor:pointer;text-align:right;font-size:smaller;" onclick="$(\'#zmi_preview_'+data_id+'\').remove()">'+$ZMI.icon("icon-remove")+' '+getZMILangStr('BTN_CLOSE')+'</div>'
								+data
							+'</div><!-- .zmi-preview -->'
						+'</div><!-- #zmi-preview -->'
					);
				$('div.zmi-preview').css({top:coords.y+$(sender).height(),left:coords.x+$(sender).width()});
			});
	}
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
			$ZMI.writeDebug("zmiRefresh.fn: =======================================");
			$ZMI.writeDebug("zmiRefresh.fn: ids= "+ids.join(','));
			var selector = null;
			if (ids.length > 0) {

				selector = '*[data-home-id="'+homeId+'"]'; 
				$ZMI.writeDebug('zmiRefresh.fn.0: '+selector+'='+$(selector).length);

				var old_id = id;
				var old_homeId = homeId;
				id = ids[0];
				ids = ids.slice(1,ids.length);

				if (id == homeId) {
					id = 'content';
					if (ids.length > 0 && ids[0] == id) {
						ids = ids.slice(1,ids.length);
					}
				}

				selector = '[data-home-id="'+homeId+'"][data-id="'+id+'"] .toggle';
				$ZMI.writeDebug('zmiRefresh.fn.3: '+selector+'='+$(selector).length);
				if ($(selector).length==0) {
					homeId = id;
					id = 'content';
					if (ids.length > 0 && ids[0] == id) {
						ids = ids.slice(1,ids.length);
					}
				}

				// Remove other than selected
				if (old_id != null) {
					selector = '[data-home-id="'+old_homeId+'"][data-id="'+old_id+'"] .zmi-page[data-id!="'+id+'"]';
					$ZMI.writeDebug('zmiRefresh.fn: Remove other than selected: '+selector+'='+$(selector).length);
					$(selector).remove();
					$('[data-home-id="'+old_homeId+'"][data-id="'+old_id+'"] .toggle[title="-"]').removeClass('icon-caret-down').addClass('icon-caret-right').attr('title','+');
				}

				selector = '*[data-home-id="'+homeId+'"][data-id="'+id+'"] .toggle';
				$ZMI.writeDebug('zmiRefresh.fn.4: '+selector+'='+$(selector).length);
				$ZMI.writeDebug('zmiRefresh.fn: click(homeId='+homeId+';id='+id+')');
				zmiToggleClick($(selector),arguments.callee);
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

var URLParser = (function (document) {
	var PROPS = 'protocol hostname host pathname port search hash href'.split(' ');
	var self = function (url) {
		this.aEl = document.createElement('a');
		this.parse(url);
	};
	self.prototype.parse = function (url) {
		this.aEl.href = url;
		if (this.aEl.host == "") {
			this.aEl.href = this.aEl.href;
		}
        PROPS.forEach(function (prop) {
            switch (prop) {
                case 'hash':
                    this[prop] = this.aEl[prop].substr(1);
                    break;
                default:
                    this[prop] = this.aEl[prop];
            }
        }, this);
        if (this.pathname.indexOf('/') !== 0) {
            this.pathname = '/' + this.pathname;
        }
        this.requestUri = this.pathname + this.search;
    };
    self.prototype.toObj = function () {
        var obj = {};
        PROPS.forEach(function (prop) {
            obj[prop] = this[prop];
        }, this);
        obj.requestUri = this.requestUri;
        return obj;
    };
    self.prototype.toString = function () {
        return this.href;
    };
    return self;
})(document);

function zmiBodyContentSearchDone() {
	$("#search_results h4:first").hide();
	$(".line.row").each(function() {
			var $h2 = $("h2",this);
			var meta_id = $("h2").attr("class");
			var display_icon = $ZMI.display_icon(meta_id);
			var $a = $("a",$h2);
			$a.html(display_icon+' '+$a.html());
			var href = $a.attr("href");
			if (href.lastIndexOf(".html")>href.lastIndexOf("/")) {
				href = href.substr(0,href.lastIndexOf("/"));
			}
			var parser = new URLParser();
			parser.parse(href);
			var url = parser.toObj();
			var titlealt = $a.text();
			$a.attr({
                'href':url['href'],
                'data-page-titlealt':titlealt,
                'data-anchor':url['hash'],
                'data-page-is-page':'true',
                'data-page-physical-path':url['pathname'],
                'data-index-html':url['href']
                })
              .click(function() {return zmiSelectObject(this)});
		});
}

$(function(){
		// Select tab.
		var $tabs_left = $("div.tabs-left");
		var anchor = $("a:first",$tabs_left).attr("href");
		if (self.location.href.indexOf("#")>0) {
			anchor = self.location.href.substr(self.location.href.indexOf("#")+1);
			if (anchor.indexOf('_')==0) {
				anchor = anchor.substr(1);
			}
			anchor = '#'+anchor;
		}
		$("a[href='"+anchor+"']",$tabs_left).tab("show");
	});
