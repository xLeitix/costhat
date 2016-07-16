from costhat import *

# step 1 - load the predefined model reflecting our small case study
casestudy = CosthatModel.xmlunpickle('ucc_casestudy_model.xml')

# step 2 - define some inwards-facing workloads
# assume that our users invoke frontend/order and frontend/landing, and
# we get some additional external pressure to order_history/get and */save
frontend, landing = casestudy.find_by_name('frontend', 'landing')
_, order = casestudy.find_by_name('frontend', 'order')
orderhistory, get = casestudy.find_by_name('order_history', 'get')
_, save = casestudy.find_by_name('order_history', 'save')
workload = {
    frontend : { landing : 150000, order : 25000 },
    orderhistory : { get : 100000, save : 10000 }
}

# step 3 - calculate original costs
costs = casestudy.calculate_costs(workload)
print("Calculated costs per hour: %.2f USD" % costs)

# step 4 - do some what-if analysis (e.g., change some parameters)
print "----------------------------------"
print "Case 1 - Twice as many orders"
workload[frontend][order] = 50000
costs = casestudy.calculate_costs(workload)
workload[frontend][order] = 25000
print "----------------------------------"
print "Case 2 - Somebody else starts using the recommendation engine"
recommend, generate = casestudy.find_by_name('recommend', 'generate')
workload[recommend] = { generate : 50000 }
costs = casestudy.calculate_costs(workload)
workload = {
    frontend : { landing : 150000, order : 25000 },
    orderhistory : { get : 100000, save : 10000 }
}
print "----------------------------------"
print "Case 3 - Migrate the order history service to an m4.2xlarge instance type (smaller)"
orderhistory.configure_service({ 'cost_per_instance' : 0.479 })
get.configure_endpoint({ 'load_factor' : 0.0000008 })
save.configure_endpoint({ 'load_factor' : 0.00001 })
costs = casestudy.calculate_costs(workload)
casestudy = CosthatModel.xmlunpickle('ucc_casestudy_model.xml')

# step 5 - evaluate a code change - add a dependency from recommend/generate to customers/get
print "----------------------------------"
print "Case 4 - Code change"
frontend, landing = casestudy.find_by_name('frontend', 'landing')
_, order = casestudy.find_by_name('frontend', 'order')
orderhistory, get = casestudy.find_by_name('order_history', 'get')
_, save = casestudy.find_by_name('order_history', 'save')
_, generate = casestudy.find_by_name('recommend', 'generate')
workload = {
    frontend : { landing : 150000, order : 25000 },
    orderhistory : { get : 100000, save : 10000 }
}
customers, get = casestudy.find_by_name('customers', 'get')
generate.callgraph.append((customers, get, 1))
costs = casestudy.calculate_costs(workload)
