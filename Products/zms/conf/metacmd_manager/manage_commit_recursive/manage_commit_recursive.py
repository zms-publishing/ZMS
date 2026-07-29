## Script (Python) "manage_commit_recursive"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Commits rekursivly all document changes beginning with this node
##
request = container.REQUEST
RESPONSE =  request.RESPONSE
request.set('count',0)
request.set('doc_container_id','e0')

def commit_tree(node):
    for ob in node.getChildNodes(request):
        doc_containers = [ e for e in ob.breadcrumbs_obj_path() if e.meta_id in ['ZMS','ZMSDocument','ZMSFolder'] ]
        doc_container = doc_containers[-1]
        if ob.isObjModified(request) and doc_container.getId()!=request.get('doc_container_id'):
            # Document Container of Object Change
            doc_container.commitObj(request)
            request.set('count',request['count']+1)
            request.set('doc_container_id',doc_container.getId())
        commit_tree(ob)

# Init
commit_tree(context)

request.set('message','%i Changes committed.'%(request['count']))
return request['message']
