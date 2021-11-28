# ZMS Administration: The Configuration Menu
*@work...*

The configuration menu primarily provides ten options for the configuration of the ZMS client:
1. User: managing user accounts and access rights
2. System: system variables, multisite hierarchies, functional components
3. Languages: languages and their editorial dependencies 
4. Meta-Attributes: general content attributes
5. Content-Objects: modelling content classes
6. Paragraph-Formats: text block formats 
7. Character-Formats: text inline formats
8. Actions: additional / self-programmed helper functions
9. Search: configuring content indexing
10. Design: design themes and JS/CSS customization 

---

## Meta-Attributes
Meta attributes ("metas") are a set of general descriptions supporting the automatic processing of content entities (e.g. keyword search). The idea of schematic categorization of content has a long tradition; for web content it started 1994 with the Dublin Core (DC) Metadata Initiative [https://en.wikipedia.org/wiki/Dublin_Core]. ZMS refers to the DC metadata set and provides a minimal list of standard attributes. The ZMS administrator can add further attributes to the list and assign a data type to each of these attributes. In fact, each meta-attribute becomes another data type and extends the list of data types.
Since each content class can use these metas as its own attributes, the entire namespace of the attributes is reduced and template coding becomes easier.

![Administration of Metadata](images/admin_gui_metas1.gif)
_Administration of metadata_



## Search: Using Zope-ZCatalog
The ZCatalog module provides a simple index for Zope contents. ZMS can address this index by default: the admin menu *Search* allows to select all the content object classes and their attributes to be indexed.
Via *ZCatalog-Connector* tab the Zope objects containing the index are listed and can be administered (by buttons like *Delete*, *Refresh" etc.).

![Administration of Metadata to be indexed](images/admin_gui_search1.gif)
_Administration of metadata to be indexed_

![Administration of the Indexer Connector](images/admin_gui_search2.gif)
_Administration of the indexer connector_




To show the search functionality in the 3rd view the templates need to provide the following references:
1. location of the search form
2. linking the JavaScript-Libs for asynchronous listing of the search results

First a ZMS document node is needed for showing the search form and the results; this can be an ordinary ZMSDocument object having an ordinary ZMSTextare containing the TAL code for the search form:

```html
<form class="search" method="get">

	<tal:block tal:condition="python:request.get('searchform',True)">
	<input tal:condition="python:request.get('searchform')" type="hidden" name="searchform" tal:attributes="value python:request.get('searchform')" />
	<input tal:condition="python:request.get('lang')" type="hidden" name="lang" tal:attributes="value python:request.get('lang')" />
	<input tal:condition="python:request.get('preview')" type="hidden" name="preview" tal:attributes="value python:request.get('preview')" />
	<legend tal:content="python:here.getZMILangStr('SEARCH_HEADER')">Search header</legend>
	<div class="form-group">
		<div class="col-md-12">
			<div class="input-group">
				<tal:block tal:content="structure python:here.getTextInput(fmName='searchform',elName='search',value=request.get('search',''))">the value</tal:block>
				<span class="input-group-btn">
			<button type="submit" class="btn btn-primary">
				<i class="fa fa-search icon-search"></i>
			</button>
				</span>
			</div>
		</div>
	</div><!-- .form-group -->
	<div class="form-group row" tal:condition="python:here.getPortalMaster() is not None or len(here.getPortalClients())>0">
		<div class="control-label col-md-12" tal:define="home_id python:here.getHome().id">
			<input type="hidden" name="home_id" tal:attributes="value python:request.get('home_id',home_id); data-value home_id">
			<input type="checkbox" class="form-check-input" onchange="var $i=$('input[name=home_id]');$i.val(this.checked?$i.attr('data-value'):'');" tal:attributes="checked python:['','checked'][request.get('home_id',home_id)==home_id]">
			<label class="form-check-label control-label">
				<strong tal:content="home_id">the home-id</strong> (local)
			</label>
		</div>
	</div><!-- .form-group -->
	</tal:block>

<div id="search_results" class="form-group" style="display:none">
	<div class="col-md-12">
		<h4 tal:content="python:here.getZMILangStr('SEARCH_HEADERRESULT')">
			Result
		</h4>
		<div class="header row">
			<div class="col-md-12">
				<span class="small-head">
					<span class="glyphicon glyphicon-refresh fas fa-spinner fa-spin" alt="Loading..."></span>
					<tal:block tal:content="python:here.getZMILangStr('MSG_LOADING')">loading</tal:block>
				</span>
			</div>
		</div><!-- .header.row -->
		<div class="line row"></div><!-- .row -->
			<div class="pull-right">
				<ul class="pagination"></ul>
			</div>
	</div>
</div>

</form>
```
The TAL code has two sections:
1. input form (with optional toggle for local search-results only inside current site) 
2. html placeholder for presenting search results and pagination 

The form's request is responded by an XML stream which is transformed into an HTML list by JavaScript. That is why the frontend code need to reference a special, ready to use JS module for handling the search gui:

```html
<script type="text/javascript" charset="UTF-8" src="/++resource++zms_/ZMS/zmi_body_content_search.js"></script>
```

Hint:
The page containing the search form may be linked from different navigation items. Instead of linking the node explicitly it might be easier to reference the page with a "permalink" (as metalement of the ZMS-root node). In the first element of the master template _standard_html_ the link to that page can defined as an object variable like this

```html
<html lang="en" 
	tal:define="zmscontext options/zmscontext;
		search_node python: zmscontext.getLinkObj( zmscontext.getConfProperty( 'ZMS.permalink.search', default='{$@content}'), request);">
```
and a link to the search page can be generated like this;

```html
<a href="#" class="nav-item pr-3" 
	tal:attributes="href python:search_node.getHref2IndexHtml(request)">
	<i class="fas fa-search"></i>&nbsp;
	<span tal:replace="python:zmscontext.getLangStr('SEARCH')">Suche</span>
</a>
```

## Managing ZMS Custom Code & Configurations

ZMS can contain a lot of custom code defining metadata, content models, custom actions, workfow steps and Zope object bundeled as ZMS libraries.
To maintain this code externally  ZMS offers a module called "Repository Manager"; the ZMS Administrator can activate this aditional functionality in the system menu:

![Adding the ZMS Repository Manager](images/admin_repo_init.png)
_Adding the ZMS Repository Manager_

In general the Repository Manager allows the synchronisation of the ZMS custom code by export/importing it between ZODB and file-system. It's _properties menu_ provides the definition of a target folder where the ZMS code is replicated into the file system. The code differences between ZODB and file-system are shown in detail as a list of the diff-marked files.

![ZMS Repository Manager Menu](images/admin_repo_view.png)
_ZMS Repository Manager menu: code files containg differences can be synct by "Export" (ZODB to file-system) or "Import" (file-system to ZODB)_


### ZMS Git Bridge

The ZMS Git bridge is a very simple approach to establish Git-based collaboration to the code management in ZMS. Thus the TTW-coding, which is very efficient for many project setups, still can be applied while combined with a professional code version management and deployment. 

In this scenario the system folder containing the exported Zope/ZMS code files will be a clone of an external Git repository. To synchronize the code by Git the ZMS Repository Manager can be extended by a set of specific ZMS-actions (named like _manage_repository\__*). As a default ZMS provides three preconfigured actions (gitconfig. gitpull, gitpush). These easily can be imported via the _Actions_ menu:

![Import Git Actions](images/admin_repo_import_gitactions.png)
_Import three Git actions used in ZMS Repository Manager_

After importing the Git actions the ZMS Repository Manager shows an additional pop-up button "Repository Interactions". Any action is represented as a menu item.

![Repository Manager GUI](images/admin_repo_show_gitactions.png)
_ZMS Repository Manager GUI enhanced by Git actions_


The additional menu provides there functions:
1. _Git Configuration_: needs the Git URL, allows the cloning of the repository
2. _Git Pull_: pulls the latest revsion by default; optionally entering a revision id may pull a specific revision
3. _Git Push_: allows entering a commit message and executes the Git push onto the repository server

![Git push menu](images/admin_repo_show_gitpush.png)
_Git push menu: before executing the Git push a commit message can be entered_

![Git push executed](images/admin_repo_execute_gitpush.png)
_Git push return: after executing the Git push the commit will be shown on the Git repo (e.g. at github.com)_

---

### Some Hints about Git Configuration
The ZMS Git Bridge uses just a minimal set of Git commands:
1. Git Pull: pulls (combined with a checkout) the latest version of the main branch ("HEAD") or alternativly pulls a specified revision by a checkout command
2. Git Push:  pushes code status into the main branch

The Git URL (saved by the _Git Configuration_ menu) is (only) necessary if a cloning will be performed by the ZMS GUI and the .git/config file will be written initally.
If the git folder is already configured it is not needed to save the Git URL in the ZMS Git Configuration.

Actually it is recommended to configure the Git folder properly before using it with ZMS. Because the ZMS Git Bridge does not save any user data a special Git user and its certificate should be available in the file system and be accessible by the zope user.

EXAMPLE:

1. `/home/my/.ssh/my_cert`
2. `/home/my/.ssh/my_cert.pub`
3. `/home/my/.ssh/config` :

	```ini
	Host github.com
		HostName github.com
		IdentityFile ~/.ssh/my_cert
		User git
	```

4. `/home/my/src/myproject/.git/config` :

	```ini
	[user]
		name=mygituser
		email=mygituser@mydomain.tld
	[core]
		repositoryformatversion = 0
		filemode = true
		symlinks=true
		bare = false
		logallrefupdates = true
	[remote "origin"]
		url = git@github.com:mydomain/myproject.git
		fetch = +refs/heads/*:refs/remotes/origin/*
	[branch "master"]
		remote = origin
		merge = refs/heads/master
	```