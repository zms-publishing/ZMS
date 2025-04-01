import time         # struct time
import DateTime     # time stamp
import json         # JSON formatting
from Products.zms import standard

# REFERENCES:
# ISSUE: https://github.com/idasm-unibe-ch/unibe-cms/issues/862
# PR: https://github.com/idasm-unibe-ch/unibe-cms/pull/866

class dotdict(dict):
	def __getattr__(self, attr):
		return self.get(attr)
	def __setattr__(self, attr, value):
		self[attr] = value
	def __delattr__(self, attr):
		del self[attr]

# Reset DST to -1 to avoid DST issues with time.mktime
def reset_dst(struct_time):
	struct_time_list = list(struct_time)
	struct_time_list[8] = -1  # Set tm_isdst to -1
	# Convert the list back to struct_time
	struct_time = time.struct_time(struct_time_list)
	return struct_time

# Check if the end date is older than given days
def get_age_expired(end_struct = None, expire_days = 720):
	# Params: end_struct = struct_time, expire_days = int
	# Return: tuple (age_days[int], is_expired[bool])
	if not end_struct:
		return (0, False)
	end_struct = reset_dst(end_struct)
	end_ts = time.mktime(end_struct)
	now_ts = DateTime.DateTime().timeTime()
	age_days = int((now_ts - end_ts) / (60 * 60 * 24))
	return (age_days, age_days > expire_days)


# ----------------------------------------
# Grading for Cleanup : keep = 0, check = 1, delete = 2
# ----------------------------------------
def get_cleanup_grading(e, request):
	# ----------------------------------------
	# Intial values
	# ----------------------------------------
	grading_value = 0
	grading_info = 'keep'
	grading_dict = {0: 'keep', 1: 'check', 2: 'delete'}
	now_ts = DateTime.DateTime().timeTime()
	age_days = 0
	is_inactive = False
	is_multilang_inactive = False
	is_too_old = False
	is_linked = True
	has_active_subpages = False
	has_inactive_parent = False
	has_active_local_subnodes = False

	# ----------------------------------------
	# Checking for inactivity, age and backlinks
	# ----------------------------------------
	# 1. Active
	is_inactive = e.attr('active') == 0
	lang_saved = request.get('lang')
	langs = e.getLangs()
	if len(langs) > 1:
		ll = []
		for lang in langs:
			request.set('lang',lang)
			lang_is_inactive = e.attr('active') and 1 or 0
			if lang_is_inactive==0:
				lang_is_inactive = get_age_expired(e.attr('attr_active_end'), expire_days=1)[1] and 1 or 0
			ll.append( lang_is_inactive )
		is_multilang_inactive = sum(ll) == 0
	else:
		is_multilang_inactive = is_inactive
	request.set('lang',lang_saved)

	# 2. Age
	last_change_struct = e.attr('change_dt') or e.attr('created_dt')
	if last_change_struct:
		age_days, is_too_old = get_age_expired(last_change_struct, expire_days=720)
	if e.attr('attr_active_end'):
		age_days, is_too_old = get_age_expired(e.attr('attr_active_end'), expire_days=720)

	# 3. Active local Sub-Nodes
	# Check if there are active sub-nodes in a different language 
	# declared as global (aka. local)
	primary_lang = e.getPrimaryLanguage()
	coverage = 'global.%s'%(primary_lang)

	# 4. Backlinks
	if not e.getRefByObjs(request):
		is_linked = False
	pageelms = e.getChildNodes(request,e.PAGEELEMENTS)
	if pageelms:
		for pageelm in pageelms:
			sub_coverage = pageelm.attr('attr_dc_coverage')
			if pageelm.getRefByObjs(request):
				is_linked = True
			if sub_coverage.startswith('global') and sub_coverage != coverage:
				has_active_local_subnodes = True
			if has_active_subpages and has_active_local_subnodes:
				break

	# 5. Active SUB-PAGES
	subpages = e.getChildNodes(request,e.PAGES)
	if subpages:
		for subpage in subpages:
			sub_coverage = subpage.attr('attr_dc_coverage')
			if subpage.attr('active') == 1:
				has_active_subpages = True
			if sub_coverage.startswith('global') and sub_coverage != coverage:
				has_active_local_subnodes = True
			if has_active_subpages and has_active_local_subnodes:
				break

	# 6. Inactive parent PAGE
	try:
		has_inactive_parent = len([ob for ob in e.breadcrumbs_obj_path() if not ob.isActive(request)]) > 0 
	except:
		has_inactive_parent = False

	# ----------------------------------------
	# Grading Value (0=keep, 1=check, 2=delete)
	# ----------------------------------------
	if is_multilang_inactive and is_too_old:
		grading_value = 2
		if (has_active_subpages or (has_active_local_subnodes and not has_inactive_parent)):
			grading_value = 1

	grading_info = grading_dict[grading_value]

	# ----------------------------------------
	# Data dictionary for cleanup grading
	# ----------------------------------------
	grading_datadict = {
		'zmsid': e.id,
		'meta_id': e.meta_id,
		'absolute_url': '/%s'%(e.absolute_url(relative=1)), # get obj by restrictedTraverse()
		'lang': request.get('lang'),
		'primary_lang': primary_lang,
		'coverage': coverage,
		'title': e.getTitlealt(request),
		'grading': grading_value,
		'grading_info': grading_info.upper(),
		'age_days': age_days,
		'is_inactive': is_inactive,
		'is_multilang_inactive': is_multilang_inactive,
		'is_too_old': is_too_old,
		'is_linked': is_linked,
		'has_active_subpages': has_active_subpages,
		'has_active_local_subnodes': has_active_local_subnodes,
		'has_inactive_parent': has_inactive_parent,
		'obj_path': [ob.id for ob in e.breadcrumbs_obj_path() if ob.id != 'content'],
		'page_elements': [f'''{pageelm.meta_id} ID={pageelm.id} {pageelm.attr('attr_dc_coverage')}''' for pageelm in pageelms]
	}

	return grading_datadict

