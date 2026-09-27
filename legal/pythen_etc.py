from rdflib import Namespace
import json
from ast import literal_eval

def compose_scenario(g, scenario_num):
    AS = Namespace("https://www.w3.org/ns/activitystreams#")
    OA = Namespace("http://www.w3.org/ns/oa#")
    EX = Namespace("http://www.example.com/")
    
    kb = EX[f"kb_scenario_{str(scenario_num)}"]

    rule_tree = []
    facts = []
    result = False
    
    for o in g.objects(kb, AS.items):
        body_value = g.value(o, OA.bodyValue)
    
        if str(g.value(o, EX["pythen_concept"])) == 'rule':
           rule_tree.append(literal_eval(str(f'{body_value}')))
        elif str(g.value(o, EX["pythen_concept"])) == 'fact':
            facts.append(str(body_value))
        else:
            result = body_value == "True"
    return {
        "rule_tree": rule_tree,
        "facts": facts,
        "result": result
    }


def collect_predicates(rule_tree):
    result = set()

    for rule in rule_tree:
        result.add(rule["p"])
        result.update(rule.get("conditions", []))
        result.update(rule.get("exceptions", []))

    return sorted(list(result))


def label_for(pred):
    return pred.replace("_", " ").capitalize()