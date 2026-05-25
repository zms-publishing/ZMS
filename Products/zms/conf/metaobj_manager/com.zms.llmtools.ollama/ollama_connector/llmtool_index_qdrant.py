from Products.zms import llmtools


def llmtool_index_qdrant(connector, context, args):
    return llmtools.execute_llmtool('index_qdrant', args or {}, context)
