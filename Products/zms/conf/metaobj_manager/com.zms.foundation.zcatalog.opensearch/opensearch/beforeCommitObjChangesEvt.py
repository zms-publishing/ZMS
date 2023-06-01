## Script (Python) "beforeCommitObjChangesEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=Calling Global Change-Event Handler for (Re-)Indexing a Document
##
from Products.zms import standard
try:
	return container.add_docmt_to_opensearch_index(context)
except:
	standard.writeBlock(context.getId(), "ERROR: [beforeCommitObjChangesEvt] failed adding content to opensearch index")
