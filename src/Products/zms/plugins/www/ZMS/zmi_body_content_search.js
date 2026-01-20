/**
 * Get url-parameter.
 *
 * @sParam the name of the parameter
 * @sDefault the default-value
 */
function GetURLParameter(sParam, sDefault) {
	var sPageURL = window.location.search.substring(1);
	var sURLVariables = sPageURL.split('&');
	for (var i = 0; i < sURLVariables.length; i++) {
		var sParameterName = sURLVariables[i].split('=');
		if (sParameterName[0] == sParam) {
			var parameterValue = sParameterName[1]
				.replace(/\+/gi,' ')
				.replace(/%23/gi,'#')
				.replace(/%24/gi,'$')
				.replace(/%26/gi,'&')
				.replace(/%2B/gi,'+')
				.replace(/%2C/gi,',')
				.replace(/%2F/gi,'/')
				.replace(/%3A/gi,':')
				.replace(/%3B/gi,';')
				.replace(/%3D/gi,'=')
				.replace(/%3F/gi,'?');
			try {
				return decodeURI(parameterValue);
			}
			catch (e) {
				return parameterValue;
			}
		}
	}
	return sDefault;
}

/**
 * Assemble url-parameters:
 *
 * add parameters from dict to url (overwrite existing values).
 * @param url the url
 * @param d the dictionary of parameters to be added to the url.
 */
function AssembleUrlParameter(url,d) {
	if (url.indexOf("?") > 0) {
		var sPageURL = url.substring(url.indexOf("?")+1);
		var sURLVariables = sPageURL.split('&');
		for (var i = 0; i < sURLVariables.length; i++) {
			var sURLVariable = sURLVariables[i].split('=');
			var sParameterName = sURLVariable[0];
			var sParameterValue = sURLVariable[1];
			if (typeof d[sParameterName]=="undefined") {
				d[sParameterName] = sParameterValue;
			}
		}
		url = url.substring(0,url.indexOf("?"));
	}
	var dl = "?";
	for (var sParameterName in d) {
		url += dl + sParameterName + "=" + d[sParameterName];
		dl = "&";
	} 
	return url;
}

/**
 * Get pagination.
 *
 * @param fn the function to assemble url for page-index.
 * @param size the total number of records.
 * @param pageSize the number of records on each page.
 * @param pageIndex the index of the current-page.
 */
function GetPagination(fn, size, pageSize, pageIndex) {
	var html = '';
	if (size > pageSize) {
		var pageCount = Math.floor(((size-1)/pageSize)+1);
		html += ''
			+ '<nav aria-label="Page navigation">'
			+ '<ul class="pagination">';
		html += ''
			+ '<li class="page-item '+(pageIndex==0?"disabled":"")+'">'
			+ '<a class="page-link" href="'+(pageIndex==0?'javascript:;':fn(pageIndex-1))+'">'+$ZMI.icon('fa fa-chevron-left icon-chevron-left')+'</span></a>'
			+ '</li>';
		for (var page = 0; page < pageCount; page++) {
			if (pageCount>=10 && page==pageCount-1 && pageIndex<pageCount-(3+1)-1) {
				html += '<li class="page-item disabled"><span>...</span></li>';
			}
			if (pageCount<10 || (page==0) || (page>=pageIndex-3 && page<=pageIndex+3) || (page==pageCount-1)) {
				html += ''
					+ '<li class="page-item ' + (pageIndex==page?"active":"") + '">'
					+ '<a class="page-link" href="'+(pageIndex==page?'javascript:;':fn(page))+'">'+(page+1)+'</a>'
					+ '</li>';
			}
			if (pageCount>=10 && page==0 && pageIndex>(3+1)) {
				html += '<li class="page-item disabled"><span>...</span></li>';
			} 
		}
		html += ''
			+ '<li class="page-item last' + (pageIndex==pageCount-1?" disabled":"") + '">'
			+ '<a class="page-link" href="'+(pageIndex==pageCount-1?'javascript:;':fn(pageIndex+1))+'">'+$ZMI.icon('fa fa-chevron-right icon-chevron-right')+'</a>'
			+ '</li>'
			+ '</ul>'
			+ '</nav><!-- .pagination -->';
	}
	$(".pagination").replaceWith(html);
}

