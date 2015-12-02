/**
 * Select object.
 */
function zmiSelectObject(sender) {
	$(".zmi-sitemap .active").removeClass("active");
	$(sender).parents("li").addClass("active");
	window.parent.manage_main.location.href=$(sender).attr("href")+"/manage_main?lang="+getZMILang();
	// window.parent.location.href=$(sender).attr("href")+"/manage?lang="+getZMILang()+"&dtpref_sitemap=1";
	return false;
}
function zmiRefresh() {
	var href = $ZMI.getPhysicalPath();
	try {
		href = window.parent.manage_main.$ZMI.getPhysicalPath();
	}
	catch(e) {
		$ZMI.writeDebug('zmiRefresh: cannot get physical-path from parent - ' + e);
	}
	$ZMI.objectTree.init(".zmi-sitemap",href,{params:{meta_types:$ZMI.getConfProperty('zms.plugins.www.object.manage_menu.meta_types','0,ZMSTrashcan')}});
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
							var icon = $(this).attr("display_icon");
							if (icon.indexOf('<')!=0) {
								icon = $ZMI.icon(icon);
							}
							if (i==0) {
								html += '<a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown" title="Favoriten">';
								html += $ZMI.icon('icon-bookmark')+' ';
								html += '<b class="caret"></b>';
								html += '</a>';
								html += '<ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">';
								html += '<li class="dropdown-header">'+$ZMI.icon('icon-bookmark')+' Favoriten</li>';
							}
							html += ''
								+ '<li role="presentation">'
									+ '<a href="'+absolute_url+'/manage_main?lang='+lang+'" target="manage_main"'
											+ ' onmouseover="$(\'.icon-remove.text-muted\').removeClass(\'text-muted\').addClass(\'text-danger\')"'
											+ ' onmouseout="$(\'.icon-remove.text-danger\').removeClass(\'text-danger\').addClass(\'text-muted\')"'
										+ '>'+icon+' '+titlealt+'</span> '
										+ '<span title="Favorit entfernen" data-path="'+bookmarks[i]+'"'
											+ '>'+$ZMI.icon('icon-remove text-muted')+'</span>'
									+ '</a>'
								+ '</li>';
							i++;
						}
					});
				if (i>0) {
					html += '</ul><!-- .dropdown-menu --> ';
				}
				$("#zmi-bookmarks").html(html);
				$("#zmi-bookmarks .icon-remove.text-muted").click(function(event) {
						event.preventDefault();
						event.stopPropagation();
						var data_path = $(this).parent().attr('data-path');
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
							var icon = $(this).attr("display_icon");
							if (icon.indexOf('<')!=0) {
								icon = $ZMI.icon(icon);
							}
							if (i==0) {
								html += '<a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown" title="Verlauf">';
								html += $ZMI.icon('icon-time')+' ';
								html += '<b class="caret"></b>';
								html += '</a>';
								html += '<ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">';
								html += '<li class="dropdown-header">'+$ZMI.icon('icon-time')+' Verlauf</li>';
							}
							html += '<li role="presentation"><a href="'+absolute_url+'/manage_main?lang='+lang+'" target="manage_main">'+(i+1)+'. '+icon+' '+titlealt+'</a></li>';
							i++;
						}
					});
				if (i>0) {
					html += '</ul><!-- .dropdown-menu --> ';
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
	frmset[0].cols=colval;
}

$(function(){
	zmiResize();
	zmiRefresh();
	zmiBookmarksChanged();
	zmiHistoryChanged();
});

