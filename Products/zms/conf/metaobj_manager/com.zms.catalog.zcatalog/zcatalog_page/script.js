//# ######################################
//# Init function show_results() as global
//# ######################################
var show_results;
var winloc = new URL(window.location);
//# ######################################
$(function() {
	const root_url=$('form#site-search-content').attr('data-root-url');
	//# Compile HB templ on docready into global var
	const hb_results_tmpl = Handlebars.compile( $('#hb_results_html').html() );
	const hb_spinner_tmpl = Handlebars.compile( $('#hb_spinner_html').html() );

	// Finally define show_results() on ready
	show_results = async (q, pageIndex) => {
		$('.search-results').removeClass('not-launched');
		$('.search-results').html(hb_spinner_tmpl(q));
		// debugger;
		const qurl = `${root_url}/zcatalog_query?q=${q}&pageIndex:int=${pageIndex}`;
		const response = await fetch(qurl);
		const res = await response.json();
		const res_processed = postprocess_results(q, res);
		var total = res_processed.total;
		var hb_results_html = hb_results_tmpl(res_processed);
		$('.search-results').html( hb_results_html );
		$('html, body').animate({scrollTop: $("#search_results").offset().top }, 1000);

		//# Add pagination ###################
		var fn = (pageIndex) => {
			q = encodeURI(decodeURI(q));
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
		var total = res.numFound;
		var facets = []; // res.facets;
		var res_processed = { 'hits':[], 'total':total, 'query':q, 'facets':facets};

		res.docs.forEach(x => {
			let source = x;
			let score = typeof source['score'] !== 'undefined' ? parseFloat(source['score']/100).toFixed(2) : -1;
			var hit = { 
				'path':source['uid'],
				'href':source['loc'] || source['index_html'],
				'title':source['title'],
				'meta_id':source['meta_id'],
				'snippet':source['standard_html'],
				'score':score
			}; 
			// Snippet: field-name = 'standard_html'
			// Attachment: field-name = 'data'
			if ( typeof source['attachment'] !== 'undefined' && hit['snippet']=='' ) {
				hit['snippet'] = source['attachment']['content'];
			}
			if (hit['snippet'].length > 200) {
				hit['snippet'] = hit['snippet'].substring(0,200) + '...';
			}
			res_processed.hits.push(hit)
		})
		return res_processed;
	};

	const show_breadcrumbs = (el) => {
		const lang = $('#lang').attr('value');
		if ( el.dataset.id.startsWith('uid') ) {
			$.get(url=`${root_url}/zcatalog_breadcrumbs_obj_path`, 
				data={ 'id' : el.dataset.id }, 
				function(data, status) {
					$(el).html(data);
				}
			);
		}
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