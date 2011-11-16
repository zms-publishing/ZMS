var zmiDialog = null;
var zmiSelectedText = null;

function showPreviewZMSGraphic(el,src,icon,filename,size) {
	var html= '';
	html += '<div class="img_head"><img src="'+icon+'" border="0" align="absmiddle"/> '+filename+' ('+size+')</div>';
	html += '<div class="img_img"><img src="'+src+'" border="0" align="absmiddle" style="max-width:200px;"/></div>';
	showPreview(el,html);
}

function showPreviewZMSFile(el,href,icon,filename,size) {
	var html= '';
	html += '<div class="file_head"><a href="'+href+'" target="_blank" class="zmi"><img src="'+icon+'" border="0" align="absmiddle"/> '+filename+' ('+size+')</a></div>';
	showPreview(el,html);
}

function showPreview(el,html) {
	var coords = $(el).offset();
	if ($("div#CKEDITOR_preview").length==0) {
		$('body').append('<div id="CKEDITOR_preview" class="form-small ui-helper-hidden" style="z-index:99999;background-color:white;position:absolute;"></div>');
	}
	$("div#CKEDITOR_preview").html(html).css({left:coords.left+20,top:coords.top+20}).show();
}

function hidePreview() {
	$("div#CKEDITOR_preview").hide();
}

function zmiAddPages(result, siblings) {
	var html = "";
	$("page",result).each(function() {
			var titlealt = "";
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
					titlealt = filename;
					extra = 'showPreviewZMSGraphic(this,\''+src+'\',\''+icon+'\',\''+filename+'\',\''+size+'\');';
				}
			}
			else if ($(this).attr("meta_id")=='ZMSFile') {
				var $file = $("file",this);
				if ($file.length==1) {
					var $fname = $("filename",$file).text();
					var $ext = $fname.substring($fname.lastIndexOf('.')+1,$fname.length);
					link_url = '<a href=&quot;'+abs_url+'/'+$("filename",$file).text()+'&quot; target=&quot;_blank&quot;>'+$(this).attr("title")+' ('+$ext+', '+$("size",$file).text()+')</a>'; 
					var src = abs_url+'/'+$("filename",$file).text();
					var icon = $("icon",$file).text();
					var filename = $("filename",$file).text();
					var size = $("size",$file).text();
					titlealt = filename;
					extra = 'showPreviewZMSFile(this,\''+src+'\',\''+icon+'\',\''+filename+'\',\''+size+'\');';
				}
			}
			var id = $(this).attr("id").replace(/\./gi,"_").replace(/\-/gi,"_");
			html += '<div id="div_'+id+'" style="padding:1px 2px 1px 8px; margin:0">';
			html += '<span onclick="zmiExpandObject(\''+id+'\',\''+abs_url+'\',\''+$(this).attr("meta_id")+'\');" style="cursor:pointer">';
			html += '<img src="/misc_/zms/pl.gif" title="+" border="0" align="absmiddle"/>';
			html += '</span>';
			html += '<span onclick="zmiSelectObject(\''+id+'\',\''+link_url+'\',\''+$(this).attr("meta_id")+'\');" style="cursor:pointer;text-decoration:none;" class="zmi">';
			html += '<img src="'+$(this).attr("display_icon")+'" title="'+$(this).attr("display_type")+'" align="absmiddle"/>';
			if (extra != null) {
				html += '<span class="ui-helper-clickable" onmouseover="'+extra+'" onmouseout="hidePreview();">&dArr;</span>';
			}
			if (titlealt=="") {
				titlealt = $(this).attr("titlealt");
			}
			html += titlealt;
			html += '</span>';
			html += '<div id="div_'+id+'_children" style="'+(siblings?'display:none;':'')+'padding:1px 2px 1px 8px; margin:0">';
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
			$div.html('<img src="/misc_/zms/loading_16x16.gif" alt="" border="0" align="absmiddle"/> '+getZMILangStr('MSG_LOADING')).show("normal");
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
		zmiResizeObject();
	}
}

function zmiSelectObject(id,abs_url,meta_id) {
	zmiDialog.getContentElement('tab1', 'inp_url').setValue(abs_url);
	zmiDialog.click("ok");
}

function zmiResizeObject() {
	var $myDiv = $("#myDiv");
	var $cke_dialog_footer = $(".cke_dialog_footer");
	var height = $cke_dialog_footer.offset().top-$myDiv.offset().top-10;
	$myDiv.css("height",height);
}

CKEDITOR.dialog.add( 'linkbuttonDlg', function( editor ) {
	return { 
		title:  getZMILangStr('CAPTION_CHOOSEOBJ'),
		minWidth: 250,
		minHeight: 180,
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
						html : '<div id="myDiv" style="overflow:auto"></div>'
					}
				 ]
			}
		 ],

			onShow: function() {
					var selection = editor.getSelection();
					if (CKEDITOR.env.ie) {
						zmiSelectedText = selection.document.$.selection.createRange().text;
					} else {
						zmiSelectedText = selection.getNative();
					}
			},

			onLoad: function() {
					zmiDialog = this;
					zmiDialog.on("resize",function(event){zmiResizeObject()});
					zmiResizeObject();
					var href = self.location.href;
					href = href.substr(0,href.lastIndexOf("/"))+"/ajaxGetParentNodes";
					$('#myDiv').html('<img src="/misc_/zms/loading_16x16.gif" alt="" border="0" align="absmiddle"/> '+getZMILangStr('MSG_LOADING'));
					$.get(href,{lang:zmiParams["lang"]},function(result) {
							var html = zmiAddPages(result,false);
							$("#myDiv").html(html);
							// Open siblings of current page-element.
							var last_page_id = $("page[is_page=1]:last",result).attr("id");
							$("div#div_"+last_page_id+" > span:first").click();
						});
				},

			onOk: function() {
					var selectedText = zmiSelectedText;
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
