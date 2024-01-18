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

$(function() {
	const root_url=$('form#site-search-content').attr('data-root-url');
	//# Compile HB templ on docready into global var
	const hb_results_tmpl = Handlebars.compile( $('#hb_results_html').html() );
	const hb_spinner_tmpl = Handlebars.compile( $('#hb_spinner_html').html() );

	// Finally define show_results() on ready
	show_results = async (q, pageIndex) => {
		$('.search-results').html(hb_spinner_tmpl(q));
		// debugger;
		const qurl = `${root_url}/opensearch_query?q=${q}&pageIndex:int=${pageIndex}`;
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
			var index_name = x['_index'];
			var source = x['_source'];
			// UNIBE
			if ( index_name != 'unitel' ) {
				var highlight = x['highlight'];
				var hit = { 
					'path':source['uid'], 
					'href':source['index_html'], 
					'title':source['title'], 
					'snippet':source['standard_html'],
					'index_name':index_name
				};
				if (typeof highlight !== 'undefined') {
					if (typeof highlight['title'] !== 'undefined') {
						hit['title'] = highlight['title'];
					}
					if (typeof highlight['standard_html'] !== 'undefined') {
						hit['snippet'] = highlight['standard_html'];
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
			} else {
			// UNITEL
				var title = `${source['Vorname']}  ${source['Nachname']}`;
				var href = '';
				var EMail = '';
				var Adresse = '';
				if (Array.isArray(source['Adresse'])) {
					console.log('Adresse object is a list');
					EMail = source['Adresse'][0]['EMail'];
					source['Adresse'].forEach(d => {
						Adresse += `<dl>${stringify_address(d)}</dl>`;
					});
				} else {
					console.log('Adresse object is a dictionary');
					EMail = source['Adresse']['EMail'];
					d = source['Adresse'];
					Adresse += `<dl>${stringify_address(d)}</dl>`;
				}
				href = `mailto:${EMail}?subject=Anfrage%20via%20Website&body=Guten%20Tag,`;
				var hit = { 
					'path':source['uid'],
					'href':href,
					'title':title, 
					'snippet':Adresse,
					'index_name':index_name
				}; 
			}
			res_processed.hits.push(hit)
		})
		return res_processed;
	};

	const show_breadcrumbs = (el) => {
		if ( el.dataset.id.startsWith('uid') ) {
			$.get(url=`${root_url}/opensearch_breadcrumbs_obj_path`, data={ 'id' : el.dataset.id }, function(data, status) {
				$(el).html(data);
			});
		}
	}

	const stringify_address = (d) => {
		var s = '';
		Object.keys(d).forEach(k => {
			s += `<dt class="${k}">${k}</dt>`;
			s += `<dd class="${k}">${d[k]}</dd>`;
		});
		return s
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

	//# Autocomplete
	$('#form-keyword').keyup(function() {
		var input = $(this).val();
		if(input.length > 2) {
			$.ajax({
				url: './opensearch_suggest',
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
