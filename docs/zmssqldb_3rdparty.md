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

```html
<tal:block tal:define="zmscontext options/zmscontext;
		datasource zmscontext;
		dummy0 python:request.set('rowid',int(request['rowid']));
		dummy0 python:request.set('qentity',request['tablename']);
		dummy0 python:standard.operator_setitem(request.form,'qentity',request['qentity']);
		dummy0 python:request.set('qindex',request.get('qindex',-1));
		dummy0 python:request.set('ZMS_EXCLUDE_IDS', [...]);
		dummy0 python:request.set('ZMS_DETAILS_EXCLUDE_IDS', [...]);
		dummy0 python:request.set('action',request.get('action','updateForm'))"
	tal:content="structure python:datasource.zmi_main(datasource,request)">
	zmi_main
</tal:block>
```