function zmiBodyContentSearch(q,pageSize,pageIndex,connectorId) {
	if (q.length==0) {
		return;
	}
	let zmi = document.location.toString().indexOf('/manage') > 0;
	$("#search_results").show();
	$("input[name=search]").val(q).change();
	$(".line.row:first").html('');
	$(".line.row:gt(0)").remove();
	let p = {};
	p['q'] = q;
	p['hl.fragsize'] = 200;
	p['hl.simple.pre'] = '<span class="highlight">';
	p['hl.simple.post'] = '</span>';
	p['page_size'] = pageSize;
	p['page_index'] = pageIndex;
	let fq = '';
	if (typeof zmiParams === 'object' && (typeof zmiParams['home_id'] === 'object' || typeof zmiParams['home_id'] === 'string' ) && zmiParams['home_id'].length > 0) {
		let home_id = (typeof zmiParams['home_id'] === 'object') ? zmiParams['home_id'][0] : zmiParams['home_id'];
		fq += 'home_id:' + home_id;
	}
	p['fq'] = fq;
	var base_url = self.location.origin + self.location.pathname;
	if (base_url.indexOf("/content")>0) {
		base_url = base_url.substring(0,base_url.indexOf("/content")+"/content".length);
	} else if (base_url.indexOf("/manage")>0) {
		base_url = base_url.substring(0,base_url.indexOf("/manage"))+"/content";
	}
	let adapter = $ZMI.getConfProperty('zms.search.adapter.id','zcatalog_adapter');
	let connector = $ZMI.getConfProperty('zms.search.connector.id','zcatalog_connector');
	// Check for connector base-url override
	let connector_base_url = $ZMI.getConfProperty('zms.search.connector.base_url','');
	if (connector_base_url.length > 0) {
		base_url = connector_base_url;
	}
	let url = base_url+'/'+adapter+'/'+connector+'/search_json';
	$.ajax({
		url:url,
		data:p,
		timeout:5000,
		error: function (xhr, ajaxOptions, thrownError) {
			$("#search_results .small-head").html(''
				+ getZMILangStr('CAPTION_ERROR')+'<hr/> '
				+ '<code>' + xhr.status + ': ' + thrownError + '</code>');
		},
		success:function(result) {
			// Connector: ZCatalog 
			let total = result['numFound'];
			let docs = result['docs']
			if (connectorId == 'opensearch_connector') {
			// Connector: OpenSearch
				total = result['hits']['total']['value'];
				docs =  result['hits']['hits'];
			}
			let html = "";
			if (total == 0) {
				$("#search_results .small-head").html(getZMILangStr('SEARCH_YOURQUERY').replace('%s','<span id="q" class="badge badge-danger fa-1x"></span>')+' '+getZMILangStr('SEARCH_NORESULTS'));
				$("#search_results .small-head #q").text(q);
			}
			else {
				$("#search_results .small-head").html(getZMILangStr('SEARCH_YOURQUERY').replace('%s','<span id="q" class="badge badge-info fa-1x"></span>')+' '+getZMILangStr('SEARCH_RETURNEDRESULTS')+':');
				$("#search_results .small-head #q").text(q);
				docs.forEach(doc => {
					let href = '';
					if (connectorId == 'opensearch_connector') {
						doc = doc._source;
					}
					let doc_headine_title = `${doc.title}`;
					if (zmi) {
						if (href=='' || href==undefined) href = doc.loc;
						if (href=='' || href==undefined) href = doc.absolute_url;
						if (href=='' || href==undefined) href = doc.path;
						href += '/manage';
						doc_headine_title = `ZMS-ID ${doc.home_id}\nPATH: ${doc.loc}`;
					} else {
						href = doc.index_html;
					}
					let snippet = doc.attr_dc_description || doc.standard_html || '';
					if (snippet.length > p['hl.fragsize']) {
						snippet = snippet.substring(0,p['hl.fragsize']);
						while (!snippet.lastIndexOf(" ")==snippet.length-1) {
							snippet = snippet.substring(0,snippet.length-2);
						}
					}
					html += `
						<div class="line row" data-uid="${doc.uid}" data-id="${doc.id}">
							<div class="col-sm-12">
								<h2 class="${doc.meta_id}" title="${doc_headine_title}">
									<a target="_blank" href="${href}">${doc.title}</a>
								</h2>
								<p>${snippet}</p>
							</div>
						</div>
					`;
				});
				// Pagination
				let fn = function(pageIndex) {
					let url = window.location.href;
					return AssembleUrlParameter(url,{"pageIndex:int":pageIndex});
				}
				GetPagination(fn,total,pageSize,pageIndex);
			}
			$(".line.row:first").replaceWith(html);
			// Callback: Done
			if (typeof zmiBodyContentSearchDone == 'function') {
				zmiBodyContentSearchDone();
			}
		}});
	return false;
}

$(function() {
	var q = GetURLParameter("search","").trim();
	var pageSize = 10;
	var pageIndex = parseInt(GetURLParameter('pageIndex:int','0'));
	var connectorId = $ZMI.getConfProperty('zms.search.connector.id','zcatalog_connector');
	return zmiBodyContentSearch(q,pageSize,pageIndex,connectorId);
});
