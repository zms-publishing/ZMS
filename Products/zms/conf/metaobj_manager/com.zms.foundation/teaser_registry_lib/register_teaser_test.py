## Script (Python) "register_teaser_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=TEST
##
# --// register_teaser_test //--
from Products.zms import standard
request = container.REQUEST
zms = context.content
zmscontext = zms.e149.teaser_item152

lang = request.get('lang','ger')
html = zmscontext.getBodyContent(request) 

context.teaser_registry.sqlite_db_upsert_sql(
        zms_id = zmscontext.getId(),
        client_id = zmscontext.getHome().getId(),
        uuid = zmscontext.get_uid(),
        change_dt = zmscontext.attr('change_dt'),
        lang = lang,
        content_md5 = zmscontext.encrypt_password(html, algorithm='md5', hex=True),
        content_datetime = zmscontext.attr('change_dt'),
        content_cache = html
)

return zmscontext.getId()

# --// /register_teaser_test //--
