//# ######################################
//# Init function show_results() as global
//# ######################################
var show_results;
var winloc = new URL(window.location);
//# ######################################
$(function() {

	//# Compile HB templ on docready into global var
	const hb_results_tmpl = Handlebars.compile( $('#hb_results_html').html() );
	const hb_spinner_tmpl = Handlebars.compile( $('#hb_spinner_html').html() );

	// Finally define show_results() on ready
	show_results = async (q, pageIndex) => {
		$('.search-results').html(hb_spinner_tmpl(q));
		// debugger;
		const qurl = `zcatalog_adapter/zcatalog_opensearch_connector/search_json?q=${q}&pageIndex:int=${pageIndex}`;
		const response = await fetch(qurl);
		const res = await response.json();
		const res_processed = postprocess_results(q, res);
		var total = res_processed.total;
		var hb_results_html = hb_results_tmpl(res_processed);
		$('.search-results').html( hb_results_html );
	
		//# Add pagination ###################
		var fn = (pageIndex) => {
			return `javascript:show_results('${q}',${pageIndex})`
		};
		GetPagination(fn, total, 10, pageIndex);
		//# ##################################

		// Add object path on UUID/ZMSIndex
		$('ul.path').each(function() {
			show_breadcrumbs(this);
		})

	};

	const postprocess_results = (q, res) => {
		var total = res.hits.total.value;
		var buckets = []
		try {
			buckets = res.aggregations.response_codes.buckets;
		} catch {
			log.console('INFO: Result does not contain buckets-element')
		}
		var res_processed = { 'hits':[], 'total':total, 'query':q, 'buckets':buckets};

		res['hits']['hits'].forEach(x => {
			var source = x['_source'];
			var highlight = x['highlight'];
			var hit = { 'path':x['_id'], 'href':source['loc'], 'title':source['title'], 'snippet':source['standard_html'] }; 
			if (typeof highlight !== 'undefined') {
				if (typeof highlight['title'] !== 'undefined') {
					hit['title'] = highlight['title'];
				}
				if (typeof highlight['standard_html'] !== 'undefined') {
					hit['snippet'] = highlight['standard_html'];
				}
			}
			if ( typeof hit['snippet'] == 'undefined') {
				if (typeof source['attr_dc_description'] == 'undefined') {
					hit['snippet'] = '';
				} else {
					hit['snippet'] = source['attr_dc_description'];
				}
			}
			// Attachment: field-name = 'data'
			if ( typeof source['attachment'] !== 'undefined' && hit['snippet']=='' ) {
				hit['snippet'] = source['attachment']['content'];
			}
			if (hit['snippet'].length > 200) {
				hit['snippet'] = hit['snippet'].substr(0,200) + '...';
			}
			res_processed.hits.push(hit)
		})
		return res_processed;
	};

	const show_breadcrumbs = (el) => {
		$.get(url='get_breadcrumbs_by_uuid', data={ 'id' : el.dataset.id }, function(data, status) {
			$(el).html(data);
		});
	}

	//# Execute on submit event
	$('.search-form form').submit(function() {
		var q = $('input',this).val();
		winloc.searchParams.set('q', q);
		history.pushState({}, '', winloc);
		show_results(q, 0);
		return false;
	});

	// POSSIBLE SECURITY ISSUE: auto-execute on ULR parameter
	if ( winloc.searchParams.get('q', undefined) ) {
		$('#form-keyword').val(encodeURI(winloc.searchParams.get('q','')));
		$('.search-form form').trigger('submit');
	}

});