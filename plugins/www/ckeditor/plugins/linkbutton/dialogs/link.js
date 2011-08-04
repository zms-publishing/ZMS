var zmiDialog = null;

function showPreviewZMSGraphic(id,src,icon,filename,size) {
	var html= '';
	html += '<div class="img_head"><img src="'+icon+'" border="0" align="absmiddle"/> '+filename+' ('+size+')</div>';
	html += '<div class="img_img"><img src="'+src+'" border="0" align="absmiddle" style="max-width:200px;"/></div>';
	html += '';
	$("div#CKEDITOR_preview_"+id).html(html).show('normal');
}

function showPreviewZMSFile(id,href,icon,filename,size) {
	var html= '';
	html += '<div class="file_head"><a href="'+href+'" target="_blank" class="zmi"><img src="'+icon+'" border="0" align="absmiddle"/> '+filename+' ('+size+')</a></div>';
	html += '';
	$("div#CKEDITOR_preview_"+id).html(html).show('normal');
}

function hidePreview(id) {
	$("div#CKEDITOR_preview_"+id).hide('normal');
}

function zmiAddPages(result, siblings) {
	var html = "";
	$("page",result).each(function() {
			var abs_url = $(this).attr("absolute_url");
			var link_url = abs_url;
			var extra = null;
			if ($(this).attr("meta_id")=='ZMSGraphic') {
				var $img = $("img",this);
				if ($img.length==1) {
					link_url = '<img src=&quot;'+abs_url+'/'+$("filename",$img).text()+'&quot;/>';
					var src = abs_url+'/'+$("filename",$img).text();
					var icon = $("icon",$img).text();
					var filename = $("filename",$img).text();
					var size = $("size",$img).text();
					extra = 'showPreviewZMSGraphic(\''+$(this).attr("id")+'\',\''+src+'\',\''+icon+'\',\''+filename+'\',\''+size+'\');';
				}
			}
			else if ($(this).attr("meta_id")=='ZMSFile') {
				var $file = $("file",this);
				if ($file.length==1) {
					link_url = '<a href=&quot;'+abs_url+'/'+$("filename",$file).text()+'&quot; target=&quot;_blank&quot;><img src=&quot;'+$("icon",$file).text()+'&quot; title=&quot;'+$("content_type",$file).text()+'&quot; border=&quot;0&quot; align=&quot;absmiddle&quot;> '+$(this).attr("title")+' ('+$("size",$file).text()+')</a>';
					var src = abs_url+'/'+$("filename",$file).text();
					var icon = $("icon",$file).text();
					var filename = $("filename",$file).text();
					var size = $("size",$file).text();
					extra = 'showPreviewZMSFile(\''+$(this).attr("id")+'\',\''+src+'\',\''+icon+'\',\''+filename+'\',\''+size+'\');';
				}
			}
			html += '<div id="div_'+$(this).attr("id")+'" style="padding:1px 2px 1px 8px; margin:0">';
			html += '<span onclick="zmiExpandObject(\''+$(this).attr("id")+'\',\''+abs_url+'\',\''+$(this).attr("meta_id")+'\');" style="cursor:pointer">';
			html += '<img src="/misc_/zms/pl.gif" title="+" border="0" align="absmiddle"/>';
			html += '</span>';
			html += '<span onclick="zmiSelectObject(\''+$(this).attr("id")+'\',\''+link_url+'\',\''+$(this).attr("meta_id")+'\');" style="cursor:pointer;text-decoration:none;" class="zmi">';
			html += '<img src="'+$(this).attr("display_icon")+'" title="'+$(this).attr("display_type")+'" align="absmiddle"/>';
			html += $(this).attr("titlealt");
			if (extra != null) {
				html += '<span title="Preview..." onmouseover="'+extra+'" onmouseout="hidePreview(\''+$(this).attr("id")+'\');"> ...</span>';
			}
			html += '</span>';
			if (extra != null) {
				html += '<div id="CKEDITOR_preview_'+$(this).attr("id")+'" class="form-small ui-helper-hidden" style="padding-left:16px"></div>';
			}
			html += '<div id="div_'+$(this).attr("id")+'_children" style="'+(siblings?'display:none;':'')+'padding:1px 2px 1px 8px; margin:0">';
			if (siblings) {
				html += '</div>';
				html += '</div>';
			}
		});
	$("page",result).each(function() {
			if (!siblings) {
				html += '</div>';
				html += '</div>';
			}
		});
	return html;
}

function zmiExpandObject(id,abs_url,meta_id) {
	var $img = $("#div_"+id+" img:first");
	if ($img.attr("title").length==1) {
		var $div = $("#div_"+id+"_children");
		if ($img.attr("title")=="+") {
			$div.show("normal");
			$img.attr({src:"/misc_/zms/mi.gif",title:"-"});
			var href = abs_url + "/ajaxGetChildNodes";
			$.get(href,{lang:zmiParams["lang"]},function(result) {
					var html = zmiAddPages(result,true);
					if (html.length==0) {
						$img.attr({src:"/misc_/zms/spacer.gif",title:""}).css({width:"16px",height:"16px"});
					}
					$div.html(html).addClass("loaded");
				});
		}
		else {
			$div.hide("normal");
			$img.attr({src:"/misc_/zms/pl.gif",title:"+"});
		}
	}
}

function zmiSelectObject(id,abs_url,meta_id) {
	zmiDialog.getContentElement('tab1', 'inp_url').setValue(abs_url);
	zmiDialog.click("ok");
}

CKEDITOR.dialog.add( 'linkbuttonDlg', function( editor ) {
	return { 
		title:  getZMILangStr('CAPTION_CHOOSEOBJ'),
 
		minWidth: 200,
		minHeight: 80,
 
 
		contents: [ 
			{
				id: 'tab1',
				label: 'Tab1',
				title: 'Tab1',
				elements : [ 
					{
						id: 'inp_url',
						type: 'text',
						label: "URL",
						validate : function() {
							// potentielle Validierungen
							if (this.getValue() == "") {
								alert("Das Feld darf nicht leer sein!");
							}
							return this.getValue() != "";
						}
					},
					{
						type: 'html',
						html : '<div id="myDiv"></div>'
					}
				 ]
			}
		 ],

			onLoad: function() {
					zmiDialog = this;
					var href = self.location.href;
					href = href.substr(0,href.lastIndexOf("/"))+"/ajaxGetParentNodes";
					$.get(href,{lang:zmiParams["lang"]},function(result) {
							var html = zmiAddPages(result,false);
							$("#myDiv").html(html);
						});
				},

			onOk: function() {
					var selectedText = editor.getSelection().getNative();
					var url = this.getContentElement('tab1', 'inp_url').getValue();
					var text = url;
					if ((""+selectedText).length>0) {
						text = selectedText;
					}
					var html = '';
					if (url.indexOf("<")==0) {
						html += url;
					}
					else {
						html += '<a href="'+url+'">'+text+'</a>';
					}
					var element = CKEDITOR.dom.element.createFromHtml(html);
					editor.insertElement(element);
			 }
 
	};
 
} );