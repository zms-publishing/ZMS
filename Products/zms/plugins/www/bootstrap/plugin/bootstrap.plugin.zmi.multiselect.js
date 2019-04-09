ZMI.prototype.multiselect = function(context) {
				var refreshContainer = function($container) {
					var c = 0;
					var $select = $container.parent().prev();
					$("option",$select).prop("selected","");
					$container.children().each(function() {
						var data_value = $(this).attr("data-value");
						$ZMI.writeDebug("refreshContainer: data-value="+data_value);
						var val = ($container.hasClass("zmi-sortable")?c+":":"")+data_value;
						$ZMI.writeDebug("refreshContainer: val="+val);
						$("option[data-value='"+data_value+"']",$select).prop({selected:"selected",value:val});
						c++;
					});
				}
				var refreshDropdown = function($select,$dropdown) {
					if ($select.attr('data-autocomplete-add')=="false" || $("li.d-none",$dropdown).length==$("li",$dropdown).length) {
						$dropdown.hide("normal");
					}
					else {
						$dropdown.show("normal");
					}
				}
				$("select.zmi-select[multiple]:not(.d-none)",context).each(function() {
					var $select = $(this);
					$select.next(".zmi-select-container").remove();
					var html = ''
						+ '<div class="zmi-select-container">'
						+ '<div class="'+$select.attr('class')+'">'
						+ '</div>'
						+ '<div class="btn-group btn-group-sortable">\n'
						+ '<button type="button" class="btn btn-secondary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">\n'
						+ $ZMI.icon('icon-plus')
						+ '</button>'
						+ '<div class="dropdown-menu scrollable-menu">';
					var c = 0;
					$("option",$select).each(function() {
						var v = $(this).attr('value');
						$(this).attr('data-value',v);
						html += ''
							+ '<a class="dropdown-item" href="javascript:;" data-value="'+v+'">\n'
							+ $(this).text()
							+ '</a>\n';
						c++;
					});
					html += ''
						+ '</div>'
						+ '</div>'
						+ '</div>';
					$select.addClass("d-none").after(html);
					var $container = $select.next().children(":first");
					var $dropdown = $container.next();
					refreshDropdown($select,$dropdown);
					$("li a",$dropdown).click(function() {
						$(this).parent().addClass("d-none");
						var data_value = $(this).attr('data-value');
						$container.append(''
							+'<div class="btn" data-value="'+data_value+'">'
							+'<a href="javascript:;">'+$ZMI.icon('icon-times')+'</a> '
							+$(this).text()
							+'</div>'
						);
						$(".btn a:last",$container).click(function() {
							var $parent = $(this).parent();
							$("li a[data-value='"+data_value+"']",$dropdown).parent().removeClass("d-none");
							$parent.remove();
							refreshDropdown($select,$dropdown);
							refreshContainer($container);
						});
						refreshDropdown($select,$dropdown);
						refreshContainer($container);
					});
					$("option:selected",this).each(function() {
						var v = $(this).attr('data-value');
						$("li a[data-value='"+v+"']",$dropdown).click();
					});
				});
				pluginUI("div.zmi-select.zmi-sortable",function() {
					$("div.zmi-select.zmi-sortable").sortable({
						tolerance:'pointer',
						forcePlaceholderSize:true,
						forceHelperSize:true,
						placeholder: "ui-state-highlight",
						revert: true,
						stop: function(event, ui) {
							refreshContainer($(this));
						}
					});
				});
}