#!/usr/bin/python
# -*- coding: utf-8 -*-
from io import BytesIO
from PIL import Image, IptcImagePlugin
from PIL.ExifTags import TAGS
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
	if request.form.get('btn')=='BTN_UPLOAD':
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

				# Extracting EXIF/IPTC Data
				exif_data = {}
				copy = desc = ''
				img_attrs_spec = 'alt=\042%s\042 '%(str(file.filename))

				try:
					image = Image.open(BytesIO(data))

					# https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#metadata-properties
					iptc_data = IptcImagePlugin.getiptcinfo(image)
					if iptc_data:
						iptc_title = iptc_data.get((2, 5))  # https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#title
						iptc_headline = iptc_data.get((2, 105))  # https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#headline
						iptc_description = iptc_data.get((2, 120))  # https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#description
						iptc_copright = iptc_data.get((2, 116))  # https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#copyright-notice
						iptc_creator = iptc_data.get((2, 80))  # https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#creator

						if iptc_description is not None:
							desc = iptc_description.decode()
						if iptc_title is not None and iptc_title.decode() not in desc:
							desc = f'{iptc_title.decode()} {desc}'
						if iptc_headline is not None and iptc_headline.decode() not in desc:
							desc = f'{iptc_headline.decode()} {desc}'

						if iptc_copright is not None:
							copy = iptc_copright.decode()
						if iptc_creator is not None and iptc_creator.decode() not in copy:
							copy = f'{copy} {iptc_creator.decode()}'

						desc = desc.strip()
						copy = copy.strip()
						copy = not copy.startswith('©') and '© ' + copy or copy

					# https://pillow.readthedocs.io/en/stable/reference/ExifTags.html
					if image.getexif() is not None:
						for tag, value in image.getexif().items():
							if tag in TAGS:
								exif_data[TAGS[tag]] = value

					if desc.strip() == '':
						if 'ImageDescription' in exif_data:
							exif_description = exif_data['ImageDescription'].encode('latin-1').decode()
							if '©' in exif_description:
								desc, copy = exif_description.split('©')

					if copy.strip() == '':
						if 'Copyright' in exif_data:
							exif_copyright = exif_data['Copyright'].encode('latin-1').decode()
							if exif_copyright.strip() != '':
								copy = not exif_copyright.startswith('©') and '© ' + exif_copyright or exif_copyright

					img_attrs_spec += '\n'.join([ 'data-EXIF-%s =\042%s\042 ' %(k, exif_data[k]) for k in exif_data.keys() ])

				except:
					pass

				newobj = self.manage_addZMSCustom(
					'ZMSGraphic',{
						'id_prefix':id_prefix, 
						'img_attrs_spec':img_attrs_spec, 
						'align':'LEFT',
						'text': desc.strip(),
						'imghires':blob, 
					}, request)

			##################
			# OTHER FILE
			##################
			else:
				newobj = self.manage_addZMSCustom('ZMSFile',{ 'id_prefix':id_prefix, 'title':file.filename, 'titlealt':file.filename, 'file':blob, 'align':'LEFT', },request)

			msg.append(self.getZMILangStr('MSG_IMPORTED')%('%s (%s)'%(file.filename,content_type))+' [%i/%i]'%(c,len(files)))

		msg.append('<br/>')
		html += '<div class="alert alert-success">%s</div><!-- .alert.alert-success -->'%('<br/>')
		request.response.redirect(standard.url_append_params('%s/manage_main'%self.absolute_url(),{'lang':request['lang'],'manage_tabs_message':'<br/>'.join(msg)}))

	# --- Display initial import form.
	# ---------------------------------
	else:

		html += """
			<div class="form-group row"">
				<div class="col-sm-12">
					<input id="file" style="height:2.55rem;" name="file" type="file" class="form-control file" multiple="true" data-show-upload="false" data-show-caption="true" />
				</div>'
			</div><!-- .form-group -->
			<div class="form-row">
				<div class="controls save py-3 px-1">
					<button type="submit" name="btn" class="btn btn-primary" value="BTN_UPLOAD">%s</button>
					<button type="submit" name="btn" class="btn btn-secondary" value="BTN_CANCEL">%s</button>
				</div>
			</div><!-- .form-group -->
			"""%(self.getZMILangStr('BTN_UPLOAD'), self.getZMILangStr('BTN_CANCEL'))

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