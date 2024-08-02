# Why are ZMS Themes located in a folder named ./skins by default?

In Zope, web design themes traditionally are referred to as “skins” because they essentially provide a layer of visual styling and presentation over the core functionality of the web application. This concept is similar to how a “skin” in other contexts (like media players or video games) changes the appearance without altering the underlying functionality.

The terminology may be a bit confusing, especially for those who are new to Zope or web development in general.
The reason why ZMS themes are located in a folder named `./skins` is because ZMS is built on top of Zope, and Zope uses the term “skin” to refer to themes. This is a historical artifact from the early days of Zope, and it has stuck around even as the web development landscape has evolved.
The Zope Product *CMFCore* provides the infrastructure for managing file system resources. File directories are registered by *CMFCore.registerDirectory* and thus Zope can get access to file system directories containing skin resources (like CSS files, images, and templates) for customizing the appearance of a website.

**By default** *CMFCore.registerDirectory* registers the directory name './skins' for that purpose as a root directory for file system resources. So, ZMS still uses this convention to store themes in a folder named `./skins`.\
But this is just a default *convention*, and you can *customize* the location of your themes by declaring the corresponding *directory* attribute in the Zope configuration file `./configure.zcml` of ZMS:\
https://github.com/zms-publishing/ZMS/blob/main/Products/zms/configure.zcml

To leave the ZMS source code unchanged, actually you can do this in a second file named *Products.zms/overrides.zcml*. This will override *configure.zcml* and ZMS will use it's directory declarations to look for filesystem resources. This is recommended if you want to organize your themes in a different way or if you want to use a different mechanism to register directories with Zope. 

Example: *Products.zms/overrides.zcml*

```xml
<configure
	xmlns="http://namespaces.zope.org/zope"
	xmlns:browser="http://namespaces.zope.org/browser">
	<browser:resourceDirectory
		name="zms_"
		directory="plugins/www"
	/>
	<!-- If ZMI resources need to be published, -->
	<!-- register the resources dir as public   -->
	<!-- 
	<browser:resourceDirectory
		name="zmi"
		directory="~/virtualenv/src/zope/src/zmi/styles/resources"
		permission="zope.Public" 
	/> 
	-->
	<configure
		xmlns:cmf="http://namespaces.zope.org/cmf"
		xmlns:zcml="http://namespaces.zope.org/zcml"
		zcml:condition="installed Products.CMFCore">
		<cmf:registerDirectory name="skin_zms5_minimal" recursive="True" />
		<cmf:registerDirectory name="themes" directory="/home/zope/src/zms_themes" recursive="True" />
	</configure>
</configure>
```

In this example, the new directory `/home/zope/src/zms_themes` is registered as a additional skin directory for ZMS. This allows you to organize your themes in a different location than the default `./skins` folder. The given *name*-attribute of the directory registration is essential, because it will be shown in the Zope-GUI as the root name of the declared  directory [1]. You can add as many directories as you like, and you can also use the `recursive` attribute to include subdirectories.

---

**[1] ZMS monkey patch for CMFCore.registerDirectory()**: 
CMFCore assumes that the ./skins directory always is located in the root of the Python module's directory (e.g. for ZMS it might be `/home/zope/venv/lib/python3.12/site-packages/Products/zms/skins`). For showing the path-name in the Zope-GUI the method *CMFCore.registerDirectory()* cuts off the first part of the path before the keyword 'skins'. That cutoff length is constantly referring to the *module's path* - and not the (optionally) declared path of the directory itself. So, if you do not want to place all your theme-data into the ZMS default ./skins-folder but into a different directory structure, that code requires a path length that is identical to the length of the ZMS-skins folder.
To avoid this inconvenience, ZMS has introduced a monkey patch that overrides the method *CMFCore.registerDirectory()* for using the *name*-attribute for path slicing instead of constantly using the keyword *skins*. Now the path-prefix *skins* is only shown in Zope-GUI by default if a directory name is not given. If a directory name is given the *name*-attribute will be used as keyword for slicig the path.\ 

[https://github.com/zms-publishing/ZMS/blob/main/Products/zms/\_\_init\_\_.py](https://github.com/zms-publishing/ZMS/blob/main/Products/zms/__init__.py#L51-L92)


```python
# subdir = str(directory[len(_context.package.__path__[0]) + 1:])
subdir = str(name)
```