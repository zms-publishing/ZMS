//# ######################################
//# Handlebars Helper
//# ######################################
Handlebars.registerHelper("compareStrings", function (p, q, options) {
	return p == q ? options.fn(this) : options.inverse(this);
})

//# ######################################
//# Init function show_results() as global
//# ######################################
var show_results;
var winloc = new URL(window.location);
//# ######################################

// Custom-Autofill-GUI: if brower autofill element is not wanted
// References:
// https://html.spec.whatwg.org/multipage/input.html#the-list-attribute
// https://html.spec.whatwg.org/multipage/forms.html#enabling-client-side-automatic-filling-of-form-controls
function complete_searchterm(el) {
	$('#form-keyword').val(el.value);
	$("#suggests").empty(); // remove any existing options
}

function show_results_facet(e) {
	var q = $('#site-search-content input').val();
	var facet = $(e).attr('data-facet');
	winloc.searchParams.set('q', q);
	winloc.searchParams.set('facet', facet);
	history.pushState({}, '', winloc);
	show_results(q, 0, facet);
	return false;
}

$(function() {
	const root_url=$('form#site-search-content').attr('data-root-url');
	//# Compile HB templ on docready into global var
	const hb_results_tmpl = Handlebars.compile( $('#hb_results_html').html() );
	const hb_spinner_tmpl = Handlebars.compile( $('#hb_spinner_html').html() );

	// Finally define show_results() on ready
	show_results = async (q, pageIndex, facet) => {
		if ( facet==undefined ) { facet=='all' };
		if (facet=='all') {
			// Replace whole tab-content
			$('.search-results').html(hb_spinner_tmpl(q));
		} else {
			// Replace only tab-pane
			$('.search-results .tab-content').html(hb_spinner_tmpl(q));
		};
		const qurl = `${root_url}/elasticsearch_query?q=${q}&pageIndex:int=${pageIndex}`;
		const response = await fetch(qurl);
		const res = await response.json();
		const res_processed = postprocess_results(q, res, facet);
		var total = res_processed.total;
		var hb_results_html = hb_results_tmpl(res_processed);
		if (facet=='all') {
			// Replace whole tab-content
			$('.search-results').html( hb_results_html );
		} else {
			// Replace only tab-pane
			$('.search-results .tab-content').html( hb_results_html );
		}
		//# Add pagination ###################
		var fn = (pageIndex) => {
			return `javascript:show_results('${q}',${pageIndex},'${facet}')`
		};
		GetPagination(fn, total, 10, pageIndex);
		//# ##################################

		// Add object path on UUID/ZMSIndex
		$('ul.path').each(function() {
			show_breadcrumbs(this);
		})
	};

	const postprocess_results = (q, res, facet) => {
		var total = res.hits.total.value;
		var buckets = []
		if (facet=='all') {
			try {
				buckets = res.aggregations.response_codes.buckets;
			} catch {
				log.console('INFO: Result does not contain buckets-element');
			}
		};
		var res_processed = { 'hits':[], 'total':total, 'query':q, 'buckets':buckets};
		res['hits']['hits'].forEach(x => {
			let index_name = x['_index'];
			let source = x['_source'];
			let highlight = x['highlight'];
			let body = source['standard_html'];
			let title = source['title'];
			// Remove repeating title string from beginning of snippet
			let snippet = body.startsWith(title) ? body.substr(title.length).trim() : body;
			var hit = { 
				'path':source['uid'], 
				'href':source['index_html'], 
				'title':title, 
				'snippet':snippet,
				'index_name':index_name
			};
			if (typeof highlight !== 'undefined') {
				if (typeof highlight['title'] !== 'undefined') {
					hit['title'] = highlight['title'];
				}
				if (typeof highlight['standard_html'] !== 'undefined') {
				    // Highlight-text may start with repeating title:
				    // For checking first remove html elements and then 
				    // split title string if hightlight-snippet is starting with it
				    let highlight_html = highlight['standard_html'][0];
				    let highlight_txt = highlight_html.replace(/(<([^>]+)>)/gi, '');
				    let snippet_text = highlight_txt.startsWith(title) ? highlight_txt.substr(title.length).trim() : highlight_txt;
				    // Determine strings after title (cave: may fail if html-elements block splitting)
				    highlight_html = highlight_html.substr( highlight_html.indexOf(snippet_text.substr(0,12)) );
					hit['snippet'] = highlight_html;
				}
			}
			if ( typeof hit['snippet'] == 'undefined' || hit['snippet'] == '' || hit['snippet'] == null ) {
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
				hit['snippet'] = hit['snippet'].substring(0,200) + '...';
			}
			res_processed.hits.push(hit)
		})
		return res_processed;
	};

	const show_breadcrumbs = (el) => {
		if ( el.dataset.id.startsWith('uid') ) {
			$.get(url=`${root_url}/elasticsearch_breadcrumbs_obj_path`, data={ 'id' : el.dataset.id }, function(data, status) {
				$(el).html(data);
			});
		}
	}

	const stringify_address = (d) => {
		var s = '';
		Object.keys(d).forEach(k => {
			if (d[k]) {
				s += `<dt class="${k}">${k}</dt>`;
				s += `<dd class="${k}">${d[k]}</dd>`;
			};
		});
		return s
	}

	//# Execute on submit event
	$('.search-form form').submit(function() {
		var q = $('input',this).val();
		var facet = 'all';
		winloc.searchParams.set('q', q);
		history.pushState({}, '', winloc);
		show_results(q, 0, facet);
		return false;
	});

	// POSSIBLE SECURITY ISSUE: auto-execute on ULR parameter
	if ( winloc.searchParams.get('q', undefined) ) {
		$('#form-keyword').val(encodeURI(winloc.searchParams.get('q','')));
		$('.search-form form').trigger('submit');
	}

	//# Autocomplete
	$('#form-keyword').keyup(function() {
		var input = $(this).val();
		if(input.length > 2) {
			$.ajax({
				url: './elasticsearch_suggest',
				type: 'GET',
				dataType: "json",
				data: {'q': input},
				success: function(data) {
					var dataList = $("#suggests");
					dataList.empty(); // remove any existing options
					$.each(data, function(index, value) {
						// create new option element and append it to datalist
						// function complete_searchterm() may used for custom-autofill-gui
						$('<option onclick="complete_searchterm(this)">')
								.val(value)
								.text(value)
								.appendTo(dataList);
					});
				}
			});
		}
	});
});
