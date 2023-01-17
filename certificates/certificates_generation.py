import json
import sys 
import os
sys.path.append(os.path.abspath(r"C:\Users\phopp\OneDrive\Desktop\ORCO\Advanced-OR-methods\git-project\AMOP-Batch-scheduling\some-solutions"))
import knapsackwithwidthandconflicts
import knapsackwithwidth
import batchschedulingmakespan
import batchschedulingwithconflictsmakespan
import treesearchsolverpy
import columngenerationsolverpy



def generate_certificates_knapsackwithwidth(start=0, end=100):
    for i in range(start, end + 1):
        print("Generating certificate for instance " + str(i) + "...")
        instance = knapsackwithwidth.Instance("AMOP-Batch-scheduling/data/knapsackwithwidthandconflicts/instance_" + str(i) + ".json")
        solution = knapsackwithwidth.dynamic_programming(instance)
        data = {"items": solution}
        certificate_name = "AMOP-Batch-scheduling/certificates/knapsackwithwidthandconflicts/certificate_" + str(i) + ".json"
        with open(certificate_name, 'w') as json_file:
            json.dump(data, json_file)

def check_certificates_knapsackwithwidth(start=0, end=100):
    fails = []
    for i in range(start, end + 1):
        instance = knapsackwithwidth.Instance("AMOP-Batch-scheduling/data/knapsackwithwidthandconflicts/instance_" + str(i) + ".json")
        certificate_name = "AMOP-Batch-scheduling/certificates/knapsackwithwidth/certificate_" + str(i) + ".json"
        (val, _) = instance.check(certificate_name)
        if not val:
            fails.append(i)
    print(fails)



def generate_certificates_knapsackwithwidthandconflicts(start=0, end=100, limit=30):
    for i in range(start, end + 1):
        print("Generating certificate for instance " + str(i) + "...")
        instance = knapsackwithwidthandconflicts.Instance("AMOP-Batch-scheduling/data/knapsackwithwidthandconflicts/instance_" + str(i) + ".json")
        branching_scheme = knapsackwithwidthandconflicts.BranchingScheme(instance)
        output = treesearchsolverpy.iterative_beam_search(branching_scheme, time_limit=limit, verbose=False)
        solution = branching_scheme.to_solution(output["solution_pool"].best)
        data = {"items": solution}
        certificate_name = "AMOP-Batch-scheduling/certificates/knapsackwithwidthandconflicts/certificate_" + str(i) + ".json"
        with open(certificate_name, 'w') as json_file:
            json.dump(data, json_file)

def check_certificates_knapsackwithwidthandconflicts(start=0, end=100):
    fails = []
    for i in range(start, end + 1):
        instance = knapsackwithwidthandconflicts.Instance("AMOP-Batch-scheduling/data/knapsackwithwidthandconflicts/instance_" + str(i) + ".json")
        certificate_name = "AMOP-Batch-scheduling/certificates/knapsackwithwidthandconflicts/certificate_" + str(i) + ".json"
        (val, _) = instance.check(certificate_name)
        if not val:
            fails.append(i)
    print(fails)

def generate_certificates_batchschedulingmakespan(start=0, end=100, limit=60):
    for i in range(start, end + 1):
        print("Generating certificate for instance " + str(i) + "...")
        instance = batchschedulingmakespan.Instance("AMOP-Batch-scheduling/data/batchschedulingwithconflictsmakepsan/instance_" + str(i) + ".json")
        parameters = batchschedulingmakespan.get_parameters(instance)
        output = columngenerationsolverpy.limited_discrepancy_search(parameters, verbose=False, time_limit=limit)
        solution = batchschedulingmakespan.to_solution(parameters.columns, output["solution"])
        data = {"jobs": solution}
        certificate_name = "AMOP-Batch-scheduling/certificates/batchschedulingmakespan/certificate_" + str(i) + ".json"
        with open(certificate_name, 'w') as json_file:
            json.dump(data, json_file)

def check_certificates_batchschedulingmakespan(start=0, end=100):
    fails = []
    for i in range(start, end + 1):
        instance = batchschedulingmakespan.Instance("AMOP-Batch-scheduling/data/batchschedulingwithconflictsmakepsan/instance_" + str(i) + ".json")
        certificate_name = "AMOP-Batch-scheduling/certificates/batchschedulingmakespan/certificate_" + str(i) + ".json"
        (val, _) = instance.check(certificate_name)
        if not val:
            fails.append(i)
    print(fails)


def generate_certificates_batchschedulingwithconflictsmakespan(start=0, end=100, limit=60):
    for i in range(start, end + 1):
        print("Generating certificate for instance " + str(i) + "...")
        instance = batchschedulingwithconflictsmakespan.Instance("AMOP-Batch-scheduling/data/batchschedulingwithconflictsmakepsan/instance_" + str(i) + ".json")
        parameters = batchschedulingwithconflictsmakespan.get_parameters(instance)
        output = columngenerationsolverpy.limited_discrepancy_search(parameters, time_limit=limit, verbose=False)
        solution = batchschedulingwithconflictsmakespan.to_solution(parameters.columns, output["solution"])
        data = {"jobs": solution}
        certificate_name = "AMOP-Batch-scheduling/certificates/batchschedulingwithconflictsmakespan/certificate_" + str(i) + ".json"
        with open(certificate_name, 'w') as json_file:
            json.dump(data, json_file)

def check_certificates_batchschedulingwithconflictsmakespan(start=0, end=100):
    fails = []
    for i in range(start, end + 1):
        instance = batchschedulingwithconflictsmakespan.Instance("AMOP-Batch-scheduling/data/batchschedulingwithconflictsmakepsan/instance_" + str(i) + ".json")
        certificate_name = "AMOP-Batch-scheduling/certificates/batchschedulingwithconflictsmakespan/certificate_" + str(i) + ".json"
        (val, _) = instance.check(certificate_name)
        if not val:
            fails.append(i)
    print(fails)


if __name__ == '__main__':
    generate_certificates_batchschedulingwithconflictsmakespan(start=100, limit=300)
    check_certificates_batchschedulingwithconflictsmakespan(start=100)
