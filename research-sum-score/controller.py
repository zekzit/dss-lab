import configparser

from anytree import AnyNode

from tree_from_assoc_rules import export_json, accumulate_node, apply_weight_by_node_level, \
    apply_freq_by_path
from weight_calculation import calculate_weight_rating, calculate_weight_ahp
from models import MongoDB

config = configparser.ConfigParser()
config.read("config.ini")
SENTIMENT_BASE_URL = config["Service"]["SENTIMENT_BASE_URL"]


def generate_decision_tree(mcda_type, factors, manual_weights, hotel_name, rule_year, rule_month):
    DB = MongoDB()
    root = AnyNode(id="root", name="DSS")
    if mcda_type == "rating":
        computed_weights = calculate_weight_rating(manual_weights)
    elif mcda_type == "pairwise":
        computed_weights = calculate_weight_ahp(manual_weights)

    sorted_weights = [weight for (weight, factor) in
                      sorted(zip(computed_weights, factors), key=lambda pair: pair[0], reverse=True)]
    sorted_factors = [factor for (weight, factor) in
                      sorted(zip(computed_weights, factors), key=lambda pair: pair[0], reverse=True)]

    accumulate_node(root, sorted_factors, hotel_name=hotel_name, rule_year=rule_year, rule_month=rule_month)
    apply_freq_by_path(root, hotel_name=hotel_name, DB=DB)
    apply_weight_by_node_level(root, sorted_weights)
    return root

