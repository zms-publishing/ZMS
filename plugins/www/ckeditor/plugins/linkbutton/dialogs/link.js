var zmiDialog = null;

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
			var link_url = $(this).attr("index_html");
			var extra = null;
			if ($(this).attr("meta_id")=='ZMSGraphic') {
				var $img = $("img",this);
				if ($img.length==1) {
					link_url = '<img src=&quot;'+$("href",$img).text()+'&quot;>';
					var src = $("href",$img).text();
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
					link_url = '<a href=&quot;'+$("href",$file).text()+'&quot; target=&quot;_blank&quot;>'+$(this).attr("title")+' ('+$ext+', '+$("size",$file).text()+')</a>'; 
					var src = $("href",$file).text();
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
			html += $(this).attr("display_icon");
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
			$div.html('<i class="icon-spinner icon-spin"></i>&nbsp;&nbsp;'+getZMILangStr('MSG_LOADING')).show("normal");
			$img.attr({src:"/misc_/zms/mi.gif",title:"-"});
			var href = abs_url + "/ajaxGetChildNodes";
			$.get(href,{lang:getZMILang()},function(result) {
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
	zmiDialog.getContentElement('info', 'url').setValue(abs_url);
	zmiDialog.click("ok");
}

function zmiResizeObject() {
	var $myDiv = $("#myDiv");
	var $cke_dialog = $myDiv.parents(".cke_dialog");
	var $cke_dialog_footer = $(".cke_dialog_footer",$cke_dialog);
	var height = $cke_dialog_footer.offset().top-$myDiv.offset().top-10;
	$myDiv.css("height",height);
}

CKEDITOR.dialog.add( 'linkbuttonDlg', function( editor )
{
	var plugin = CKEDITOR.plugins.link;

	var parseLink = function( editor, element )
	{
		var href = '',
			retval = {};
		// Record down the selected element in the dialog.
		this._.selectedElement = element;
		return retval;
	};

	var commonLang = editor.lang.common,
		linkLang = editor.lang.link;

	return {
		title : getZMILangStr('CAPTION_CHOOSEOBJ'),
		minWidth : 250,
		minHeight : 180,
		contents : [
			{
				id : 'info',
				label : linkLang.info,
				title : linkLang.info,
				elements :
				[
					{
						type : 'text',
						id : 'url',
						label : commonLang.url,
						required: true,
						onLoad : function ()
						{
							this.allowOnChange = true;
							zmiDialog = this.getDialog();
							zmiDialog.on("resize",function(event){zmiResizeObject()});
							zmiResizeObject();
							var href = self.location.href;
							href = href.substr(0,href.lastIndexOf("/"))+"/ajaxGetParentNodes";
							$('#myDiv').html('<i class="icon-spinner icon-spin"></i>&nbsp;&nbsp;'+getZMILangStr('MSG_LOADING'));
							$.get(href,{lang:getZMILang()},function(result) {
									var html = zmiAddPages(result,false);
									$("#myDiv").html(html);
									// Open siblings of current page-element.
									var last_page_id = $("page[is_page=1]:last",result).attr("id");
									$("div#div_"+last_page_id+" > span:first").click();
								});
						},
						validate : function()
						{
							var dialog = this.getDialog();
							var func = CKEDITOR.dialog.validate.notEmpty( linkLang.noUrl );
							return func.apply( this );
						},
						setup : function( data )
						{
							this.allowOnChange = false;
							if ( data.url )
								this.setValue( data.url.url );
							this.allowOnChange = true;
						},
						commit : function( data )
						{
							if ( !data.url )
								data.url = {};
							data.url.url = this.getValue();
							this.allowOnChange = false;
						}
					},
					{
						type: 'html',
						html : '<div id="myDiv" style="overflow:auto"></div>'
					}
				]
			}
		],
		onShow : function()
		{
			var editor = this.getParentEditor(),
				selection = editor.getSelection(),
				element = null;

			// Fill in all the relevant fields if there's already one link selected.
			if ( ( element = plugin.getSelectedLink( editor ) ) && element.hasAttribute( 'href' ) )
				selection.selectElement( element );
			else
				element = null;

			this.setupContent( parseLink.apply( this, [ editor, element ] ) );
		},
		onOk : function()
		{
			var attributes = {},
				removeAttributes = [],
				data = {},
				me = this,
				editor = this.getParentEditor();

			this.commitContent( data );

			// Compose the URL.
			var url = ( data.url && CKEDITOR.tools.trim( data.url.url ) ) || '';

			if (url.indexOf("<") == 0) {
				var element = CKEDITOR.dom.element.createFromHtml(url);
				editor.insertElement(element);
			}
			else {
				attributes[ 'data-cke-saved-href' ] = url;
				// Browser need the "href" fro copy/paste link to work. (#6641)
				attributes.href = attributes[ 'data-cke-saved-href' ];
				// Create element if current selection is collapsed.
				var selection = editor.getSelection(),
					ranges = selection.getRanges( true );
				if ( ranges.length == 1 && ranges[0].collapsed ) {
					var text = new CKEDITOR.dom.text( attributes[ 'data-cke-saved-href' ], editor.document );
					ranges[0].insertNode( text );
					ranges[0].selectNodeContents( text );
					selection.selectRanges( ranges );
				}
				// Apply style.
				var style = new CKEDITOR.style( { element : 'a', attributes : attributes } );
				style.type = CKEDITOR.STYLE_INLINE;		// need to override... dunno why.
				style.apply( editor.document );
			}
		}
	};
});