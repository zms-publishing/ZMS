/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';

  // Linkbutton: @see http://stackoverflow.com/questions/1957156/ckeditor-how-to-add-a-custom-button-to-the-toolbar-that-calls-a-javascript-funct
  config.extraPlugins = 'linkbutton,tableresize';

  // skins
  config.skin = getZMIConfProperty("CKEDITOR.config.skin","kama");

  //  Toolbar: @see http://docs.cksource.com/CKEditor_3.x/Developers_Guide/Toolbar
  config.toolbar = 'ZMSBasicToolbar';
  config.toolbar_ZMSBasicToolbar =[
     ['Format'],
     ['Bold','Italic','Underline','NumberedList','BulletedList'],
     ['Undo','Redo'],
     ['Find','linkbutton','Link','Unlink'],
     ['Anchor','Table'],
     ['Source','ShowBlocks','Maximize','About']
  ];
};
