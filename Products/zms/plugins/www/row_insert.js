// Title: Row Insert Functions
// Description: Functions for adding more data-rows to ZMI config tables.

/**
 * Get current number of language terms.
 */
function get_lang_terms_count() {
	let lang_terms_count = 0;
	// Refresh cached language dictionary
	let lang_dict_json = $.ajax({
		url: $ZMI.getBaseUrl()+'/get_lang_dict',
		async: false
		}).responseJSON;
	$ZMI.setCachedValue('get_lang_dict',lang_dict_json);

	// Get language count from cached language dictionary
	let lang_dict = ZMI.prototype.getCachedValue('get_lang_dict');
	if ( lang_dict!='undefined' ) {
		if ( typeof lang_dict == 'object' ) {
			lang_terms_count = Object.keys(lang_dict).length;
		} else {
			lang_terms_count = Object.keys(JSON.parse(lang_dict)).length;
		}
	};
	return lang_terms_count;
}


/**
 * Remove row from table.
 */
function remove_row(context) {
	// 1. Remove row from table
	$(context).closest('tr').hide('slow',function(){$(this).closest('tr').remove()});
	// 2. Set form as modified (ZMS.onChangeObjEvt)
	$ZMI.set_form_modified(context);
	// 3. Normalize sorting-UI after deleting a row
	renew_sort_options(this_table = $(context).closest('table'));
}


/**
 * Normalize sorting-UI after deleting a row.
 */
function clean_deleted_row(context) {
	$(context).closest('tr').hide('slow',function(){
		$(context).closest('tr').remove();
		renew_sort_options(this_table = $(context).closest('table'));
	})
}

/**
 * Normalize inserted rows.
 */
function renew_sort_options(this_table) {

	let lang = getZMILang();
	// Remove highlighting of new rows
	$('tr[id*="new_row"]').each(function() {
		$(this).removeAttr('id');
	});

	let $rows = $('tbody tr', this_table)
	let sort_options_len = $rows.length;
	let row_counter = 0;
	$rows.each( function() {
		row_counter++;
		let sort_options_html = ``;
		let old_id = $(this).find('td.meta-id input').attr('name');
		let old_id_html = `<input type="hidden" name="old_ids:list" value="${old_id}">`;
		for (let i = 1; i < sort_options_len; i++) {
			if (i == row_counter) {
				sort_options_html += `<option value="${i}" selected>${i}</option>`;
			} else {
				sort_options_html += `<option value="${i}">${i}</option>`;
			}
		};
		const new_btn_html = `
			<div class="input-group input-group-sm">
				${old_id_html}
				<select class="zmi-sort form-control-sm"
					onchange="zmiFormSubmit(this,{btn:'move_to',id:'${old_id}','pos:int':this.selectedIndex})">
					${sort_options_html}
				</select>
				<div class="input-group-append">
					<a class="btn btn-secondary" title="Delete Meta Attribute"
						hx-get="manage_changeMetaProperties?btn=BTN_DELETE&target=zmi_manage_tabs_message&lang=${lang}&id=${old_id}"
						hx-target="#zmi_manage_tabs_message"
						hx-on:htmx:after-request="clean_deleted_row(this)">
						<i class="fas fa-times"></i>
					</a>
				</div>
			</div>
		`;

		if (row_counter < sort_options_len) {
			$(this).find('td.meta-sort').html(new_btn_html);
			htmx.process($(this).find('td.meta-sort')[0]); // Process the new elements with htmx
		};
	});
};

/**
 * Add new row to table: click event function
 */
function add_new_row(this_btn) {
	let $where_insert = $(this_btn).closest('tr');
	let table_id  = $(this_btn).closest('table').attr('id').split('_').pop();
	let row_count = $('tbody tr',$(this_btn).closest('table')).length;
	let new_row_name = `new_row_${table_id}_${row_count}`;
	let old_id_html = `<input type="hidden" name="old_ids:list" value="new${row_count}">`;
	if (table_id == 'languages') {
		// metaobj_manager.meta_languages
		old_id_html = '';
	}
	let new_btn_html = `
		${old_id_html}
		<span class="btn btn-secondary mr-1 w-100" style="color:#999"
			title="Revoke New Row"
			onclick="javascript:$(this).closest('tr').hide('slow',function(){$(this).closest('tr').remove()})">
			<i class="fas fa-undo-alt"></i>
		</span>
	`;

	// Clone(true) to get a deep copy including select options
	let $new_row = $where_insert.clone(true);

	// Process table cells of the clone like "old" row
	$new_row.find('td').each(function() {
		$(this).find('input,select,textarea').each(function() {
			$(this).removeAttr('disabled');
			$(this).removeAttr('id');
			let tagname = $(this).prop('tagName').toLowerCase();
			let defname = $(this).attr('name').split(':')[0]; 
			let deftype = $(this).attr('type');
			let newval  = `new${row_count}`;
			let newname = `${defname}_${newval}`;
			if (defname.slice(-1)=='0') {
				newname = defname.replace('0', row_count);
			};
			if (defname.includes('_0_')) {
				newname = defname.replace('_0_', `_${row_count}_`);
			};
			$(this).attr('name',newname);
			if (!(tagname == 'select')) {
				$(this).val(newval);
			};
			if ( tagname == 'input' && deftype != 'checkbox') {
				$(this).attr('placeholder',newval);
			};
			if ( deftype == 'checkbox' ) {
				$(this).attr('name',`${newname}:int`);
				$(this).val(1);
			};
			if ( $(this).hasClass('url-input') ) {
				$(this).closest('.input-group').replaceWith(`<input class="form-control url-input" name="${newname}" placeholder="Select Url..."/>`); 
			};
		});
	});

	// Process td:first-child of the clone
	$new_row.find('td.meta-sort').html(new_btn_html);
	$new_row.removeClass('row_insert').attr('id',new_row_name);

	// Insert the new row
	$new_row.insertBefore($where_insert);
	// Set form as modified
	$ZMI.set_form_modified($('.meta-id input',$new_row));
	$ZMI.initUrlInput($("td.meta-url",$new_row));
	// Reset the clone template
	$where_insert.find('input:not([type="checkbox"]),select,textarea').each(function() {
		$(this).val(undefined);
	});
	// New field set: reset to disabled inputs
	$('input, textarea, select','tr.row_insert').attr('disabled',true);
}
