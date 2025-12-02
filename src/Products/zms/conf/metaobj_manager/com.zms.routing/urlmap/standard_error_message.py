## Script (Python) "standard_error_message"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=error_type='',error_value='',error_tb='',error_traceback='',error_message='',error_log_url=''
##title=ERROR HANDLER
##
# --// standard_error_message //--
request = container.REQUEST
response =  request.response
try:
    zmscontext=context.content
except:
    zmscontext=context
text = error_message
if (error_type == 'NotFound') and ('came_from' not in request.get('URL')):
    try:
        # Hint request.URL omits the index-suffix like './index_ger.html'
        req_target = container.url_mapping.get_url_by_key(url_key=request.get('URL'),zmscontext=zmscontext)
        response.redirect(req_target,status=301,lock=True)
    except:
        response.redirect('%s?info=ex'%(container.standard_error_messages.error_404.absolute_url()))
else:
    print(text)
    return printed

# --// /standard_error_message //--
