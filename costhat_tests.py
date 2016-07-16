from costhat import *

def truncate(f):
    return float('%.3f'%(f))

def test_basic_lambda_service():

    sae = LambdaEndpoint('ea')
    sa = LambdaService('a', [sae])
    sae_cf = {'capi' : 1, 'cio' : 0, 'ccmp' : 2, "coth" : 5}
    sae.configure_endpoint(sae_cf)

    sbe = LambdaEndpoint('eb')
    sb = LambdaService('b', [sbe])
    sbe_cf = {'capi' : 0, 'cio' : 0, 'ccmp' : 1, "coth" : 10}
    sbe.configure_endpoint(sbe_cf)

    sce = LambdaEndpoint('ec')
    sc = LambdaService('c', [sce])
    sce_cf = {'capi' : 1, 'cio' : 1, 'ccmp' : 1, "coth" : 0}
    sce.configure_endpoint(sce_cf)

    sae_cg = [(sb, sbe, 1), (sc, sce, 4)]
    sae.set_callgraph(sae_cg)

    sbe_cg = [(sc, sce, 0.1)]
    sbe.set_callgraph(sbe_cg)

    model = CosthatModel([sa, sb, sc])

    # test 1
    inward1 = {sa : { sae : 10 }}
    costs = truncate(model.calculate_costs(inward1))
    expected = 178.000
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

    # test 2
    inward2 = {sa : { sae : 5 }, sb : { sbe : 1 }}
    costs = truncate(model.calculate_costs(inward2))
    expected = 97.800
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

def test_basic_instance_service():

    sae = InstanceEndpoint('ea')
    sa = InstanceService('a', [sae])
    sae_cf = {'capi' : 1, 'cio' : 0, "coth" : 5, "load_factor" : 0.2}
    sae.configure_endpoint(sae_cf)
    sa_cf = {'cost_per_instance' : 12}
    sa.configure_service(sa_cf)

    sbe = InstanceEndpoint('eb')
    sb = InstanceService('b', [sbe])
    sbe_cf = {'capi' : 0, 'cio' : 0, "load_factor" : 0.1, "coth" : 10}
    sbe.configure_endpoint(sbe_cf)
    sb_cf = {'cost_per_instance' : 5}
    sb.configure_service(sb_cf)

    sce = InstanceEndpoint('ec')
    sc = InstanceService('c', [sce])
    sce_cf = {'capi' : 1, 'cio' : 1, "load_factor" : 0.01, "coth" : 0}
    sce.configure_endpoint(sce_cf)
    sc_cf = {'cost_per_instance' : 2}
    sc.configure_service(sc_cf)

    sae_cg = [(sb, sbe, 1), (sc, sce, 4)]
    sae.set_callgraph(sae_cg)

    sbe_cg = [(sc, sce, 0.1)]
    sbe.set_callgraph(sbe_cg)

    model = CosthatModel([sa, sb, sc])

    # test 1
    inward1 = {sa : { sae : 10 }}
    costs = truncate(model.calculate_costs(inward1))
    expected = 138.000
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

    # test 2
    inward2 = {sa : { sae : 5 }, sb : { sbe : 1 }}
    costs = truncate(model.calculate_costs(inward2))
    expected = 80.200
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

def test_multiple_endpoints():

    sae1 = InstanceEndpoint("sae1")
    sae2 = InstanceEndpoint("sae2")
    sae1_cf = {'capi' : 1, 'cio' : 0, "load_factor" : 0.01, "coth" : 40}
    sae1.configure_endpoint(sae1_cf)
    sae2_cf = {'capi' : 2, 'cio' : 0, "load_factor" : 0.1, "coth" : 0}
    sae2.configure_endpoint(sae2_cf)
    sa = InstanceService("a", [sae1, sae2])
    sa_cf = {'cost_per_instance' : 1}
    sa.configure_service(sa_cf)

    sbe1 = InstanceEndpoint("sbe1")
    sbe2 = InstanceEndpoint("sbe2")
    sbe1_cf = {'capi' : 0, 'cio' : 0, "load_factor" : 0.1, "coth" : 0}
    sbe1.configure_endpoint(sbe1_cf)
    sbe2_cf = {'capi' : 5, 'cio' : 0, "load_factor" : 0.0, "coth" : 0}
    sbe2.configure_endpoint(sbe2_cf)
    sb = InstanceService("b", [sbe1, sbe2])
    sb_cf = {'cost_per_instance' : 15}
    sb.configure_service(sb_cf)

    sce1  = LambdaEndpoint("sce1")
    sce2  = LambdaEndpoint("sce2")
    sce3  = LambdaEndpoint("sce3")
    sce1_cf = {'capi' : 3, 'cio' : 0, 'ccmp' : 2, "coth" : 1}
    sce1.configure_endpoint(sce1_cf)
    sce2_cf = {'capi' : 1, 'cio' : 0, 'ccmp' : 0, "coth" : 0}
    sce2.configure_endpoint(sce2_cf)
    sce3_cf = {'capi' : 4, 'cio' : 0, 'ccmp' : 0, "coth" : 10}
    sce3.configure_endpoint(sce3_cf)
    sc = LambdaService("c", [sce1, sce2, sce3])

    sae1_cg = [(sa, sae2, 1), (sb, sbe1, 1)]
    sae1.set_callgraph(sae1_cg)
    sae2_cg = [(sb, sbe2, 1), (sc, sce2, 0.5), (sc, sce3, 0.5)]
    sae2.set_callgraph(sae2_cg)
    sbe1_cg = [(sc, sce1, 2)]
    sbe1.set_callgraph(sbe1_cg)

    model = CosthatModel([sa, sb, sc])

    # test 1
    inward1 = {sa : { sae1 : 10 }}
    costs = truncate(model.calculate_costs(inward1))
    expected = 273.000
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

    # test 2
    inward2 = {sa : { sae1 : 10, sae2 : 1 }, sb : { sbe2 : 50}, sc : { sce2 : 100 }}
    costs = truncate(model.calculate_costs(inward2))
    expected = 632.500
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

    # test no workload
    costs = truncate(model.calculate_costs({}))
    expected = 0
    print("Hoping for %d, and received %d" % (expected, costs))
    assert costs == expected

''' Start main test script! '''

test_basic_lambda_service()
test_basic_instance_service()
test_multiple_endpoints()