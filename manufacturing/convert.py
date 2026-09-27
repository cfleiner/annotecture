import re
from collections import defaultdict

def resolve_consensus(rules):

    grouped = defaultdict(lambda: {
        "positive_effect": [],
        "negative_effect": []
    })

    for rule in rules:
        parsed = parse_effect_rule(rule["content"])

        if parsed is None:
            continue

        effect_type, signature = parsed

        # Store the case that supports the rule
        grouped[signature][effect_type].append(rule["case"])

    
    kb_rules = {"positive_effect": set(), "negative_effect": set()}
    errors = []

    for signature, data in grouped.items():

        pos_cases = data["positive_effect"]
        neg_cases = data["negative_effect"]

        pos = len(pos_cases)
        neg = len(neg_cases)

        if pos and neg:

            if pos > neg:
                chosen = "positive_effect"

            elif neg > pos:
                chosen = "negative_effect"

            else:
                errors.append(
                    f"Unresolvable contradiction for "
                    f"{signature[0]}, {signature[1]}: "
                    f"positive({', '.join(pos_cases)}) "
                    f"negative({', '.join(neg_cases)})"
                )
                continue
            kb_rules[chosen].add(f"({signature[0]}, {signature[1]})")

        elif pos:
            kb_rules["positive_effect"].add(f"({signature[0]}, {signature[1]})")

        elif neg:
            kb_rules["negative_effect"].add(f"({signature[0]}, {signature[1]})")


    return kb_rules, errors


def resolve_order(rules, case_order):
    # case -> priority index
    priority = {
        case: idx
        for idx, case in enumerate(case_order)
    }

    grouped = defaultdict(list)

    # Group rules by signature
    for rule in rules:
        parsed = parse_effect_rule(rule["content"])

        if parsed is None:
            continue

        effect_type, signature = parsed

        grouped[signature].append({
            "case": rule["case"],
            "effect_type": effect_type,
            "content": rule["content"]
        })

    # kb_rules = []
    kb_rules = {"positive_effect": set(), "negative_effect": set()}
    errors = []

    for signature, signature_rules in grouped.items():

        # Sort according to case priority
        signature_rules = sorted(
            signature_rules,
            key=lambda r: priority.get(r["case"], float("inf"))
        )

        # Check for contradictions within the same case
        by_case = defaultdict(set)

        for rule in signature_rules:
            by_case[rule["case"]].add(rule["effect_type"])

        contradictory_cases = [
            case
            for case, effects in by_case.items()
            if len(effects) > 1
        ]

        if contradictory_cases:
            errors.append(
                f"Unresolvable contradiction for "
                f"{signature[0]}, {signature[1]} "
                f"in case(s): {', '.join(map(str, contradictory_cases))}"
            )
            continue

        if not signature_rules:
            continue

        # First rule in the ordered cases wins
        winning_rule = signature_rules[0]

        winning_effect = winning_rule["effect_type"]
        winning_case = winning_rule["case"]

        # Collect overridden opposite effects
        opposite_effect = (
            "negative_effect"
            if winning_effect == "positive_effect"
            else "positive_effect"
        )

        overridden = [
            rule["case"]
            for rule in signature_rules[1:]
            if rule["effect_type"] == opposite_effect
        ]

        kb_rules[winning_effect].add(f"({signature[0]}, {signature[1]})")

        if overridden:
            errors.append(
                f"{signature[0]}, {signature[1]}: "
                f"{winning_effect} from {winning_case} overrides "
                f"conflicting rule(s) from {', '.join(map(str, overridden))}"
            )

    return kb_rules, errors

def parse_effect_rule(content):
    """
    positive_effect := {(Kp, Settling_Time)}
    ->
    (
        "positive_effect",
        ("Kp", "Settling_Time")
    )
    """

    m = re.match(
        r"(positive_effect|negative_effect)\s*:=\s*\{\(([^,]+),\s*([^)]+)\)\}",
        content.strip()
    )

    if not m:
        return None

    effect_type = m.group(1)
    parameter = m.group(2).strip()
    outcome = m.group(3).strip()
    return effect_type, (parameter, outcome)
