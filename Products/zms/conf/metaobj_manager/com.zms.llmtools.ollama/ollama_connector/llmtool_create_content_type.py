from Products.zms import llmtools


def llmtool_create_content_type(connector, context, args):
    return llmtools.execute_llmtool('create_content_type', args or {}, context)