# ----------------------------------------
# REFRESH Node by URL
# html-return: <ins>REFRESHED</ins>, <mark>ERROR</mark>
# ----------------------------------------
def refresh_by_url(self,refresh_url):
	request = self.REQUEST
	response =  request.response
	response.setHeader('Content-Type', 'text/html')
	zmscontext = self
	if not refresh_url:
		return '<mark>NOT REFRESHED (Error: No URL provided)</mark>'
	zmsnode = zmscontext.restrictedTraverse(refresh_url)
	if zmsnode:
		zmsnode.setObjStateModified(request)
		zmsnode.commitObj(request)
		return '<ins>SAVED with a Refreshed Date %s</ins>' % refresh_url
	else:
		return '<mark>NOT REFRESHED (Error: no parent found for %s)</mark>'%id


# ----------------------------------------
# DELETE Node by URL
# html-return: <del>DELETED</del>, <mark>ERROR</mark>
# ----------------------------------------
def delete_by_url(self,delete_url):
	request = self.REQUEST
	response =  request.response
	response.setHeader('Content-Type', 'text/html')
	zmscontext = self
	if not delete_url:
		return '<mark>NOT DELETED (Error: No URL provided)</mark>'
	zmsnode = zmscontext.restrictedTraverse(delete_url)
	parent = zmsnode.getParentNode()
	if zmsnode and parent:
		id = zmsnode.id
		# # Zope Delete
		# parent.manage_deleteObjs(request.get('lang','ger'), [id], request, RESPONSE=None)
		# # Move to ZMSTrashcan
		parent.moveObjsToTrashcan([id], request)
		return '<del>DELETED %s</del>' % delete_url
	else:
		return '<mark>NOT DELETED (Error: no parent found for %s)</mark>'%id


