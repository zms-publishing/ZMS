# Using ZMSSqlDb-Forms in 3rd-View

## Prerequisites
* Zope Database Adapter
* ZMS SQL-Datasource for the Database Adapter
* Permalink to ZMS SQL-Datasource with key ```db```

## Assets
Include Javascript (and CSS) from ZMI:

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
Include Template with *noFilterForm* through ```zmi_main``` from datasource:

```html
<tal:block tal:define="standard modules/Products.zms/standard;
        db python:here.getLinkObj(here.getConfProperty('ZMS.permalink.db'));
        dummy0 python:request.set('qentity','employees');
        dummy0 python:request.set('action',request.get('action','noFilterForm'));">
    <tal:block tal:content="structure python:db.zmi_main(db,request)">zmi_main</tal:block>
</tal:block>
```

## Form
Include Template with *updateForm* through ```zmi_main``` from datasource:

```html
<tal:block tal:define="db python:here.getLinkObj(here.getConfProperty('ZMS.permalink.db'));
        dummy0 python:request.set('qentity','employees');
        dummy0 python:request.set('rowid',request.get('rowid',1));
        dummy0 python:request.set('qexcludeids',['PHONE','FAX']);
        dummy0 python:request.set('action',request.get('action','updateForm'));">
    <tal:block tal:content="structure python:db.zmi_main(db,request)">zmi_main</tal:block>
</tal:block>
```
## Save
```TODO```

## Links
* [SQLite Sample Database](https://www.sqlitetutorial.net/sqlite-sample-database/)