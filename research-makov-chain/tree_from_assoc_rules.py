# [CAL-02] การสร้างตารางการตัดสินใจจาก Association Rules

import configparser
import os
import uuid

import requests
from anytree import AnyNode, LevelOrderGroupIter
from anytree.exporter import JsonExporter

config = configparser.ConfigParser()
config.read("config.ini")

ASSOC_RULE_BASE_URL = config["Service"]["ASSOC_RULE_BASE_URL"]


def accumulate_node(node, factors, depth=0, hotel_name=None, rule_year=None, rule_month=None):
    if depth > 10:
        return None
    if len(factors) == 0:
        return None
    print(hotel_name)
    current_factor = factors[0]
    next_factors = factors[1:]
    # print(depth, current_factor, factors, next_factors)
    if node.is_root:
        node.weight = ""
        node.level = 0
        entities = __list_entities(current_factor)
        for entity in entities:
            new_node = AnyNode(id=uuid.uuid4().hex, name=entity, parent=node, level=depth, weight=None, score=None)
            accumulate_node(new_node, next_factors, depth + 1, hotel_name=hotel_name, rule_year=rule_year, rule_month=rule_month)
    else:
        # AnyNode(id=uuid.uuid4().hex, name="Leaf node", parent=node)
        rules = __fetch_assoc_rule(node.name, current_factor, hotel_name=hotel_name, rule_year=rule_year, rule_month=rule_month)
        rules = __find_unique(rules)
        for rule in rules:
            r = rule[0]
            new_node = AnyNode(id=uuid.uuid4().hex, name=r["consequents"], parent=node, level=depth, confidence=r["confidence"], lift=r["lift"])
            accumulate_node(new_node, next_factors, depth + 1, hotel_name=hotel_name, rule_year=rule_year, rule_month=rule_month)


def apply_freq_by_path(node, factors=[], hotel_name=None, DB=None, parent_frequency=None):
    it_factors = factors.copy()
    if not node.is_root:
        it_factors.append(node.name)
    node.frequency = DB.count_by_factors(hotel_name, it_factors)
    if parent_frequency is not None and parent_frequency != 0:
        node.percent = node.frequency / parent_frequency
    else:
        node.percent = 0
    if len(node.children) > 0:
        for childNode in node.children:
            apply_freq_by_path(childNode, factors=it_factors, hotel_name=hotel_name, DB=DB,
                               parent_frequency=node.frequency)


def apply_weight_by_node_level(node, weights = []):
    nodes_all_level = [[node for node in children] for children in LevelOrderGroupIter(node)]
    for idx, nodes_in_level in enumerate(nodes_all_level):
        if idx == 0:
            node.weight = None
            continue
        for node in nodes_in_level:
            node.weight = weights[idx - 1]
            if node.weight is not None:
                try:
                    node.score = node.weight * node.percent
                except:
                    # print("Node has no confidence value, ignored.")
                    pass
            else:
                node.score = None


def export_json(root_node):
    exporter = JsonExporter(indent=2, sort_keys=True)
    # UniqueDotExporter(root_node, options=["rankdir=LR;"]).to_picture("d-tree-" + str(uuid.uuid4().hex) + ".png")
    return exporter.export(root_node)


def list_all_factors():
    file = open('possible_values.csv')
    entities = [line.replace("\n", "") for line in file]
    file.close()
    return entities


def __list_entities(factor):
    file = open('possible_values.csv')
    entities = [line.replace("\n", "") for line in file if line.startswith(factor)]
    file.close()
    return entities


def __fetch_assoc_rule(lhs, rhs, hotel_name=None, rule_year=None, rule_month=None):
    payload = {'antecedents': lhs, 'consequents': rhs, 'hotel_name': hotel_name, 'rule_year': rule_year,
               'rule_month': rule_month}
    r = requests.get(ASSOC_RULE_BASE_URL + "/rules/dss", params=payload)
    return r.json()


def __find_unique(rules):
    values = set(map(lambda x: x["consequents"], rules))
    newlist = [[y for y in rules if y["consequents"] == x] for x in values]

    # TODO: ทำเป็น Dict แทนที่จะเป็น Array ดีไหม?
    # TODO: หาตัวเลือกจากกลุ่มออกมา

    return newlist
