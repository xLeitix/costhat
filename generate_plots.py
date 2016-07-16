from ggplot import *
import pandas

data = pandas.read_csv('numerical_eval.csv', sep=';')

_nodes = data[data.TESTTYPE == 'NODE']
_edges = data[data.TESTTYPE == 'EDGE']

print ggplot(_nodes, aes(x='SIZE',y='VALUE',colour='BACKED')) + \
    geom_line() + \
    scale_x_continuous() + \
    scale_y_continuous() + \
    labs(x = "# of Nodes", y = "Duration of 100 Cost Calculations [ms]")

print ggplot(_edges, aes(x='SIZE',y='VALUE',colour='BACKED')) + \
    geom_line() + \
    scale_x_continuous() + \
    scale_y_continuous() + \
    labs(x="# of Service Calls", y="Duration of 100 Cost Calculations [ms]")