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

/**
 * Select object.
 */
function zmiSelectObject(sender) {
	var uid = $(sender).attr('data-uid');
	var abs_url = $(sender).attr('href');
	data_id = uid;
	zmiDialog.getContentElement('info', 'url').setValue(abs_url);
	zmiDialog.click("ok");
	return false;
}

/**
 * Resize object.
 */
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
							href = href.substr(0,href.lastIndexOf("/"));
							$ZMI.objectTree.init("#myDiv",href,{'toggleClick.callback':'zmiResizeObject'});
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
						html : '<div id="myDiv" class="zmi-sitemap" style="overflow:auto"></div>'
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