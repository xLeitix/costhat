from timeit import timeit
from random import *
from costhat import *
import sys

sys.setrecursionlimit(1000000)


node_test_config = {
    'min_nodes' : 10,
    'max_nodes': 8000,
    'nodes_step': 50,
    'max_ep_per_s' : 10,
    'edge_per_ep' : 1
}

edge_test_config = {
    'graph_size' : 5000,
    'ep_per_s': 2,
    'min_edges' : 100,
    'max_edges': 8000,
    'edges_step': 50
}

def generate_node_test_model(nodes, max_ep, edge_per_ep, type):
    _cntr = 1
    _nodes = 0
    services = []
    while _nodes < nodes:
        if type == 'INSTANCE':
            _cntr += 1
            eps_count = randint(1, max_ep)
            _nodes += eps_count
            eps = []
            for _ in range(eps_count):
                ep = InstanceEndpoint("E%d" % _cntr)
                _cntr += 1
                ep.configure_endpoint({'capi' : 1, 'cio' : 1, 'load_factor' : 1, "coth" : 1})
                callgraph = []
                for _ in range(edge_per_ep):
                    s, e = _random_ep(services)
                    if not s == None:
                        callgraph.append((s, e, 1))
                if not len(callgraph) == 0:
                    ep.set_callgraph(callgraph)
                eps.append(ep)
            s = InstanceService("S%d" % _cntr, eps)
            s.configure_service({'cost_per_instance' : 1})
            services.append(s)
        else:
            _cntr += 1
            eps_count = randint(1, max_ep)
            _nodes += eps_count
            eps = []
            for _ in range(eps_count):
                ep = LambdaEndpoint("E%d" % _cntr)
                _cntr += 1
                ep.configure_endpoint({'capi': 1, 'cio': 1, 'ccmp': 1, "coth": 1})
                callgraph = []
                for _ in range(edge_per_ep):
                    s, e = _random_ep(services)
                    if not s == None:
                        callgraph.append((s, e, 1))
                if not len(callgraph) == 0:
                    ep.set_callgraph(callgraph)
                eps.append(ep)
            s = LambdaService("S%d" % _cntr, eps)
            services.append(s)
    model = CosthatModel(services)
    return model

def generate_edge_test_model(nodes, ep_count, edges, type):
    _cntr = 1
    _nodes = 0
    services = []
    while _nodes < nodes:
        if type == 'INSTANCE':
            _cntr += 1
            _nodes += ep_count
            eps = []
            for _ in range(ep_count):
                ep = InstanceEndpoint("E%d" % _cntr)
                _cntr += 1
                ep.configure_endpoint({'capi' : 1, 'cio' : 1, 'load_factor' : 1, "coth" : 1})
                eps.append(ep)
            s = InstanceService("S%d" % _cntr, eps)
            s.configure_service({'cost_per_instance' : 1})
            services.append(s)
        else:
            _cntr += 1
            _nodes += ep_count
            eps = []
            for _ in range(ep_count):
                ep = LambdaEndpoint("E%d" % _cntr)
                _cntr += 1
                ep.configure_endpoint({'capi': 1, 'cio': 1, 'ccmp': 1, "coth": 1})
                eps.append(ep)
            s = LambdaService("S%d" % _cntr, eps)
            services.append(s)
    for _ in range(edges):
        s_source, e_source = _random_ep(services)
        s_target, e_target = _random_ep(services)
        while(s_source.name > s_target.name):
            s_source, e_source = _random_ep(services)
            s_target, e_target = _random_ep(services)
        if not hasattr(e_source, 'callgraph'):
            e_source.set_callgraph( [(s_target, e_target, 1)] )
        else:
            e_source.callgraph.append((s_target, e_target, 1))

    model = CosthatModel(services)
    return model

def _random_ep(services):
    if len(services) == 0:
        return (None, None)
    s = choice(services)
    e = choice(s.eps)
    return (s, e)

def calculate_costs():
    MODEL.calculate_costs(WORKLOAD)

# BEGIN MAIN TEST FILE

MODEL = None
WORKLOAD = None

OUT_FILE = 'numerical_eval.csv'
with open(OUT_FILE, 'w') as _file:

    _file.write("TESTTYPE;INSTANCETYPE;SIZE;VALUE\n")

    # # run node tests
    # for instancetype in ("INSTANCE", "LAMBDA"):
    #     curr_nodes = node_test_config['min_nodes']
    #     while curr_nodes <= node_test_config['max_nodes']:
    #         MODEL = generate_node_test_model(curr_nodes, node_test_config['max_ep_per_s'], node_test_config['edge_per_ep'], instancetype)
    #         # MODEL.xmlpickle("xmlconfigs/node_%s_%d.xml" % (instancetype, curr_nodes))
    #         WORKLOAD = { MODEL.services[0] : { MODEL.services[0].eps[0] : 1 } }
    #         time = timeit(calculate_costs, number=100)
    #         str = "NODE;%s;%d;%d\n" % (instancetype, curr_nodes, (time * 1000))
    #         _file.write(str)
    #         print str
    #         curr_nodes += node_test_config['nodes_step']

    # run edge tests
    for instancetype in ("INSTANCE", "LAMBDA"):
        curr_edges = edge_test_config['min_edges']
        while curr_edges <= edge_test_config['max_edges']:
            MODEL = generate_edge_test_model(edge_test_config['graph_size'], edge_test_config['ep_per_s'], curr_edges, instancetype)
            # MODEL.xmlpickle("xmlconfigs/edge_%s_%d.xml" % (instancetype, curr_edges))
            WORKLOAD = {MODEL.services[0]: {MODEL.services[0].eps[0]: 1}}
            time = timeit(calculate_costs, number=100)
            str = "EDGE;%s;%d;%d\n" % (instancetype, curr_edges, (time * 1000))
            _file.write(str)
            print str
            curr_edges += edge_test_config['edges_step']