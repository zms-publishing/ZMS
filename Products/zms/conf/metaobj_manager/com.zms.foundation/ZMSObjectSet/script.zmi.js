function addZMSCustom(sort_id,custom) {
	var title = '<i class="fas fa-plus"></i> '+getZMILangStr('BTN_INSERT');
	var target = 'manage_addProduct/zms/manage_addzmscustomform';
	var data = {lang:getZMILang(),preview:'preview',id_prefix:'records','_sort_id:int':sort_id,custom:custom};
	// Show add-dialog.
	$ZMI.iframe(target,data,{
		id:'zmiIframeAddDialog',
		title:title,
		width:800,
		open:function(event,ui) {
			$ZMI.runReady();
			$('#addInsertBtn').click(function() {
				self.btnClicked = $(this).text();
				var $fm = $(".modal form.form-horizontal");
				$("input[name=btn]:hidden",$fm).remove();
				$fm.append('<input type="hidden" name="btn" value="BTN_INSERT">');
				$fm.submit();
			});
			$('#addCancelBtn').click(function() {
				zmiModal("hide");
			});
			if($('#zmiIframeAddDialog div.form-group:not([class*="activity"]) .form-control').length==0) {
				$('#addInsertBtn').click();
			}
		},
		close:function(event,ui) {
			$('#manage_addProduct').remove();
		},
		buttons:[
			{id:'addInsertBtn', text:getZMILangStr('BTN_INSERT'), name:'btn', 'class':'btn btn-primary'},
			{id:'addCancelBtn', text:getZMILangStr('BTN_CANCEL'), name:'btn', 'class':'btn btn-secondary'}
		]
	});
	return false;
}

function _zmiObjectSetExec(sender, target) {
	var $btnGroup = $(sender).parents(".btn-group");
	$("input[name='qindices:list']",$btnGroup).prop("checked","checked");
	var i = $("input[name='qindices:list']:checkbox:checked").length;
	var b = true;
	if (target.indexOf("manage_cutObjects") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_CUTOBJS') + $ZMI.getDescendantLanguages();
		msg = msg.replace("%i",""+i);
		b = i > 0 && confirm(msg);
	}
	else if (target.indexOf("manage_deleteObjs") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_TRASHOBJS');
		msg = msg.replace("%i",""+i);
		msg += $ZMI.getDescendantLanguages();
		b = i > 0 && confirm(msg);
	}
	if (b) {
		var html = '';
		html += '<form class="d-none" id="zmiObjectSetExecForm" method="post" action="'+target+'">';
		html += '<input type="hidden" name="lang" value="'+getZMILang()+'"/>';
		$("input[name='qindices:list']:checkbox:checked").each(function() {
			html += '<input type="hidden" name="ids:list" value="'+$(this).val()+'"/>';
		});
		html += '</form>';
		$("body").append(html);
		$("#zmiObjectSetExecForm").submit();
	}
	else {
		$("input[name='qindices:list']",$btnGroup).prop("checked","");
	}
	return false;
}

function zmiObjectSetDelete(sender) {
	return _zmiObjectSetExec(sender,'manage_deleteObjs');
}

function zmiObjectSetCut(sender) {
	return _zmiObjectSetExec(sender,'manage_cutObjects');
}

function zmiObjectSetCopy(sender) {
	return _zmiObjectSetExec(sender,'manage_copyObjects');
}

function zmiObjectSetPaste(sender) {
	return _zmiObjectSetExec(sender,'manage_pasteObjs');
}

function zmiObjectSetBuildGridParams(prefix) {
	var params = {lang:zmiParams['lang'],AUTHENTICATED_USER:$(".authenticated_user").text()};
	for (var i in localStorage) {
		if (i.indexOf(prefix)==0) {
			console.log("i="+i);
			params[i.substring(prefix.length)] = localStorage[i];
		}
	}
	// Force to ZMI language
	params['lang'] = zmiParams['lang'];
	return params;
}

function zmiObjectSetAssembleGrid($grid, prefix) {
	// Assemble info.
	$(".zmi-info",$grid).each(function() {
		if (!$(this).hasClass("active")) {
			$(this).parents("tr").addClass("inactive");
		}
	});

	// Assemble update.
	$(".dropdown-menu a[onclick='[[UPDATE]]']",$grid).each(function() {
		var $btnGroup = $(this).parents(".btn-group");
		var rawId = $("input[name='qindices:list']",$btnGroup).val();
		if (typeof rawId !== 'string' || !/^[A-Za-z0-9._\/-]+$/.test(rawId)) {
			return;
		}
		var safeId = encodeURIComponent(rawId);
		var href = safeId + '/manage_main?lang=' + getZMILang();
		$(this).attr({href:href,onclick:''});
	});

	// Assemble insert.
	var $insertContent = $("<div></div>");
	$insertContent.append(
		$('<li class="dropdown-header insert-action"><i class="icon-caret-down fas fa-caret-down"></i> '+getZMILangStr('BTN_INSERT')+'</li>')
	);
	$("select[name='record_meta_ids:list'] option:selected").each(function() {
		var $option = $(this);
		var custom = $option.text().trim();
		var $item = $('<a class="dropdown-item" href="javascript:;"></a>');
		$item.text($option.text());
		$item.on("click", function(event) {
			event.preventDefault();
			addZMSCustom(0, custom);
		});
		$insertContent.append($item);
	});
	$insertContent.append(
		$('<li class="dropdown-header insert-action"><i class="icon-caret-down fas fa-caret-down"></i> '+getZMILangStr('ATTR_ACTION')+'</li>')
	);
	$(".dropdown-menu .fa-plus",$grid).each(function() {
		$(this).parents(".dropdown-item").replaceWith($insertContent.children().clone(true));
	});

}