# -----------------------------------------------------
# ZMI HTML page 
# -----------------------------------------------------
def html_page(self):
		request = self.REQUEST
		response =  request.response
		zmscontext = self
		html = []
		html.append('<!DOCTYPE html>')
		html.append('<html lang="en">')
		html.append(zmscontext.zmi_html_head(zmscontext,request))
		html.append('<body class="%s">'%(' '.join(['zmi',request['lang'],'cleanup_recursive', zmscontext.meta_id])))
		html.append(zmscontext.zmi_body_header(zmscontext,request))
		html.append('<div id="zmi-tab">')
		html.append(zmscontext.zmi_breadcrumbs(zmscontext,request))
		html.append('<form id="form_cleanup_recursive" class="form-horizontal card" method="post" enctype="multipart/form-data">')
		html.append('<input type="hidden" name="form_id" value="manage_cleanup_recursive"/>')
		html.append('<input type="hidden" name="do_execution:boolean" value="1"/>')
		html.append('<legend>')
		html.append('<div>Content Cleanup for <i class="fas fa-home"></i> <span>%s</span> containing <span id="info_page_count">...</span> Nodes in <span id="info_lang_count">...</span> Languages <span id="info_proc_time">(... sec)</span></div>'%(zmscontext.getHome().id))
		html.append('''
					<nav>
						<a target="_blank" href="manage_cleanup_recursive?content_type=cvs" title="Show this List as CVS for Importing to Excel">CVS</a>&nbsp;&nbsp;&vert;&nbsp;
						<a target="_blank" href="manage_cleanup_recursive?content_type=json" title="Show Complete Tree in Details as JSON">JSON</a>&nbsp;&nbsp;&vert;&nbsp;
						<a href="manage_cleanup_recursive?content_type=html" class="active" title="Reload and Update this List"><i class="fas fa-sync text-primary"></i></a>
					</nav>
					''')
		html.append('</legend>')
		html.append('<div class="card-body" hx-target="this" hx-get="manage_cleanup_recursive?lang=%s&do_execution=1" hx-trigger="load">'%(request.get('lang','ger')))
		html.append('<div style="text-align:center;margin:2rem auto;"><i class="text-primary fas fa-spinner fa-spin fa-3x"></i></div>')
		html.append('</div>')
		html.append('</form>')
		html.append('</div>')
		html.append(zmscontext.zmi_body_footer(self,request))
		html.append('''
			<style>
				#form_cleanup_recursive legend {
					display: flex;
					justify-content: space-between;
				}
			 	#form_cleanup_recursive legend > div > span{
					color:#354f67;
				}
				#form_cleanup_recursive legend nav, 
				#form_cleanup_recursive legend nav a {
					text-decoration: none;
					color: #ccc;
					font-weight: normal;
					font-family: monospace;
				}
				#form_cleanup_recursive legend nav a:hover,
				#form_cleanup_recursive legend nav a.active,
				#form_cleanup_recursive legend nav a:hover i {
					color: #000 !important;
				}
				#form_cleanup_recursive h2 {
					text-transform: uppercase;
					margin: 0 0 1rem 0;
					font-size: 1.5rem;
					font-weight: bold;
				}
				#form_cleanup_recursive .card-body a {
					font-weight: bold;
				}
				#form_cleanup_recursive .card-body h2.delete,
				#form_cleanup_recursive .card-body .delete a {
					color: red;
				}
				#form_cleanup_recursive .card-body h2.check,
				#form_cleanup_recursive .card-body .check a {
					color:#03A9F4;
				}
				#form_cleanup_recursive .card-body pre {
					display: block;
					width: 25vw;
					overflow: hidden;
					text-overflow: ellipsis;
					padding-left: .5rem;
					margin: 0;
				}
				#form_cleanup_recursive .card-body ol.delete {
					margin-bottom: 2rem;
				}
				#form_cleanup_recursive .card-body li div {
					display: flex;
					justify-content: left;
					align-items: flex-start;
					cursor: help;
				}
				#form_cleanup_recursive .card-body li:nth-child(odd) div {
					background-color: #f1f3f5;
				}
				#form_cleanup_recursive .card-body pre:nth-child(3),
				#form_cleanup_recursive .card-body pre:nth-child(4) {
					width: 7vw;
				}
				#form_cleanup_recursive .card-body pre:nth-child(5),
				#form_cleanup_recursive .card-body pre:nth-child(6) {
					width: 4vw;
				}
				#form_cleanup_recursive .card-body pre i {
					cursor: pointer;
				}
				/* DELETE & REFRESH RESPONSE */
				#form_cleanup_recursive .card-body ol li:not(:has(div)) {
					padding-left: calc(2rem - 3px);
					font-family:monospace;
					font-size:85%;
					color:green;
					cursor:help;
					margin-left:3px;
					font-weight:bold
				}
				#form_cleanup_recursive .card-body ol li div pre > mark,
				#form_cleanup_recursive .card-body ol li div pre > del,
				#form_cleanup_recursive .card-body ol li div pre > ins {
					background-color:unset !important;
					text-decoration: none;
					color:black !important
				}
				#form_cleanup_recursive .card-body ol li div pre > mark:before,
				#form_cleanup_recursive .card-body ol li div pre > del:before,
				#form_cleanup_recursive .card-body ol li div pre > ins:before {
					/* Font Awesome Icon Check */
					content: "\\f00c";
					font-family: 'Font Awesome 5 Free';
					font-weight: 900;
					margin-right: 0.5rem;
					display: inline-block;
				}
				#form_cleanup_recursive .card-body ol li div pre > mark:before {
			  		/* Font Awesome Icon Exclamation Triangle */
					content: "\\f071";
					color: #FF5722;
				}
				#form_cleanup_recursive .card-body ol li div:has(pre > mark) {
					background-color:#ffeb3b !important;
				}
				#form_cleanup_recursive .card-body ol li div:has(pre > del) {
					background-color:#fbbfba !important;
				}
				#form_cleanup_recursive .card-body ol li div:has(pre > ins) {
					background-color:#b3dbfb !important;
				}

			</style>
		''')
		html.append('</body>')
		html.append('</html>')
		response.setHeader('Content-Type', 'text/html')
		return '\n'.join(html)

# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
def manage_cleanup_recursive(self):
	request = self.REQUEST
	response =  request.response
	zmscontext = self
	zmsclient_url = zmscontext.getHome().absolute_url()

	# -----------------------------------------------------
	# SHOW SPINNER page while waiting until action 
	# has completed it's execution
	# -----------------------------------------------------
	if not request.get('do_execution') and request.get('content_type') not in ['json','cvs']:
		response.setHeader('Content-Type', 'text/html')
		return html_page(zmscontext)
	else:
		pass

	# -----------------------------------------------------
	# REFRESH Node by URL
	# -----------------------------------------------------
	if request.get('do_refresh') and request.get('refresh_url'):
		response.setHeader('Content-Type', 'text/html')
		try:
			refresh_url = request.get('refresh_url')
			return refresh_by_url(zmscontext,refresh_url)
		except:
			return '<mark>NOT REFRESHED (Error: Could not refresh %s)</mark>'%refresh_url
	else:
		pass

	# -----------------------------------------------------
	# DELETE Node by URL
	# -----------------------------------------------------
	if request.get('do_delete') and request.get('delete_url'):
		response.setHeader('Content-Type', 'text/html')
		try:
			delete_url = request.get('delete_url')
			return delete_by_url(zmscontext,delete_url)
		except:
			return '<mark>NOT DELETED (Error: Could not delete %s)</mark>'%delete_url
	else:
		pass

	# -----------------------------------------------------
	# Get grading data for all pages
	# -----------------------------------------------------
	ZMI_TIME = DateTime.DateTime().timeTime()
	grading_data = [] # list of grading data dictionaries
	langs = zmscontext.getLangs()
	pages = [zmscontext]
	pages.extend( zmscontext.getTreeNodes(request, zmscontext.PAGES) )
	c = -1
	for page in pages:
		grading = 0
		c += 1
		l = 0
		for lang in langs:
			l += 1
			request.set('lang',lang)
			grading_datadict = get_cleanup_grading(page,request)
			grading_data.append(grading_datadict)

	# -----------------------------------------------------
	# DEBUG: Show all grading data as JSON
	# -----------------------------------------------------
	# return json.dumps(grading_data, indent=4)

	# VALIDATE "DELETE" NODES (grading == 2)
	# All nodes with grading == 2 are deleted only if their SUB-PAGES are inactive:
	# The grading value will be downgraded from 2 to 1 if any SUB-PAGE is active.
	delete_data = []
	valid_grading_data = []
	for grading_datadict in grading_data:
		grade = grading_datadict['grading']
		if grade == 2:
			# First search all grading_datadicts that contain the zmsid as item in obj_path
			# and then validate if any of them has grading == 1
			zmsid = grading_datadict['zmsid']
			for grading_datadict2 in grading_data:
				if zmsid in grading_datadict2['obj_path'] and grading_datadict2['is_multilang_inactive'] == False:
					# Downgrade grading value from 2 to 1
					grading_datadict['grading'] = 1
					grading_datadict['grading_info'] = 'CHECK'
					break
			if grading_datadict['grading'] == 2:
				delete_data.append(grading_datadict)
		valid_grading_data.append(grading_datadict)
	
	# -----------------------------------------------------
	# Clean the resulting lists of grading data by
	# -----------------------------------------------------
	clean_delete_data = delete_data.copy()
	clean_check_data = valid_grading_data.copy()

	# 1. Removing from DELETE-list language duplicates
	for delete_item in clean_delete_data:
		delete_item_id = delete_item['zmsid']
		for d in [e for e in standard.filter_list(l=clean_check_data,i='zmsid',v=delete_item_id,o='=') if e['lang']!=e['primary_lang']]:
			try:
				clean_delete_data.remove(d)
			except:
				standard.writeStdout(zmscontext, 'Step-1-Cleanup Processor Message: Could not remove %s from delete_data'%delete_item_id)
				pass

	# 2. Removing from DELETE-list all children of any parent that is marked for deletion
	for delete_item in clean_delete_data:
		delete_item_id = delete_item['zmsid']
		for delete_item2 in delete_data:
			if delete_item_id in delete_item2['obj_path'][:-1]:
				try:
					clean_delete_data.remove(delete_item2)
				except:
					standard.writeStdout(zmscontext, 'Step-2-Cleanup Processor Message: Could not remove %s from delete_data'%delete_item_id)
					pass

	# 3. Removing from CHECK-list all DELETE-nodes and their children
	for delete_item in delete_data:
		delete_item_id = delete_item['zmsid']
		for lang in langs:
			for check_item in clean_check_data:
					if (delete_item_id == check_item['zmsid'] and lang == check_item['lang']) or delete_item_id in check_item['obj_path']:
						try:
							clean_check_data.remove(check_item)
						except:
							standard.writeStdout(zmscontext, 'Step-3-Cleanup Processor Message: Could not remove %s from delete_data'%delete_item_id)
							pass


	# -----------------------------------------------------
	# Output of valid grading data for [A] JSON 
	# and delete/check-subset data for [B] CVS and [C] HTML
	# -----------------------------------------------------

	if request.get('content_type') == 'json':
	# [A] JSON
		# HINT: Use https://github.com/callumlocke/json-formatter
		# to format the JSON output in the browser
		response.setHeader('Content-Type', 'text/plain')
		return json.dumps(valid_grading_data, indent=4)
	# [B] CVS
	if request.get('content_type') == 'cvs':
		cvs = []
		cvs.append('INFO\tTITLE\tURL\tLANGUAGE\tAGE/YEARS')
		server_url = request.get('SERVER_URL')
		if clean_delete_data:
			for e in clean_delete_data:
				cvs.append('\t'.join([ e['grading_info'],e['title'], server_url + e['absolute_url'], e['lang'], str(round(e['age_days']/365)) ]))
		cvs.append('-\t-\t-\t-\t-')
		if clean_check_data:
			for e in clean_check_data:
				if e['grading'] == 1:
					cvs.append('\t'.join([ e['grading_info'],e['title'], server_url + e['absolute_url'], e['lang'], str(round(e['age_days']/365)) ]))
		response.setHeader('Content-Type', 'text/plain')
		return '\n'.join(cvs)
	# [C] HTML
	else:
		html = []
		li_tmpl = '''
			<li title="{TOOLTIP}">
				<div>
					<pre><a target="blank" href="{e.absolute_url}/manage?lang={e.lang}&dtpref_sitemap=1">{e.title}</a></pre>
					<pre>ID:{ID}</pre>
					<pre>LANG:{e.lang}</pre>
					<pre title="{e.age_days}T">YEARS:{YEARS}</pre>
					<pre><i title="Move to Trashcan"  hx-post="manage_cleanup_recursive?do_delete=1&delete_url={e.absolute_url}&lang={e.lang}"   hx-confirm="Move to Trashcan: Sure?"  hx-on:htmx:before-request="this.parentNode.parentNode.lastElementChild.innerHTML='<i class=\\\'fas fa-spinner fa-spin\\\'></i>'" hx-target="next .message" class="far fa-trash-alt text-danger"></i></pre>
					<pre><i title="Refresh Edit-Date" hx-post="manage_cleanup_recursive?do_refresh=1&refresh_url={e.absolute_url}&lang={e.lang}" hx-confirm="Refresh Edit-Date: Sure?" hx-on:htmx:before-request="this.parentNode.parentNode.lastElementChild.innerHTML='<i class=\\\'fas fa-spinner fa-spin\\\'></i>'" hx-target="next .message" class="fas fa-calendar-check text-primary"></i></pre>
					<pre class="message"></pre>
				</div>
			</li>'''

		if clean_delete_data:
			html.append('<h2 class="delete"><i class="far fa-trash-alt"></i> delete</h2>')
			html.append('<ol class="delete">')
			for e in clean_delete_data:
				TOOLTIP = json.dumps(e, indent=4).replace('"', '')
				html.append(li_tmpl.format(TOOLTIP=TOOLTIP, e=dotdict(e), ID='/content/' not in e['absolute_url'] and e['absolute_url'] or e['absolute_url'].split('/content')[1], YEARS=round(e['age_days']/365)))
			html.append('</ol>')
			html.append('<p />')

		# Show only the check items with grading == 1
		clean_check_data = [e for e in clean_check_data if e['grading'] == 1]
		if clean_check_data:
			html.append('<h2 class="check"><i class="fas fa-eye"></i> check</h2>')
			html.append('<ol class="check">')
			for e in clean_check_data:
				TOOLTIP = json.dumps(e, indent=4).replace('"', '')
				html.append(li_tmpl.format(TOOLTIP=TOOLTIP, e=dotdict(e), ID='/content/' not in e['absolute_url'] and e['absolute_url'] or e['absolute_url'].split('/content')[1], YEARS=round(e['age_days']/365)))
			html.append('</ol>')
		
		if not clean_delete_data and not clean_check_data:
			html.append('<h2 class="text-success"><i class="fas fa-check"></i> No items to check</h2>')
			html.append('<p>All items are active or have active subpages. Nothing to clean,</p>')
			html.append('<p />')

		# -----------------------------------------------------
		ZMI_TIME_SEC = int((DateTime.DateTime().timeTime()-ZMI_TIME)*100.0)/100.0

		html.append('''
			<script>
				document.getElementById('info_page_count').innerText = '%s';
				document.getElementById('info_lang_count').innerText = '%s';
				document.getElementById('info_proc_time').innerText = '(%.2f sec)';
			</script>
		'''%(len(pages), len(langs), ZMI_TIME_SEC))

		response.setHeader('Content-Type', 'text/html')
		return '\n'.join(html)