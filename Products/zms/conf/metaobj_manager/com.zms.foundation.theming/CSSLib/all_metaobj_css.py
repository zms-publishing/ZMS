## Script (Python) "CSSLib.all_metaobj_css"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Aggregate All Default CSS
##
# --// all_default_css //--
request = container.REQUEST
response =  request.response
zms = context.content
css_list = []
for meta_id in zms.getMetaobjIds():
    css_attrs = [id for id in zms.getMetaobjAttrIds(meta_id) if ('default' in id and ('_css' in id or '_scss' in id)) ]
    for css_attr in css_attrs:
        syntax = '_css' in css_attr and 'css' or 'scss'
        css_list.append('\n\n/* %s.%s (%s) */'%(meta_id, css_attr, syntax))
        css_list.append(getattr(context.content.metaobj_manager,'CSSLib.get_metaobj_css')(meta_id=meta_id,css_attr=css_attr,syntax=syntax))

response.setHeader('Content-Type', 'text/css')
return '\n'.join(css_list)

# --// /all_default_css //--
