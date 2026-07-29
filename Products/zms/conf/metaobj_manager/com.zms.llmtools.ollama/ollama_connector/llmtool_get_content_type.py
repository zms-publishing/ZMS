from Products.zms import llmtools


def llmtool_get_content_type(connector, context, args):
    return llmtools.execute_llmtool('get_content_type', args or {}, context)
