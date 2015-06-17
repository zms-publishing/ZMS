var zmiDialog = null;
var data_id = null;

/**
 * Preview.
 */
function zmiPreview(sender) {
	var data_id = $(sender).closest('.zmi-page').attr('data-id');
	if($('#zmi_preview_'+data_id).length > 0) {
		$('#zmi_preview_'+data_id).remove();
	}
	else {
		var coords = $ZMI.getCoords(sender);
		var abs_url = $(sender).parent('div').children('[data-page-physical-path]').attr('data-page-physical-path');
		$.get(abs_url+'/ajaxGetBodyContent',{lang:getZMILang(),preview:'preview'},function(data){
				$('div.zmi-browse-iframe-preview').remove();
				$('body').append(''
						+'<div id="zmi_preview_'+data_id+'">'
							+'<div class="zmi-browse-iframe-preview">'
								+'<div class="bg-primary" style="margin:-1em -1em 0 -1em;padding:0 4px 2px 4px;cursor:pointer;text-align:right;font-size:smaller;" onclick="$(\'#zmi_preview_'+data_id+'\').remove()">'+$ZMI.icon("icon-remove")+' '+getZMILangStr('BTN_CLOSE')+'</div>'
								+data
							+'</div><!-- .zmi-browse-iframe-preview -->'
						+'</div><!-- #zmi-preview -->'
					);
				$('div.zmi-browse-iframe-preview').css({top:coords.y+$(sender).height(),left:coords.x+$(sender).width()});
			});
	}
}

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
			var page = this;
			var titlealt = "";
			var page_uid = $(page).attr("uid");
			var page_home_id = $(page).attr("home_id");
			var page_id = $(page).attr("id").substr(page_home_id.length+1);
			var page_absolute_url = $(page).attr("absolute_url");
			var page_physical_path = $(page).attr("physical_path");
			var link_url = $(page).attr("index_html");
			var page_is_page = $(page).attr("is_page")=='1' || $(page).attr("is_page")=='True';
			var page_meta_type = $(page).attr("meta_id");
			var page_titlealt = $(page).attr("titlealt");
			var page_display_icon = $(page).attr("display_icon");
			if ($(this).attr("meta_id")=='ZMSGraphic') {
				var $img = $("img",this);
				if ($img.length==1) {
					link_url = '<img src=&quot;'+$("href",$img).text()+'&quot;>';
					page_titlealt = filename;
				}
			}
			else if ($(this).attr("meta_id")=='ZMSFile') {
				var $file = $("file",this);
				if ($file.length==1) {
					var $fname = $("filename",$file).text();
					var $ext = $fname.substring($fname.lastIndexOf('.')+1,$fname.length);
					link_url = '<a href=&quot;'+$("href",$file).text()+'&quot; target=&quot;_blank&quot;>'+$(this).attr("title")+' ('+$ext+', '+$("size",$file).text()+')</a>'; 
					page_titlealt = filename;
				}
			}
			var id = $(this).attr("id").replace(/\./gi,"_").replace(/\-/gi,"_");
			html += '<div id="div_'+id+'" data-id="'+page_id+'" data-home-id="'+page_home_id+'" class="zmi-page" style="padding:1px 2px 1px 8px; margin:0">';
			html += '<span onclick="zmiExpandObject(\''+id+'\',\''+page_absolute_url+'\',\''+$(this).attr("meta_id")+'\');" style="cursor:pointer">';
			html += '<img src="/misc_/zms/pl.gif" title="+" border="0" align="absmiddle"/>';
			html += '</span>';
			if (!page_is_page) {
				html += '<span style="cursor:help" onclick="zmiPreview(this)">'+page_display_icon+'</span> ';
			}
			html += '<a href="#" onclick="return zmiSelectObject(\''+page_uid+'\',\''+link_url+'\',\''+page_meta_type+'\')"'
				+ ' data-page-physical-path="'+page_physical_path+'"'
				+ '>';
			if (page_is_page) {
				html += page_display_icon+' ';
			}
			html += page_titlealt;
			html += '</a>';
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
			$.get(href,{lang:getZMILang(),physical_path:$('meta[name=physical_path]').attr('content')},function(result) {
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
	data_id = id;
	zmiDialog.getContentElement('info', 'url').setValue(abs_url);
	zmiDialog.click("ok");
	return false;
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
				attributes[ 'data-id' ] = data_id;
				attributes[ 'data-cke-saved-href' ] = url;
				// Browser need the "href" for copy/paste link to work. (#6641)
				attributes.href = attributes[ 'data-cke-saved-href' ];
				// Create element if current selection is collapsed.
				var selection = editor.getSelection();
				var b = selection.getRanges()[0];
				if (b.collapsed ) {
					var a = new CKEDITOR.dom.text( attributes[ 'data-cke-saved-href' ], editor.document );
					b.insertNode(a);
					b.selectNodeContents(a);
				}
				// Apply style.
				var g = editor.document;
				var c = new CKEDITOR.style( { element : 'a', attributes : attributes } );
				c.type = CKEDITOR.STYLE_INLINE;		// need to override... dunno why.
				c.applyToRange(b,g);
				b.select();
			}
		}
	};
});