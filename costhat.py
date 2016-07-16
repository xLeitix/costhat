import json
import math
from lxml import etree
from abc import ABCMeta, abstractmethod

class CosthatModel:

    def __init__(self):
        pass

    def __init__(self, services):
        self.services = services

    def xmlpickle(self, file):
        with open(file, 'w') as _file:
            root = etree.Element('costhat')
            for s in self.services:
                root.append( s.xmlpickle() )
            _file.write(etree.tostring(root, pretty_print=True))

    @staticmethod
    def xmlunpickle(file):
        with open(file, 'r') as _file:
            costhat = etree.parse(_file).getroot()
        services = []
        # deserialize services and endpoints (including config)
        for s in costhat:
            if type(s) is etree._Comment:
                continue
            eps = []
            cost_per_instance = 0
            for e in s:
                if type(e) is etree._Comment:
                    continue
                if e.tag == 'config':
                    cost_per_instance = float(e.get('cost_per_instance'))
                    continue
                if s.get('backed') == 'instance':
                    endpoint = InstanceEndpoint.xmlunpickle(e)
                else:
                    endpoint = LambdaEndpoint.xmlunpickle(e)
                eps.append(endpoint)
            if s.get('backed') == 'instance':
                service = InstanceService(s.get('name'), eps)
                s_config = cost_per_instance
                service.configure_service({ 'cost_per_instance':s_config })
            else:
                service = LambdaService(s.get('name'), eps)
            services.append(service)
        model = CosthatModel(services)
        # deserialize callgraph in second go through file
        for s in costhat:
            if type(s) is etree._Comment:
                continue
            for e in s:
                if type(e) is etree._Comment:
                    continue
                for child in e:
                    if type(child) is etree._Comment:
                        continue
                    if child.tag == 'callgraph':
                        outcalls = []
                        for o in child:
                            if type(o) is etree._Comment:
                                continue
                            servicename = o.get('service')
                            epname = o.get('endpoint')
                            prop = float(o.get('probability'))
                            _service, _ep = model.find_by_name(servicename, epname)
                            outcalls.append( (_service, _ep, prop) )
                        _, _ep = model.find_by_name(s.get('name'), e.get('name'))
                        _ep.set_callgraph(outcalls)
        return model

    def calculate_costs(self, inward_workload):
        print "#######"
        total_wl = self._calculate_total_workload(inward_workload)
        print "Total workload:"
        self._print_workload(total_wl)
        print "#######"
        sum = 0.0
        for s in self.services:
            sum += s.calculate_service_costs(total_wl[s])
        print "Sum of all costs: %.2f" % sum
        return sum

    def find_by_name(self, service, endpoint):
        for s in self.services:
            if s.name == service:
                for e in s.eps:
                    if e.name == endpoint:
                        return (s, e)
        return None

    def _print_workload(self, wl):
        print 'Requests:'
        for s in wl:
            for e in s.eps:
                print "%s/%s: %d" % (s.name, e.name, wl[s][e])

    def _calculate_total_workload(self, inward_workload):
        total_wl = self._empty_wl()
        for s in self.services:
            for e in s.eps:
                if s in inward_workload and e in inward_workload[s]:
                    self._triggered(total_wl, s, e, inward_workload[s][e])
        return total_wl

    def _triggered(self, workload, service, ep, n):
        workload[service][ep] += n
        if not hasattr(ep, 'callgraph'):
            return
        for s, e, p in ep.callgraph:
            self._triggered(workload, s, e, n * p)

    def _empty_wl(self):
        wl = {}
        for s in self.services:
            wl[s] = {}
            for e in s.eps:
                wl[s][e] = 0.0
        return wl

class Service:

    __metaclass__ = ABCMeta

    def __str__(self):
        return self.name

    @abstractmethod
    def calculate_service_costs(self, workload):
        pass

    @abstractmethod
    def configure_service(self, configuration):
        pass

    @abstractmethod
    def xmlpickle(self):
        pass

class LambdaService(Service):

    def __init__(self, name, eps):
        self.name = name
        # lamda services should only have lambda eps
        for ep in eps:
            assert type(ep) is LambdaEndpoint
        self.eps = eps

    def calculate_service_costs(self, workload):
        total_costs = 0
        for ep in self.eps:
            if workload[ep] > 0:
                total_costs += ep.calculate_endpoint_costs(workload[ep])
        print "Costs of service %s: %.2f" % (self.name, total_costs)
        return total_costs

    def configure_service(self, configuration):
        # nothing to configure here
        pass

    def xmlpickle(self):
        service = etree.Element('service', name=self.name, backed='lambda')
        for ep in self.eps:
            service.append( ep.xmlpickle() )
        return service