function zmiObjectSetSortHeaderClick(event) {
	event.preventDefault();
	var $link = $(event.currentTarget);
	var href = $link.attr("href") || '';
	if (href.length==0) {
		return false;
	}

	var $grid = $("#metaobj_recordset_main_grid");
	$(".ZMSRecordSet.main_grid form",$grid).css({'transition':'opacity 1.5s','opacity':'0.25'});
	if ($("#loading",$grid).length==0) {
		$grid.prepend("<div id='loading' class='zmi-page text-center' style='width:100%;position:absolute;margin-bottom:0.75em'><i class='text-primary fas fa-circle-notch fa-spin fa-3x'></i></div>");
	}

	var params = {};
	try {
		var sortUrl = new URL(href, window.location.href);
		sortUrl.searchParams.forEach(function(value, key) {
			params[key] = value;
		});
	}
	catch (e) {
		console.log("Could not parse sort-link URL", e);
	}

	var prefix = $grid.data('zms-prefix');
	if (typeof prefix=='undefined' || prefix===null) {
		prefix = $("meta[name=physical_path]").attr("content").split("/");
		prefix = prefix[prefix.length-1]+".ZMSRecordSet.";
		$grid.data('zms-prefix',prefix);
	}
	params = $.extend({}, zmiObjectSetBuildGridParams(prefix), params);

	$.get("publicRecordSetGrid",params,function(data) {
		$grid.html(data);
		zmiObjectSetAssembleGrid($grid,prefix);
	});
	return false;
}

$(function() {

	// always collapse last-modified-accordion
	$(".attr_last_modified a.card-toggle").each(function(){
		var data_root = $("body").attr('data-root');
		var id = $(this).attr('href').substring(1);
		var key = "ZMS."+data_root+".collapse-"+id;
		console.log("$ZMILocalStorageAPI.set("+key+",0)");
		$ZMILocalStorageAPI.set(key,'0');
	});

	$("#tabProperties").hide();
	$(".zmi-change-uid").after(' <a href="javascript:;" title="Change Objectset Configuration" onclick="$(\'#tabProperties\').slideToggle();"><i class="fas fa-cog"></i></a>');

	// Relocate buttons.
	var e = $(".controls.save:gt(0)").detach();
	e.insertAfter(".form-group.coverage");

	$(document).off('click.zmiObjectSetSort','#metaobj_recordset_main_grid table.zmi-sortable th > a');
	$(document).on('click.zmiObjectSetSort','#metaobj_recordset_main_grid table.zmi-sortable th > a',zmiObjectSetSortHeaderClick);

	$(".ZMSRecordSet form.form-horizontal,.ZMSRecordSet.main_grid > form").each(function() {
		var prefix = $("meta[name=physical_path]").attr("content").split("/");
		prefix = prefix[prefix.length-1]+".ZMSRecordSet.";
		console.log(prefix);
		var $fm = $(this);
		localStorage[prefix+"btn"] = getZMILangStr('BTN_REFRESH');
		if (zmiParams['btn']==getZMILangStr('BTN_REFRESH')) {
			for (var i in zmiParams) {
				localStorage[prefix+i] = zmiParams[i];
			}
			$("input:text,input:checkbox,input:radio,select,textarea",$fm).each(function() {
				var $input = $(this);
				var n = $input.attr("name");
				var v = $input.val();
				if ($input.attr("type")=="radio") {
					v = $("input[name='"+n+"']:radio:checked").val();
				}
				if ($input.attr("type")=="checkbox") {
					v = $input.prop("checked")?v:null;
				}
				if ($input[0].nodeName.toUpperCase()=="SELECT") {
					v = $("option:selected",$input).val();
				}
				localStorage[prefix+n] = v;
			});
		}
		else if (typeof zmiParams['btn']!='undefined') {
			for (var i in localStorage) {
				if (i.indexOf(prefix)==0) {
					localStorage.removeItem(i);
				}
			}
		}

		var params = zmiObjectSetBuildGridParams(prefix);

		$.get("publicRecordSetGrid",params,function(data) {
			// Assemble grid.
			var $grid = $("#metaobj_recordset_main_grid");
			$grid.data('zms-prefix',prefix);
			$grid.html(data);
			zmiObjectSetAssembleGrid($grid,prefix);

		});
	});
});