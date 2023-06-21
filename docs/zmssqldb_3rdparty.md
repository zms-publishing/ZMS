# Using ZMSSqlDb-Forms in 3rd-View

Include Javascript and CSS from ZMI:

```html
<!-- <script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zms-all.min.js"></script> -->
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/jquery/plugin/jquery.plugin.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/jquery/plugin/jquery.plugin.extensions.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zmi.core.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zmi.internal.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/bootstrap/plugin/bootstrap.plugin.zmi.js"></script>
```

Initialize ZMI Explicitly:

```html
<script>
	$(function() {
		$ZMI.runReady(); 
	});
</script>
```

Include Template zmi_main from Datasource:
