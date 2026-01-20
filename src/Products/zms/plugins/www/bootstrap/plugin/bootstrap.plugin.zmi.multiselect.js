// Hint: To be cached by the browser in sessionStorage
ZMI.prototype.multiselect = function(context) {
	let multiselect_index = 0;
	$("select.zmi-select[multiple]:not(.d-none)",context).each(function() {
		multiselect_index++;
		var refreshContainer = function($container) {
			var c = 0;
			var $select = $container.parent().prev();
			$("option",$select).prop("selected","");
			$container.children().each(function() {
				var data_value = $(this).attr("data-value");
				var val = ($container.hasClass("zmi-sortable")?c+":":"")+data_value;
				$("option[data-value='"+data_value+"']",$select).prop({selected:"selected",value:val});
				c++;
			});
			// sortable(".zmi-select.zmi-sortable", "reload");
		}
		var refreshDropdown = function($select,$dropdown) {
			if ($select.attr('data-autocomplete-add')=="false" 
					|| $(".dropdown-item.d-none",$dropdown).length==$(".dropdown-item",$dropdown).length) {
				$dropdown.hide("normal");
			}
			else {
				$dropdown.show("normal");
			}
		};
		var $select = $(this);
		var $select_disabled = ( $select.attr('disabled')=='disabled' ) ? ' disabled="disabled" ': '';
		$select.next(".zmi-select-container").remove();

		var html = `
			<div class="zmi-select-container form-inline">
				<div class="${$select.attr('class').replace('form-control','')}"></div>
				<div class="btn-group btn-group-sortable mt-2">
					<button type="button" ${$select_disabled} 
						class="btn btn-secondary dropdown-toggle" 
						data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
						<i class="fas fa-plus mr-1"></i>
					</button>
					<div class="dropdown-menu scrollable-menu">`;

		var option_count = $("option",$select).length;
		if (option_count==0) {
			html += '<a class="dropdown-item" href="javascript:;">(No Data)</a>';
		} else if (option_count > 12) {
			html += `
				<div class="dropdown-header menufilter">
					<span class="btn-group">
						<label for="menufilter${multiselect_index}" 
							onmouseover="$('#menufilter${multiselect_index}').focus()">
							<i class="fas fa-filter menufilter" style="cursor:default;"></i>
						</label>
						<input id="menufilter${multiselect_index}"
							placeholder="${getZMILangStr('CAPTION_CHOOSEOBJ')}"
							name="menufilter" type="text" 
							class="form-control dropdown-header"
							title="Filter object list by entering name or id" />
					</span>
				</div>`;
		};
		$("option",$select).each(function() {
			var v = $(this).attr('value');
			$(this).attr('data-value',v);
			html += `<a class="dropdown-item" href="javascript:;" data-value="${v}">${$(this).text()}</a>\n`;
		});
		html += `
					</div><!-- dropdown-menu -->
				</div><!-- btn-group -->
			</div><!-- zmi-select-container -->`;

		$select.addClass("d-none").after(html);
		var $container = $select.next().children(":first");
		var $dropdown = $container.next();
		refreshDropdown($select,$dropdown);
		$("a.dropdown-item",$dropdown).click(function() {
			$(this).addClass("d-none");
			var data_value = $(this).attr('data-value');
			if ( $select_disabled ) {
				$container.append(`<div class="btn bg-light mt-2" disabled="disabled">${$(this).text()}</div>`);
			} else {
				$container.append(`<div class="btn btn-light mt-2" data-value="${data_value}"><a href="javascript:;"><i class="fas fa-times"></i></a> ${$(this).text()}</div>`);
			};
			$(".btn a:last",$container).click(function() {
				var $parent = $(this).parent();
				$("a.dropdown-item[data-value='"+data_value+"']",$dropdown).removeClass("d-none");
				$parent.remove();
				refreshDropdown($select,$dropdown);
				refreshContainer($container);
			});
			refreshDropdown($select,$dropdown);
			refreshContainer($container);
		});
		$("option:selected",this).each(function() {
			var v = $(this).attr('data-value');
			$("a.dropdown-item[data-value='"+v+"']",$dropdown).click();
		});
		pluginSortable(".zmi-select.zmi-sortable",function() {
			sortable(".zmi-select.zmi-sortable",{
				forcePlaceholderSize: true,
				placeholderClass: 'btn btn-light sortable-placeholder',
			});
			$(".zmi-select.zmi-sortable").bind('sortupdate', function() {
				refreshContainer($container);
			});
		});

		// +++++++++++++++++++++++++++
		// Menufilter: Object-List
		// +++++++++++++++++++++++++++
		$('#menufilter'+multiselect_index).keyup(function (event) {
			let menufilter = $(this).val();
			if (isModifierKeyPressed(event)) {
				return; // ignore
			}
			if (event.which == 13) {
				event.preventDefault();
			};
			$("a.dropdown-item",$dropdown).each(function() {
				if ($(this).text().toLowerCase().indexOf(menufilter.toLowerCase()) >= 0) {
					$(this).show();
				} else {
					$(this).hide();
				}
			});
		});

		// Reset filter on dropdown shown
		$dropdown.parent().on('shown.bs.dropdown', function () {
			$('#menufilter' + multiselect_index).val('').trigger('keyup').focus();
		});

	});

	// Function to check if a modifier key is pressed
	/**
	 * Check if a modifier key (Alt, Ctrl, Meta) is pressed.
	 * @param {Event} event - The keyboard event to check.
	 * @returns {boolean} - True if a modifier key is pressed, false otherwise.
	 */
	function isModifierKeyPressed(event) {
		return event.altKey ||
		event.ctrlKey ||
		event.metaKey;
	}
}