class InstanceService(Service):

    def __init__(self, name, eps):
        self.name = name
        # instance services should only have instance eps
        for ep in eps:
            assert type(ep) is InstanceEndpoint
        self.eps = eps

    def calculate_service_costs(self, workload):
        non_compute_costs = 0
        for ep in self.eps:
            if workload[ep] > 0:
                non_compute_costs += ep.calculate_endpoint_costs(workload[ep])
        compute_costs = self._calculate_compute_costs(workload)
        total_costs = compute_costs + non_compute_costs
        print "Costs of service %s: %.2f (%.2f compute, %.2f other)" % (self.name, total_costs, compute_costs, non_compute_costs)
        return total_costs

    def configure_service(self, configuration):
        self.cost_per_instance = configuration['cost_per_instance']

    def xmlpickle(self):
        service = etree.Element('service', name=self.name, backed='instance')
        config = etree.Element('config', cost_per_instance=str(self.cost_per_instance))
        service.append(config)
        for ep in self.eps:
            service.append( ep.xmlpickle() )
        return service

    def _calculate_compute_costs(self, workload):
        if not hasattr(self, 'cost_per_instance'):
            raise NotInitializedError()
        instance_count = 0.0
        for ep in self.eps:
            instance_count += ep.load_factor * workload[ep]
        instance_count = math.ceil(instance_count)
        return instance_count * self.cost_per_instance

class Endpoint:

    __metaclass__ = ABCMeta

    def __str__(self):
        return self.name

    @abstractmethod
    def calculate_endpoint_costs(self):
        pass

    @abstractmethod
    def configure_endpoint(self, configuration):
        pass

    @abstractmethod
    def xmlpickle(self):
        pass

    def set_callgraph(self, cg):
        self.callgraph = cg

class LambdaEndpoint(Endpoint):

    def __init__(self, name):
        self.name = name

    def calculate_endpoint_costs(self, request_count):
        if not hasattr(self, 'capi'):
            raise NotInitializedError()
        costs =  request_count * (self.capi + self.ccmp + self.cio) + self.coth
        # print "Costs of lambda endpoint %s: %.2f " % (self.name, costs)
        return costs

    def configure_endpoint(self, configuration):
        if 'capi' in configuration:
            self.capi = configuration['capi']
        if 'ccmp' in configuration:
            self.ccmp = configuration['ccmp']
        if 'cio' in configuration:
            self.cio = configuration['cio']
        if 'coth' in configuration:
            self.coth = configuration['coth']

    def xmlpickle(self):
        endpoint = etree.Element('endpoint', name=self.name)
        config = etree.Element('config', capi=str(self.capi), ccmp=str(self.ccmp), cio=str(self.cio), coth=str(self.coth))
        endpoint.append(config)
        if hasattr(self, "callgraph"):
            cg = etree.Element('callgraph')
            for s, e, p in self.callgraph:
                call = etree.Element('outcall', service=s.name, endpoint=e.name, probability=str(p))
                cg.append(call)
            endpoint.append(cg)
        return endpoint

    @staticmethod
    def xmlunpickle(element):
        ep = LambdaEndpoint(element.get('name'))
        for child in element:
            if type(child) is etree._Comment:
                continue
            if child.tag == 'config':
                config = {
                    'capi' : float(child.get('capi')),
                    'ccmp': float(child.get('ccmp')),
                    'cio': float(child.get('cio')),
                    'coth': float(child.get('coth'))
                }
        ep.configure_endpoint(config)
        return ep

class InstanceEndpoint(Endpoint):

    def __init__(self, name):
        self.name = name

    def calculate_endpoint_costs(self, request_count):
        if not hasattr(self, 'capi'):
            raise NotInitializedError()
        costs = request_count * (self.capi + self.cio) + self.coth
        # print "Non-compute costs of instance endpoint %s: %.2f " % (self.name, costs)
        return costs

    def configure_endpoint(self, configuration):
        if 'capi' in configuration:
            self.capi = configuration['capi']
        if 'cio' in configuration:
            self.cio = configuration['cio']
        if 'coth' in configuration:
            self.coth = configuration['coth']
        if 'load_factor' in configuration:
            self.load_factor = configuration['load_factor']

    def xmlpickle(self):
        endpoint = etree.Element('endpoint', name=self.name)
        config = etree.Element('config', capi=str(self.capi), cio=str(self.cio), coth=str(self.coth), load_factor=str(self.load_factor))
        endpoint.append(config)
        if hasattr(self, "callgraph"):
            cg = etree.Element('callgraph')
            for s, e, p in self.callgraph:
                call = etree.Element('outcall', service=s.name, endpoint=e.name, probability=str(p))
                cg.append(call)
            endpoint.append(cg)
        return endpoint

    @staticmethod
    def xmlunpickle(element):
        ep = InstanceEndpoint(element.get('name'))
        for child in element:
            if type(child) is etree._Comment:
                continue
            if child.tag == 'config':
                config = {
                    'capi' : float(child.get('capi')),
                    'load_factor': float(child.get('load_factor')),
                    'cio': float(child.get('cio')),
                    'coth': float(child.get('coth'))
                }
        ep.configure_endpoint(config)
        return ep

class NotInitializedError(Exception):
    pass