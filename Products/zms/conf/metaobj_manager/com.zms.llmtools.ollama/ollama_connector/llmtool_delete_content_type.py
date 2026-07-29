from Products.zms import llmtools


def llmtool_delete_content_type(connector, context, args):
    return llmtools.execute_llmtool('delete_content_type', args or {}, context)
