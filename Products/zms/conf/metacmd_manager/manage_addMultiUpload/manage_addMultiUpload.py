#!/usr/bin/python
# -*- coding: utf-8 -*-
from Products.zms import standard

def manage_addMultiUpload(self):
	request = self.REQUEST
	html = ''
	html += '<!DOCTYPE html>'
	html += '<html lang="en">'
	html += self.zmi_html_head(self,request)
	html += '<body class="%s">'%(' '.join(['zmi',request['lang'],'transition',self.meta_id]))
	html += self.zmi_body_header(self,request,options=[{'action':'#','label':'Multi-Upload...'}])
	html += '<div id="zmi-tab">'
	html += self.zmi_breadcrumbs(self,request)

	html += '<form class="form-horizontal card" method="post" enctype="multipart/form-data">'
	html += '<input type="hidden" name="form_id" value="manage_addMultiUpload" />'
	html += '<input type="hidden" name="lang" value="%s" />'%request['lang']
	html += '<legend>Multi-File-Upload</legend>'
	html += '<div class="card-body" style="min-height:20rem">'
	html += self.zmi_form_section_begin(self,request)

	# --- Import
	# ---------------------------------
	if request.form.get('btn')=='BTN_IMPORT':
		id_prefix = 'e'
		msg = []
		files = request.get('file',[])
		if not type(files) is list: files = [files]
		c = 0
		for file in files:
			c += 1
			blob = self.FileFromData(file,file.filename)
			data = blob.getData()
			content_type = blob.getContentType()
			##################
			# HTML/TEXT
			##################
			if content_type == 'text/html':
				newobj = self.manage_addZMSCustom('ZMSTextarea',{ 'id_prefix':id_prefix, 'text':file, 'format':'plain_html', },request)
				text = standard.pystr(data)
				# Post-Process HTML
				i = text.lower().find('<body')
				if i >= 0:
					text = text[i:]
					text = text[text.find('>')+1:]
					i = text.lower().find('</body')
					if i >= 0:
						text = text[:i]
					newobj.setObjStateModified(request)
					newobj.setObjProperty('text',text,forced=True)
					newobj.onChangeObj(request)
			##################
			# IMAGE
			##################
			elif content_type.startswith('image/'):
				request.set('generate_preview_imghires_%s'%request.get('lang','ger'),True)
				newobj = self.manage_addZMSCustom('ZMSGraphic',{'id_prefix':id_prefix, 'img_attrs_spec':'alt=\042'+str(file.filename)+'\042', 'imghires':blob, },request)
			##################
			# OTHER FILE
			##################
			else:
				newobj = self.manage_addZMSCustom('ZMSFile',{ 'id_prefix':id_prefix, 'title':file.filename, 'titlealt':file.filename, 'file':blob, 'align':'LEFT', },request)

			msg.append(self.getZMILangStr('MSG_IMPORTED')%('%s (%s)'%(file.filename,content_type))+' [%i/%i]'%(c,len(files)))

		msg.append('<br/>')
		html += '<div class="alert alert-success">%s</div><!-- .alert.alert-success -->'%('<br/>')
		request.response.redirect(self.url_append_params('%s/manage_main'%self.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(msg)}))

	# --- Display initial import form.
	# ---------------------------------
	else:

		html += '<div class="form-group row"">'
		html += '<div class="col-sm-12">'
		html += '<input id="file" style="height:2.55rem;" name="file" type="file" class="form-control file" multiple="true" data-show-upload="false" data-show-caption="true" />'
		html += '</div>'
		html += '</div><!-- .form-group -->'

		html += """
			<div class="form-row">
				<div class="controls save py-3 px-1">
					<button type="submit" name="btn" class="btn btn-primary" value="BTN_IMPORT">%s</button>
					<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>
				</div>
			</div><!-- .form-group -->
			"""%(self.getZMILangStr('BTN_IMPORT'),self.getZMILangStr('BTN_CANCEL'))

	# ---------------------------------

	html += '</form><!-- .form-horizontal -->'
	html += '</div><!-- .card -->'
	html += '</div><!-- #zmi-tab -->'
	html += self.zmi_body_footer(self,request)

	html += '''
		<!-- Optional: Applying Bootstrap Fileinput Plugin https://github.com/kartik-v/bootstrap-fileinput --> 
		<link href="/++resource++zms_/fileupload/bootstrap_fileinput/fileinput.css" media="all" rel="stylesheet" type="text/css" />'
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/buffer.js" type="text/javascript"></script>
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/filetype.js" type="text/javascript"></script>
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/piexif.js" type="text/javascript"></script>
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/sortable.js" type="text/javascript"></script>
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/fileinput.js" type="text/javascript"></script>
		<script defer src="/++resource++zms_/fileupload/bootstrap_fileinput/theme.js" type="text/javascript"></script>
		<style>
			/* Fix Plugin Styles */
			.file-input .file-preview .fileinput-remove {
				top: .5rem !important;
				right: .5rem !important;
			}
			.file-input .file-caption {
				margin-top: 1rem !important;
			}
		</style>
		<script>
			$(document).ready(function() {
				// Initialize Plugin with Defaults
				$("#file").fileinput({
					theme: 'fa5',
				});
			});
		</script>
	'''
	html +='</body></html>'
	return html