import treesearchsolverpy
import json
from functools import total_ordering


class Item:
    id = -1
    weight = 0
    width = 0
    profit = 0
    conflicting_items = None


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
                for item_id_1, item_id_2 in data["conflicts"]:
                    self.add_conflict(item_id_1, item_id_2)

    def add_item(self, weight, width, profit):
        item = Item()
        item.id = len(self.items)
        item.weight = weight
        item.width = width
        item.profit = profit
        item.conflicting_items = []
        self.items.append(item)

    def add_conflict(self, item_id_1, item_id_2):
        self.items[item_id_1].conflicting_items.append(item_id_2)
        self.items[item_id_2].conflicting_items.append(item_id_1)

    def write(self, filepath):
        data = {"capacity": self.capacity,
                "item_weights": [item.weight for item in self.items],
                "item_widths": [item.width for item in self.items],
                "item_profits": [item.profit for item in self.items],
                "conflicts": [
                    (item_1.id, item_2.id)
                    for item_1 in self.items
                    for item_2 in self.items
                    if item_1.id in item_2.conflicting_items
                    and item_1.id < item_2.id]}
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
            # Compute number_of_conflicts.
            number_of_conflicts = sum(
                    item_id_1 in self.items[item_id_2].conflicting_items
                    and item_id_1 < item_id_2
                    for item_id_1 in data["items"]
                    for item_id_2 in data["items"])
            # Compute number_of_duplicates.
            number_of_duplicates = len(data["items"]) - len(set(data["items"]))

            is_feasible = (
                    (number_of_duplicates == 0)
                    and (number_of_conflicts == 0)
                    and (weight <= self.capacity))
            objective_value = profit - width
            print(f"Profit: {profit}")
            print(f"Weight: {weight} / {self.capacity}")
            print(f"Width: {width}")
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"Number of conflicts: {number_of_conflicts}")
            print(f"Feasible: {is_feasible}")
            print(f"Objective value: {objective_value}")
            return (is_feasible, objective_value)


class BranchingScheme:

    @total_ordering
    class Node:

        id = None
        father = None
        taken = None
        conflicts = None
        maxWidth = None
        next_child = 0
        profits = None
        weight = None
        guide = None
        value = None
        potential_increase = None

        def __lt__(self, other):
            if self.guide != other.guide:
                return self.guide < other.guide
            return self.id < other.id

    def __init__(self, instance):
        self.instance = instance
        self.id = 0

    def root(self):
        node = self.Node()
        node.father = None
        node.taken = 0
        node.conflicts = 0
        node.profits = 0
        node.weight = 0
        node.maxWidth = 0
        node.guide = 0
        node.value = 0
        node.potential_increase = sum(item.profit for item in self.instance.items)
        node.id = self.id
        self.id += 1
        return node

    def next_child(self, father):
        i = father.next_child
        if i == len(self.instance.items):
            return None
        
        father.next_child += 1
        item = self.instance.items[i]
        if (father.conflicts >> i & 1) or (father.taken >> i & 1):
            # The item would be conflicting in the child
            return None
        if father.weight + item.weight > self.instance.capacity:
            # The item is too heavy, we add a conflict
            father.conflicts += (1 << i)
            father.potential_increase -= item.profit
            return None

        # Child when item i is taken
        child = self.Node()
        child.father = father
        child.taken = father.taken + (1 << i)
        child.conflicts = father.conflicts
        for j in item.conflicting_items:
            if not(father.conflicts >> j & 1):
                child.conflicts += (1 << j)
        child.profits = father.profits + item.profit
        child.potential_increase = father.potential_increase - item.profit
        child.weight = father.weight + item.weight
        child.maxWidth = max(father.maxWidth, item.width)
        child.value = child.profits - child.maxWidth
        child.guide = child.weight / max(child.value, 1)
        child.id = self.id
        self.id += 1

        return child




    def infertile(self, node):
        return node.next_child == len(self.instance.items)

    def leaf(self, node):
        return node.next_child == len(self.instance.items)

    def bound(self, node_1, node_2):
        return node_1.value + node_1.potential_increase <= node_2.value

    # Solution pool.

    def better(self, node_1, node_2):
        return node_1.value > node_2.value

    def equals(self, node_1, node_2):
        return node_1.value == node_2.value and node_1.weight == node_2.weight and node_1.taken + node_1.conflicts == node_2.taken + node_2.conflicts

    # Dominances.

    def comparable(self, node):
        return True

    class Bucket:

        def __init__(self, node):
            self.node = node

        def __hash__(self):
            return hash((self.node.conflicts, self.node.taken))

        def __eq__(self, other):
            return self.node.taken + self.node.conflicts == other.node.taken + other.node.conflicts

    def dominates(self, node_1, node_2):
        return node_1.value >= node_2.value and node_1.weight <= node_2.weight

    # Outputs.

    def display(self, node):
        value = max(0, node.value)
        return str(value)

    def to_solution(self, node):
        objects = []
        if node.value < 0:
            return objects
        for i in range(len(self.instance.items)):
            if node.taken >> i & 1:
                objects.append(i)
        return objects


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="iterative_beam_search",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            default="AMOP-Batch-scheduling/data/knapsackwithwidthandconflicts/instance_50.json",
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default="AMOP-Batch-scheduling/certificate.json",
            help='')

    args = parser.parse_args()

    if args.algorithm == "generator":
        import random
        random.seed(0)
        for number_of_items in range(101):
            instance = Instance()
            total_weight = 0
            for item_id in range(number_of_items):
                profit = random.randint(100, 200)
                width = random.randint(100, 200)
                weight = random.randint(100, 200)
                total_weight += weight
                instance.add_item(weight, width, profit)
            instance.capacity = random.randint(
                    total_weight * 1 // 4,
                    total_weight * 2 // 4)
            conflicts = set()
            n = number_of_items * (number_of_items - 1) // 2
            d = random.randint(1, 25)  # density between 1% and 25%
            number_of_conflicts = n * d // 100
            for _ in range(number_of_conflicts):
                item_id_1 = random.randint(0, number_of_items - 1)
                item_id_2 = random.randint(0, number_of_items - 2)
                if item_id_2 >= item_id_1:
                    item_id_2 += 1
                conflicts.add((
                    min(item_id_1, item_id_2),
                    max(item_id_1, item_id_2)))
            for item_id_1, item_id_2 in conflicts:
                instance.add_conflict(item_id_1, item_id_2)
            instance.write(
                    args.instance + "_" + str(number_of_items) + ".json")

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)

    else:
        instance = Instance(args.instance)
        branching_scheme = BranchingScheme(instance)
        if args.algorithm == "greedy":
            output = treesearchsolverpy.greedy(
                    branching_scheme)
        elif args.algorithm == "best_first_search":
            output = treesearchsolverpy.best_first_search(
                    branching_scheme,
                    time_limit=30)
        elif args.algorithm == "iterative_beam_search":
            output = treesearchsolverpy.iterative_beam_search(
                    branching_scheme,
                    time_limit=120)
        solution = branching_scheme.to_solution(output["solution_pool"].best)
        if args.certificate is not None:
            data = {"items": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)
