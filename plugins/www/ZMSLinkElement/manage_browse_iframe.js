/**
 * Select internal url.
 */
function zmiSelectObject(sender) {
	var parent = self.window.parent;
	var uid = $(sender).attr('data-uid');
	var selectedLang = zmiParams['selectedLang'];
	uid = uid.substr(0,uid.lastIndexOf('}'))+(typeof selectedLang=='undefined' || selectedLang==''?'':';lang='+selectedLang)+"}";
	var href = $(sender).attr('href');
	var titlealt = $(sender).attr('data-page-titlealt');
	$ZMI.writeDebug('zmiSelectObject: uid='+uid+'\nhref='+href+'\ntitlealt='+titlealt);
	var fm;
	var fmName = zmiParams['fmName']; 
	var elName = zmiParams['elName']; 
	if (typeof fmName != 'undefined' && fmName != '' && typeof elName != 'undefined' && elName != '') {
		fm = parent.document.forms[fmName];
	}
	if (fm) {
		parent.zmiBrowseObjsApplyUrlValue(fmName,elName,uid,titlealt);
	}
	else {
		parent.selectObject(href,titlealt,uid);
	}
	self.window.parent.zmiModal("hide");
}

/**
 * Select external url.
 */
function selectUrl(href) {
	var titlealt = '';
	$ZMI.writeDebug('selectUrl: href='+href+'\ntitlealt='+titlealt);
	var fm;
	var fmName = zmiParams['fmName']; 
	var elName = zmiParams['elName']; 
	if (typeof fmName != 'undefined' && fmName != '' && typeof elName != 'undefined' && elName != '') {
		fm = parent.document.forms[fmName];
	}
	if (fm) {
		parent.zmiBrowseObjsApplyUrlValue(fmName,elName,href);
	}
	else {
		self.window.parent.selectObject(href,titlealt);
	}
	self.window.parent.zmiModal("hide");
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
