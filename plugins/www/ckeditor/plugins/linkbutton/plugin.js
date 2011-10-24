/**
 * @see http://www.pro4j.de/erstellen-eines-plugins-fur-den-ckeditor-30
 */
CKEDITOR.plugins.add('linkbutton', {
	init : function( editor )
	{
		editor.addCommand( 'linkbuttonDlg', new CKEDITOR.dialogCommand( 'linkbuttonDlg' ) );
 
		editor.ui.addButton( 'linkbutton',
			{
				label : 'Toolbox',
				command : 'linkbuttonDlg',
				icon: '/misc_/zms/btn_paste1.gif'
			});

		CKEDITOR.dialog.add( 'linkbuttonDlg', this.path+'dialogs/link.js?ts='+new Date());

	}
});
