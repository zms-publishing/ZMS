CKEDITOR.dialog.add( 'mediabuttonDlg', function( editor )
{
	var commonLang = editor.lang.common,
		linkLang = editor.lang.link;

	return {
		title : getZMILangStr('CAPTION_CHOOSEOBJ'),
		minWidth : 280,
		minHeight : 80,
		contents : [
			{
				id : 'info',
				label : linkLang.info,
				title : linkLang.info,
				elements :
				[
					{
						type : 'file',
						id : 'file',
						label : getZMILangStr('ATTR_FILE'),
						required: true
					},
					{
						type : 'checkbox',
						id : 'thumbnail',
						label : getZMILangStr('ACTION_GENERATE_PREVIEW'),
						'default' : 'checked'
					}
				]
			}
		],
		onOk : function()
		{
		}
	};
});
