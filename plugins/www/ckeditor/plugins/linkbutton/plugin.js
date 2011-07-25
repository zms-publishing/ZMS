/**
 * @see http://www.pro4j.de/erstellen-eines-plugins-fur-den-ckeditor-30
 */
CKEDITOR.plugins.add('linkbutton', {
	init : function( editor )
	{
		editor.addCommand( 'linkbuttonDlg', new CKEDITOR.dialogCommand( 'linkbuttonDlg' ) );
 
		editor.ui.addButton( 'linkbutton',
			{
				label : 'Internal Link',
				command : 'linkbuttonDlg',
				icon: this.path + 'images/anchor.png',
			});

		// @todo: remove ts (debugging only!)
		CKEDITOR.dialog.add( 'linkbuttonDlg', this.path+'dialogs/link.js?ts='+new Date());

	}
});