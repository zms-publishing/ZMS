from Products.zms import llmtools


def llmtool_list_content_types(connector, context, args):
    return llmtools.execute_llmtool('list_content_types', args or {}, context)
