# ZMS Development

## Practical Examples for Using API Functions

### 1. renderShort()
The function `renderShort()` renders a plain view of a content block shown in the ZMI. For page-like container objects this might be just the short title (titlealt) attribute; actually this is what happens by default when you see a sequence of ZMSDocument containers in the ZMI.
For content-containing objects like ZMSTextarea their function `standard_html()` is used as the *renderShort*-view by default.

To any object class defined via ZMS configuration menu a custom `renderShort()` function (primitive type *py* or *zpt*) can be added optionally. This will overwrite its default ZMI view. The following picture shows an enhanced view of the ZMSDocument items followed by a python snippet generating this view:


![Add ZMS](images/develop_api_renderShort.png)
*Adding a renderShort function as a py-primitive allow you to customize the objects view in the ZMS GUI*

#### Custom Code Example
The code shows the title and the desciption attribute. Conditionally a warning is shown if the editor forgot naming the creator of the document:
```python
## Script (Python) "ZMSDocument.renderShort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Overwrite renderShort
##
# --// renderShort //--
alert = '<div class="alert alert-warning mx-0">Creator is missing!</div>'
if zmscontext.attr('attr_dc_creator'): 
    alert=''
return '<h1>%s<br/><small>%s</small></h1>%s'%(zmscontext.attr('title'), zmscontext.attr('attr_dc_description'), alert)
# --// /renderShort //--
```

