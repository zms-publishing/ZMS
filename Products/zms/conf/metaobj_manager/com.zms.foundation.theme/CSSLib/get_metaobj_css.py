## Script (Python) "CSSLib.get_metaobj_css"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=meta_id='CSSLib', css_attr='default_scss', syntax='scss'
##title=
##
# --// get_metaobj_css //--
request = container.REQUEST
response =  request.response
zms = context.content
attr_obj = zms.getMetaobjAttr(meta_id,css_attr)

if attr_obj['type'] == 'resource': # file type attribute
    try:
        css = str(attr_obj['ob'])
    except:
        css = str('/* ATTRIBUTE-ERROR: %s */'%(attr_obj['id']))
else:
    css = str(attr_obj['custom'])

if syntax=='scss':
    css = context.compile_scss(scss=css)

response.setHeader('Content-Type', 'text/css')
return css

# --// /get_metaobj_csss //--
