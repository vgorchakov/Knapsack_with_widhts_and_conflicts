import json
import numpy as np


class Item:
    id = -1
    weight = 0
    width = 0
    profit = 0


class Instance:

    def __init__(self, filepath=None):
        self.items = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                self.capacity = data["capacity"]
                items = zip(
                        data["item_weights"],
                        data["item_widths"],
                        data["item_profits"])
                for (weight, width, profit) in items:
                    self.add_item(weight, width, profit)

    def add_item(self, weight, width, profit):
        item = Item()
        item.id = len(self.items)
        item.weight = weight
        item.width = width
        item.profit = profit
        self.items.append(item)

    def write(self, filepath):
        data = {"capacity": self.capacity,
                "item_weights": [item.weight for item in self.items],
                "item_widths": [item.width for item in self.items],
                "item_profits": [item.profit for item in self.items]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            data = json.load(json_file)
            # Compute profit.
            profit = sum(self.items[item_id].profit
                         for item_id in data["items"])
            # Copute weight.
            weight = sum(self.items[item_id].weight
                         for item_id in data["items"])
            # Compute width.
            width = max((self.items[item_id].width
                         for item_id in data["items"]),
                        default=0)
            # Compute number_of_duplicates.
            number_of_duplicates = len(data["items"]) - len(set(data["items"]))

            is_feasible = (
                    (number_of_duplicates == 0)
                    and (weight <= self.capacity))
            objective_value = profit - width
            print(f"Profit: {profit}")
            print(f"Weight: {weight} / {self.capacity}")
            print(f"Width: {width}")
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"Feasible: {is_feasible}")
            print(f"Objective value: {objective_value}")
            return (is_feasible, objective_value)



def dynamic_programming(instance):
    items = instance.items
    n = len(items)
    capacity = instance.capacity
    
    # We create a list of the items indexes sorted by the increasing width
    sorted_indexes = [i for i in range(n)]
    def sorter(i):
        return items[i].width
    sorted_indexes.sort(key=sorter)

    # Then when do a classical Knapsack with the new idexes
    t = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    for i, index in enumerate(sorted_indexes):
        item = items[index]
        for c in range(min(item.weight, capacity + 1)): # (Some cheeky objects are of size > capacity)
            t[i + 1][c] = t[i][c]

        for c in range(item.weight, capacity + 1):
            t[i + 1][c] = max(t[i][c - item.weight] + item.profit, t[i][c])

    # Solution retrieval
    solution = []

    sorted_widths = [items[i].width for i in range(n)]
    sorted_widths.insert(0, 0)
    i = np.argmax([t[i][capacity] - sorted_widths[i] for i in range(n + 1)])
    c = capacity

    while i > 0:
        if t[i][c] != t[i - 1][c]:
            index = sorted_indexes[i - 1]
            solution.append(index)
            c -= items[index].weight
        i -= 1

    return solution
    



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="dynamic_programming",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            default="advanced-OR-project/data/knapsackwithwidthandconflicts/instance_100.json",
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default="AMOP-Batch-scheduling/certificate.json",
            help='')

    args = parser.parse_args()

    if args.algorithm == "dynamic_programming":
        instance = Instance(args.instance)
        solution = dynamic_programming(instance)
        if args.certificate is not None:
            data = {"items": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)
