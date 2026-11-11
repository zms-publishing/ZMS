from Products.zms import llmtools


def llmtool_update_attribute_custom(connector, context, args):
    return llmtools.execute_llmtool('update_attribute_custom', args or {}, context)
