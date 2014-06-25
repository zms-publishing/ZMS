/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For the complete reference:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config
	config.emailProtection = 'encode';
	config.forcePasteAsPlainText = true

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbarGroups = [
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
		{ name: 'links' },
		{ name: 'insert' },
		{ name: 'forms' },
		{ name: 'tools' },
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'others' },
		'/',
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
		{ name: 'styles' },
		{ name: 'colors' },
		{ name: 'about' }
	];

	// Remove some buttons, provided by the standard plugins, which we don't
	// need to have in the Standard(s) toolbar.
	config.removeButtons = 'Subscript,Superscript';

	// Set the most common block elements.
	$ZMI.CKEDITOR_editorConfig(config);

	// Make dialogs simpler.
	config.removeDialogTabs = 'image:advanced;link:advanced';

  // Linkbutton
  // Mediabutton
  // @see http://stackoverflow.com/questions/1957156/ckeditor-how-to-add-a-custom-button-to-the-toolbar-that-calls-a-javascript-funct
  config.extraPlugins = 'linkbutton,mediabutton,tableresize';

  //  Toolbar: @see http://docs.cksource.com/CKEditor_3.x/Developers_Guide/Toolbar
  config.toolbar = 'ZMSBasicToolbar';
  config.toolbar_ZMSBasicToolbar =[
     ['Format'],
     ['Bold','Italic','Underline','NumberedList','BulletedList','Outdent','Indent'],
     ['Undo','Redo'],
     ['Find','linkbutton','Link','Unlink'],
     ['Image','Anchor','Table'],
     ['Source','ShowBlocks','Maximize','About']
  ];
  config.toolbar_ZMSBasicInsertToolbar =[
     ['Format'],
     ['Bold','Italic','Underline','NumberedList','BulletedList','Outdent','Indent'],
     ['Undo','Redo'],
     [],
     [],
     ['ShowBlocks','Maximize','About']
  ];
};

CKEDITOR.on( 'dialogDefinition', function( event ) {
    var dialogDefinition = event.data.definition,
        genericOnShow = dialogDefinition.onShow;
      dialogDefinition.onShow = function() {
          genericOnShow.apply( this );
            var dialog = CKEDITOR.dialog.getCurrent();
            if (dialog.getName() == 'link') {
              subject = dialog.getContentElement('info','emailSubject');
              if (subject.getValue() == '') {
                subject.setValue(' ');
              }
            }
      }
});
