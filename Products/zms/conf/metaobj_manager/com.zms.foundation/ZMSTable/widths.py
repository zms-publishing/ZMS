## Script (Python) "ZMSTable.widths"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Col-Widths [list]
##
# --// BO widths //--

REQUEST = zmscontext.REQUEST
table = zmscontext.attr('table')
ncols = max([len(x) for x in table])
weights = [1 for x in range( ncols)]
for row in table:
    i = 0
    for cell in row:
        weight = len(zmscontext.re_sub('<(.*?)>', '',zmscontext.dt_exec(cell.get('content',''))))
        weights[i] = weights[i] + weight
        i += 1
return [int((x*100.0)/sum(weights)) for x in weights]

# --// EO widths //--
