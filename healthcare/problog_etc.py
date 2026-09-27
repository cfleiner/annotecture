import re
from collections import defaultdict
from problog.program import PrologString
from problog import get_evaluatable

def run_problog_program(problog_program: str) -> list[str]:
    output = []
    try:
        model = PrologString(problog_program)

        result = (
            get_evaluatable()
            .create_from(model)
            .evaluate()
        )

        output.append("Results")
        output.append("-------------------")

        for query, probability in sorted(
            result.items(),
            key=lambda x: str(x[0])
        ):
            output.append(f"{query} = {probability:.6f}")

    except Exception as e:

        output.append("Inference failed:")
        output.append(str(e))

    return output

def get_variable_domains_from_problog(filename):
    """
    Returns:
    {
        "ChestXRay":["normal", "oligaemic", "plethoric"],
        "Disease":  ["PFC", "TGA", "Fallot", "PAIVS", "TAPVD", "Lung"]
    }
    """

    domains = defaultdict(set)

    head_pattern = re.compile(
        r'^\s*[\d.]+::\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(([^()]+)\)'
    )

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("%"):
                continue

            match = head_pattern.match(line)
            if match:
                variable = match.group(1)
                state = match.group(2).strip()

                # ignore variables such as query(X)
                if state and state[0].isupper():
                    continue

                domains[variable].add(state)

    return {
        var: states
        for var, states in sorted(domains.items())
    }


if __name__ == "__main__":
    domains = get_variable_domains_from_problog("./healthcare/child.problog")
    from pprint import pprint
    pprint(domains)