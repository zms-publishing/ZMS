$(function() {

	//# Compile HB templ on docready into global var
	const hb_results_tmpl = Handlebars.compile( $('#hb_results_html').html() );

	const show_results = async (q) => {
		// debugger;
		const response = await fetch(`zcatalog_adapter/zcatalog_opensearch_connector/search_json?q=${q}`);
		const res = await response.json();
		const res_processed = postprocess_results(q, res);
		var total = res_processed.total;
		var hb_results_html = hb_results_tmpl(res_processed);
		$('.search-results').html( hb_results_html );
	
		//# @WORK ############################
		var fn = (pageIndex) => {
			var url = window.location.href;
			return AssembleUrlParameter(url,{"pageIndex:int":pageIndex});
		};
		GetPagination(fn,total,10,0);
		//####################################
	};

	const postprocess_results = (q, res) => {
		var total = res.hits.total.value;
		var res_processed = { 'hits':[], 'total':total, 'query':q };
		res["hits"]["hits"].forEach(x => {
			var source = x["_source"];
			var highlight = x["highlight"];
			var hit = {"path":x["_id"], "href":source["loc"], "title":source["title"], "snippet":source["standard_html"]}; 
			if (typeof highlight !== "undefined") {
				if (typeof highlight["title"] !== "undefined") {
					hit["title"] = highlight["title"];
				}
				if (typeof highlight["standard_html"] !== "undefined") {
					hit["snippet"] = highlight["standard_html"];
				}
			}
			if (hit["snippet"].length > 200) {
				hit["snippet"] = hit["snippet"].substr(0,200) + "...";
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
	$(".search-form form").submit(function() {
		var q = $("input",this).val();
		var msg = `<h2>Suche nach <code>${q}</code></h2><div title="Loading..." class="spin"></div>`;
		$(".search-results").html(msg);
		show_results(q);
		//# @WORK ############################
		//# How to promise on show_results()?
		//# ##################################
		setTimeout(() => {
			$('ul.path').each(function() {
				show_breadcrumbs(this);
			})
		}, 1500);
		return false;
	});

});