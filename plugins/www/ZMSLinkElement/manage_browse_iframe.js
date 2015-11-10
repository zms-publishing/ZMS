/**
 * Select object.
 */
function zmiSelectObject(sender) {
	var uid = $(sender).attr('data-uid');
	var physical_path = $(sender).attr('data-page-physical-path');
	var anchor = $(sender).attr('data-anchor');
	var titlealt = $(sender).attr('data-page-titlealt');
	$ZMI.writeDebug('BO zmiSelectObject: uid='+uid+'\nphysical_path='+physical_path+'\nanchor='+anchor+'\ntitlealt='+titlealt);
	var fm;
	var url = physical_path;
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
		self.window.parent.selectObject(url,title,uid);
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
	var lang = self.window.parent.getZMILang();
	path = "{$"+path+(lang==getZMILang()?'':';lang='+getZMILang())+"}";
	$ZMI.writeDebug('EO getInternalUrl: path='+path);
	return path;
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
	var physical_path = $('span[name=physical_path]').text();
	var href = physical_path;
	if (typeof href == "undefined" || href == "") {
		href = $ZMI.getPhysicalPath();
	}
	$ZMI.objectTree.init(".zmi-sitemap",href,{});
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
