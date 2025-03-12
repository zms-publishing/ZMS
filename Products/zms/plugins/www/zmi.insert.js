// Title: Row Insert Functions
// Description: Functions for adding more data-rows to ZMI config tables.

// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// [A] MAIN FUNCTION: Add new row to data-grid
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
function add_new_row(this_btn) {
	let $where_insert = $(this_btn).closest('tr');
	let table_id  = $(this_btn).closest('table').attr('id').split('_').pop();
	let row_count = $('tbody tr',$(this_btn).closest('table')).length;
	let new_row_name = `new_row_${table_id}_${row_count}`;
	let old_id_html = (table_id == 'languages') ? '' : `<input type="hidden" name="old_ids:list" value="new${row_count}">`;
	let new_btn_html = `
		${old_id_html}
		<span class="btn btn-secondary mr-1 w-100" style="color:#999"
			title="Revoke New Row"
			onclick="javascript:remove_row($(this))">
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
			let tag_name = $(this).prop('tagName').toLowerCase();
			let field_name = $(this).attr('name').split(':')[0]; 
			let field_type = $(this).attr('type');
			let new_field_value  = `new${row_count}`;
			let new_field_name = `${field_name}_${new_field_value}`;
			if ( field_name.slice(-1)=='0' && !field_name.includes('_0_') ) {
				new_field_name = field_name.replace('0', row_count)
			} else if ( field_name.includes('_0_') ) {
				new_field_name = field_name.replace('_0_', `_${row_count}_`)
			}
			$(this).attr('name',new_field_name);
			if (!(tag_name == 'select')) {
				$(this).val(new_field_value);
			};
			if ( tag_name == 'input' && field_type != 'checkbox') {
				$(this).attr('placeholder',new_field_value);
			};
			if ( field_type == 'checkbox' ) {
				$(this).attr('name',`${new_field_name}:int`);
				$(this).val(1);
			};
			if ( $(this).hasClass('url-input') ) {
				$(this).closest('.input-group').replaceWith(`<input class="form-control url-input" name="${escapeHtml(new_field_name)}" placeholder="Select Url..."/>`); 
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

	// Reset the cloned fields toundefined/disabled
	$where_insert.find('input:not([type="checkbox"]),select,textarea').each(function() {
		$(this).val(undefined);
	});
	$('input, textarea, select','tr.row_insert').attr('disabled',true);
};


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// [B] HELPER FUNCTIONS
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


// [1] Remove row from table.
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
function remove_row(context) {
	let table_id  = $(context).closest('table').attr('id').split('_').pop();
	// 1. Remove row from table and set form as modified
	$(context).closest('tr').hide('slow',function(){
		$(this).closest('tr').remove();
		$ZMI.set_form_modified(context);
	});
	// 2. Normalize sorting-UI after deleting a row 
	// if the current table-cell contains a SELECT element
	if ($(context).closest('td').find('select').length > 0) {
		renew_sort_options(this_table = $(context).closest('table'));
	}
};


// [2] Normalize sorting-UI after deleting a row.
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
function renew_sort_options(this_table) {

	let lang = getZMILang();
	// Remove highlighting of new rows
	$('tr[id*="new_row"]').each(function() {
		$(this).removeAttr('id');
	});
	let table_id  = this_table.attr('id').split('_').pop();
	let $rows = $('tbody tr', this_table);
	let sort_options_len = $rows.length;
	let row_counter = 0;
	$rows.each( function() {
		row_counter++;
		let sort_options_html = ``;
		let old_id = $(this).find('td.meta-id input').attr('name');
		let old_id_html = (table_id == 'languages') ? '' : `<input type="hidden" name="old_ids:list" value="${old_id}">`;
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
						hx-on:htmx:after-request="remove_row(this)">
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

// [3] Get language terms count from cached language dictionary.
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
};


// [4] Escape HTML characters
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
const escapeHtml = (unsafe) => {
	return unsafe
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#039;');
}

