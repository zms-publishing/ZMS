## Script (Python) "getTeaserElements"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Function: Teaser-Elements
##
# --// BO getTeaserElements //--

request = container.REQUEST
teaserElmnts = []
obs = context.breadcrumbs_obj_path(portalMaster=False)
obs.reverse()
this = context.getSelf()
for ob in obs:
  abort_penetrance = ob != this and ob.meta_type == 'ZMSLinkElement'
  if abort_penetrance:
    break
  temp = []
  subobs = ob.filteredChildNodes( request, ['ZMSCustom','ZMSTeaserContainer'])
  for subob in subobs:
    if subob.meta_id == 'ZMSTeaserContainer':
      temp.extend( subob.filteredChildNodes( request))
    elif subob.getType() == 'ZMSTeaserElement':
      temp.append( subob)
  for teaserElmnt in temp:
    penetrance = teaserElmnt.attr('attr_penetrance')
    if ( penetrance in [0,'this',''] and context == ob) or \
       ( penetrance in [1,'sub_nav'] and context.meta_id in ['ZMS','ZMSFolder']) or \
       ( penetrance in [2,'sub_all']):
      teaserElmnts.insert( 0, teaserElmnt)
  abort_penetrance = ob.attr('attr_zmsteasercontainer_abort_penetrance') not in ['',0]
  if abort_penetrance:
    break
teaserElmnts.reverse()
return teaserElmnts

# --// EO getTeaserElements //--
