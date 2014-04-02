## Script (Python) "manage_transferContent.mapping"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
m =  {
  'case':{
    'meta_id':'ZMSDocument',
    'attrs':{
      'case_customer':'attr_dc_subject',
      'case_screen':'e',
      'case_specials':'e',
    },
  },
  'ZMSTextarea': {
    'meta_id':'ZMSTextarea',
    'attrs':{
      'text':'text',
    },
  },
}
return m