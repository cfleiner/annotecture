

def collect_predicates(rule_tree):
    result = set()

    for rule in rule_tree:
        result.add(rule["p"])
        result.update(rule.get("conditions", []))
        result.update(rule.get("exceptions", []))

    return sorted(list(result))


def label_for(pred):
    return pred.replace("_", " ").capitalize()