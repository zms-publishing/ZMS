/**
 * @see http://www.pro4j.de/erstellen-eines-plugins-fur-den-ckeditor-30
 * @see http://docs.ckeditor.com/#!/guide/plugin_sdk_integration_with_acf
 */
CKEDITOR.plugins.add('linkbutton', {
	init : function( editor )
	{
		editor.addCommand( 'linkbuttonDlg', new CKEDITOR.dialogCommand( 'linkbuttonDlg', {
					allowedContent:'a[data-id,href]'
				}
		) );
 
		editor.ui.addButton( 'linkbutton',
			{
				label : 'Toolbox',
				command : 'linkbuttonDlg',
				icon: '/misc_/zms/btn_paste1.gif'
			});

		CKEDITOR.dialog.add( 'linkbuttonDlg', this.path+'dialogs/link.js?ts='+new Date());

	}
});
