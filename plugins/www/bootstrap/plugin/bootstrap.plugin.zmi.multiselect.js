ZMI.prototype.multiselect = function(context) {
				var refreshContainer = function($container) {
					var c = 0;
					var $select = $container.prev();
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
				var refreshDropdown = function($dropdown) {
					if ($("li.hidden",$dropdown).length==$("li",$dropdown).length) {
						$dropdown.hide("normal");
					}
					else {
						$dropdown.show("normal");
					}
				}
				$("select.zmi-select[multiple]:not(.hidden)",context).each(function() {
					var $select = $(this);
					var html = ''
						+ '<div class="'+$(this).attr('class')+'">'
						+ '</div>'
						+ '<div class="btn-group btn-group-sortable">\n'
						+ '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">\n'
						+ $ZMI.icon('icon-plus')
						+ '</button>'
						+ '<ul class="dropdown-menu scrollable-menu">';
					var c = 0;
					$("option",$select).each(function() {
						var v = $(this).attr('value');
						$(this).attr('data-value',v);
						html += ''
							+ '<li>\n'
							+ '<a href="javascript:;" data-value="'+v+'">\n'
							+ $(this).text()
							+ '</a>\n'
							+ '</li>\n';
						c++;
					});
					html += ''
						+ '</ul>'
						+ '</div>';
					$(this).addClass("hidden").after(html);
					var $container = $select.next();
					var $dropdown = $container.next();
					$("li a",$dropdown).click(function() {
						$(this).parent().addClass("hidden");
						refreshDropdown($dropdown);
						var data_value = $(this).attr('data-value');
						$container.append(''
							+'<div class="btn" data-value="'+data_value+'">'
							+'<a href="javascript:;">'+$ZMI.icon('icon-remove')+'</a> '
							+$(this).text()
							+'</div>'
						);
						$(".btn a:last",$container).click(function() {
							var $parent = $(this).parent();
							$("li a[data-value='"+data_value+"']",$dropdown).parent().removeClass("hidden");
							$parent.remove();
							refreshDropdown($dropdown);
							refreshContainer($container);
						});
						refreshDropdown($dropdown);
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