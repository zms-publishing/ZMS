## Script (Python) "tryout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=TEST
##
# --// tryout //--
from Products.zms import standard
request = container.REQUEST
zmscontext = context.content

lang = zmscontext.getPrimaryLanguage()
request.set('lang',lang)

teasers = zmscontext.getTreeNodes(request,meta_types=['ZMSTeaserElement'])

for teaser in teasers:
    html = teaser.getBodyContent(request)

    context.teaser_registry.sql_upsert(
        zms_id = zmscontext.getId(),
        client_id = zmscontext.getHome().getId(),
        uuid = zmscontext.get_uid(),
        change_dt = zmscontext.attr('change_dt'),
        lang = lang,
        content_md5 = zmscontext.encrypt_password(html, algorithm='md5', hex=True),
        content_datetime = zmscontext.attr('change_dt'),
        content_cache = html
    )

return container.index_html()

# --// /tryout //--
