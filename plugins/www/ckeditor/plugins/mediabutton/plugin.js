/**
 * @see http://www.pro4j.de/erstellen-eines-plugins-fur-den-ckeditor-30
 */
CKEDITOR.plugins.add('mediabutton', {
	init : function( editor )
	{
		editor.addCommand( 'mediabuttonDlg', new CKEDITOR.dialogCommand( 'mediabuttonDlg' ) );
 
		editor.ui.addButton( 'mediabutton',
			{
				label : getZMILangStr('BTN_UPLOAD')+'/'+getZMILangStr('BTN_INSERT'),
				command : 'mediabuttonDlg',
				icon: this.path+'images/media-button.png'
			});

		CKEDITOR.dialog.add( 'mediabuttonDlg', this.path+'dialogs/link.js?ts='+new Date());

	}
});
