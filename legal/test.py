from pythen import RuleTreeEvaluator

# Define the rule set


# Define the rule set
contract_rules = [
    {
        "p": "contract_voidable",
        "op": "ANY",
        "conditions": ["party_is_minor"],
        "exceptions": ["contract_for_necessities"]
    },
    {
        "p": "party_is_minor",
        "op": "ALL",
        "conditions": ["party_age_below_18"],
        "exceptions": []
    }
]


# Case 1: A 16-year-old buys a luxury item
facts_case_1 = ["party_age_below_18"]

# Case 2: A 17-year-old buys food (a necessity)
facts_case_2 = ["party_age_below_18", "contract_for_necessities"]


evaluator = RuleTreeEvaluator(contract_rules)

# Evaluate Case 1
result_1 = evaluator.evaluate(facts_case_1, "contract_voidable")
print(f"Case 1 (Luxury Item): Is contract voidable? {result_1}")
# Output: Case 1 (Luxury Item): Is contract voidable? True

# Evaluate Case 2
result_2 = evaluator.evaluate(facts_case_2, "contract_voidable")
print(f"Case 2 (Necessities): Is contract voidable? {result_2}")
# Output: Case 2 (Necessities): Is contract voidable? False

# print(evaluator.get_all_predicates())
