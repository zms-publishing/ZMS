# Using ZMSSqlDb-Forms in 3rd-View
Include Javascript and CSS from ZMI:

*all*
```html
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zms-all.min.js"></script>
```

*individual*
```html
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/jquery/plugin/jquery.plugin.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/jquery/plugin/jquery.plugin.extensions.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zmi.core.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/zmi.internal.js"></script>
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/bootstrap/plugin/bootstrap.plugin.zmi.js"></script>
```

Initialize ZMI explicitly:

```html
<script>
	$(function() {
		$ZMI.runReady(); 
	});
</script>
```

## Grid
_TODO_

## Edit-Form
Include Template with *updateForm* through ```zmi_main``` from datasource:

```
<tal:block tal:define="standard modules/Products.zms/standard;
        db python:here.getLinkObj(here.getConfProperty('ZMS.permalink.db'));
        entities python:db.getEntities();
        tables python:[x for x in entities if x['type'].upper()=='TABLE'];
        dummy0 python:request.set('qentity','employees');
        dummy0 python:standard.operator_setitem(request.form,'qentity',request['qentity']);
        dummy0 python:request.set('rowid',request.get('rowid',1));
        dummy0 python:request.set('qindex',request.get('qindex',-1));
        dummy0 python:request.set('ZMS_EXCLUDE_IDS',[]);
        dummy0 python:request.set('ZMS_DETAILS_EXCLUDE_IDS',[]);
        dummy0 python:request.set('action',request.get('action','updateForm'));">
    <tal:block tal:content="structure python:db.zmi_main(db,request)">zmi_main</tal:block>
</tal:block>
```

## Links
* [SQLite Sample Database](https://www.sqlitetutorial.net/sqlite-sample-database/)