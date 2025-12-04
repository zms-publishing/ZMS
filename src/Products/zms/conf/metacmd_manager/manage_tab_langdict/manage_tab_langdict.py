## Script (Python) "manage_tab_langdict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=TAB_LANGUAGES
##
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE
langIds = context.getLangIds(sort=True)
xml = context.getMetaobjManager().exportMetaobjXml(ids=[context.meta_id])
rs = standard.distinct_list([x.split(',')[0] for x in standard.re_search('getLangStr\((.*?)\)',xml) if len(x.split(','))==2])
rs = [x[1:-1] for x in rs if len(x)>2 and x[0] in ["'",'"'] and x[0] == x[-1]]
rs.sort()

prt = []
prt.append('<!DOCTYPE html>')
prt.append('<html lang="en">')
prt.append(context.zmi_html_head(context,request))
prt.append('<body class="%s">'%context.zmi_body_class(id='tab_languages'))
prt.append(context.zmi_body_header(context,request))
prt.append('<div id="zmi-tab">')
prt.append(context.zmi_breadcrumbs(context,request))
prt.append('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
prt.append('<input type="hidden" name="id" value="manage_tab_langdict"/>')
prt.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
prt.append('<legend>%s</legend>'%context.getZMILangStr('ATTR_DICTIONARY'))
prt.append('<div class="card-body">')

# --- Save.
# ---------------------------------
if request.form.get('btn')=='BTN_SAVE':
	message = []
	message.append('%s (%i)'%(context.getZMILangStr('MSG_CHANGED'),c))
	request.response.redirect(context.url_append_params('manage_main',{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(message)}))

# --- Display initial insert form.
# ---------------------------------
else:
	prt.append('<table class="table table-sm table-striped table-bordered table-hover">')
	prt.append('<thead>')
	prt.append('<tr>')
	prt.append('<th>%s</th>'%context.getZMILangStr('ATTR_KEY'))
	prt.extend(['<th>%s</th>'%context.getLanguageLabel(x) for x in langIds])
	prt.append('</tr>')
	prt.append('</thead>')
	prt.append('<tbody>')
	for ri in rs:
		prt.append('<tr>')
		prt.append('<td>%s</td>'%str(ri))
		prt.extend(['<td><div class="single-line"><textarea class="form-control form-control-sm" name="%s" placeholder="%s">%s</textarea></div></td>'%(ri+'_'+x[0],x[1],[x[1],''][int(ri==x[1])]) for x in [(y,context.getLangStr(bytes(ri,'utf-8'),y)) for y in langIds]])
		prt.append('</tr>')
	prt.append('</tbody>')
	prt.append('</table>')
	prt.append('<div class="form-group row">')
	prt.append('<div class="controls save">')
	prt.append('<button type="submit" name="btn" class="btn btn-primary" value="BTN_SAVE">%s</button> '%context.getZMILangStr('BTN_SAVE'))
	prt.append('<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button> '%context.getZMILangStr('BTN_CANCEL'))
	prt.append('</div><!-- .controls.save -->')
	prt.append('</div><!-- .form-group -->')

# ---------------------------------

prt.append('</div><!-- .card-body -->')
prt.append('</form><!-- .form-horizontal -->')
prt.append('</div><!-- #zmi-tab -->')
prt.append(context.zmi_body_footer(context,request))
prt.append('</body>')
prt.append('</html>')

return '\n'.join(prt)
