/**
 * Select object.
 */
function zmiSelectObject(sender) {
	$(".zmi-sitemap .active").removeClass("active");
	let $sender = $(sender);
	$sender.parents("li").addClass("active");
	let origin = window.location.origin;
	let href = $sender.attr("href");
	let lang = getZMILang();
	// same origin?
	if (href.startsWith(origin)) {
			// change location in manage_main-frame
			window.parent.manage_main.location.href=href + "/manage_main?lang=" + lang;
	} else {
			// open new home in new tab
			window.open(href + "/manage?lang=" + lang + "&dtpref_sitemap=1", "_blank").focus();
	}
	return false;
}
function zmiRefresh() {
	var href = $ZMI.getPhysicalPath();
	try {
		href = window.parent.manage_main.$ZMI.getPhysicalPath();
	}
	catch(e) {
		console.log('zmiRefresh: cannot get physical-path from parent - ' + e);
	}
	$ZMI.objectTree.init(".zmi-sitemap",href,{params:{meta_types:$ZMI.getConfProperty('zms.plugins.www.object.manage_menu.meta_types','0,1,ZMSTrashcan')}});
}

// Leading Zeros
// https://gist.github.com/aemkei/1180489
function pad(a,b){
	return(1e15+a+"").slice(-b)
}

function zmiBookmarksChanged() {
	var data_root = $("body").attr('data-root');
	var key = "ZMS."+data_root+".bookmarks";
	var bookmarks = $ZMILocalStorageAPI.get(key,[]);
	var url = "ajaxGetNodes";
	var lang = getZMILang();
	var data = {lang:lang};
	for (var i = 0; i < bookmarks.length; i++) {
		data['ref'+i] = bookmarks[i];
	}
	$.ajax({
			url:url,data:data
		})
		.done(function(response) {
				var html = '';
				var i = 0;
				$("page",response).each(function() {
						var not_found = $(this).attr("not_found");
						if (typeof not_found=="undefined" || not_found!="1") {
							var titlealt = $(this).attr("titlealt");
							var absolute_url = $(this).attr("absolute_url");
							var icon = $(this).attr("zmi_icon");
							if (i==0) {
								html += '<a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown" title="Bookmarks">';
								html += $ZMI.icon('far fa-bookmark')+' ';
								html += '</a>';
								html += '<div class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">';
								html += '<div class="dropdown-header">Bookmarks</div>';
							}
							html += ''
									+ '<a class="dropdown-item pr-5" href="'+absolute_url+'/manage_main?lang='+lang+'" target="manage_main">'
											+ '<span class="title">' + $ZMI.icon(icon)+titlealt+'</span>'
											+ '<span class="close" title="Remove Favorite" data-path="'+bookmarks[i]+'">×</span>'
									+ '</a>';
							i++;
						}
					});
				if (i>0) {
					html += '</div><!-- .dropdown-menu --> ';
				}
				$("#zmi-bookmarks").html(html);
				$("#zmi-bookmarks .close").click(function(event) {
						event.preventDefault();
						event.stopPropagation();
						var data_path = $(this).attr('data-path');
						if(confirm(getZMILangStr('MSG_CONFIRM_DELOBJ'))){
							var index = bookmarks.indexOf(data_path);
							bookmarks.splice(index,1);
							$ZMILocalStorageAPI.replace(key,bookmarks);
							zmiBookmarksChanged();
						}
					});
			});
}

function zmiHistoryChanged() {
	var data_root = $("body").attr('data-root');
	var key = "ZMS."+data_root+".history";
	var history = $ZMILocalStorageAPI.get(key,[]);
	var url = "ajaxGetNodes";
	var lang = getZMILang();
	var data = {lang:lang};
	for (var i = 0; i < Math.min(history.length,10); i++) {
		data['ref'+i] = history[i];
	}
	$.ajax({
			url:url,data:data
		})
		.done(function(response) {
				var html = '';
				var i = 0;
				$("page",response).each(function() {
						var not_found = $(this).attr("not_found");
						if (typeof not_found=="undefined" || not_found!="1") {
							var titlealt = $(this).attr("titlealt");
							var absolute_url = $(this).attr("absolute_url");
							var icon = $(this).attr("zmi_icon");
							if (icon && icon.indexOf('<')!=0) {
								icon = $ZMI.icon(icon);
							}
							if (i==0) {
								html += '<a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown" title="History">';
								html += $ZMI.icon('far fa-clock')+' ';
								html += '</a>';
								html += '<div class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">';
								html += '<div class="dropdown-header">History</div>';
							}
							html += '<a class="dropdown-item" href="'+absolute_url+'/manage_main?lang='+lang+'" target="manage_main">'+pad((i+1),2)+'. '+icon+' '+titlealt+'</a>';
							i++;
						}
					});
				if (i>0) {
					html += '</div><!-- .dropdown-menu --> ';
				}
				$("#zmi-history").html(html);
			});
}

function zmiResize(init) {
	var key = "ZMS.manage_menu.width";
	$(window).resize(function() {
			$ZMILocalStorageAPI.set(key,window.innerWidth);
		});
	var frmwidth = $ZMILocalStorageAPI.get(key,224);
	var frmset = parent.document.getElementsByTagName('frameset');
	var colval = frmwidth + ",*";
	try {
		frmset[0].cols=colval;
	} catch(err) {
		console.log(err)
	}
}

$(function(){
	zmiResize();
	zmiRefresh();
	zmiBookmarksChanged();
	zmiHistoryChanged();
});

