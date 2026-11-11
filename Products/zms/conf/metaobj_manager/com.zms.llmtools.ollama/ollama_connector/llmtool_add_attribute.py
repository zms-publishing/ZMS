from Products.zms import llmtools


def llmtool_add_attribute(connector, context, args):
    return llmtools.execute_llmtool('add_attribute', args or {}, context)
