from itertools import product
import re

import networkx as nx
from pgmpy.readwrite import BIFReader
from num2words import num2words

def normalize_identifier(value: str) -> str:
    """
    Convert BIF identifiers into valid Prolog atoms.

    Examples
    --------
    0-3_days   -> zero_to_three_days
    4-10_days  -> four_to_ten_days
    11-30_days -> eleven_to_thirty_days
    <5         -> lt_five
    5-12       -> five_to_twelve
    12+        -> twelve_plus
    >=7.5      -> ge_seven_point_five
    Asy/Patch  -> asy_patch
    """

    value = str(value)

    # relational operators
    value = value.replace(">=", "ge_")
    value = value.replace("<=", "le_")
    value = value.replace(">", "gt_")
    value = value.replace("<", "lt_")

    # required conversion
    value = value.replace("-", "_to_")

    value = value.replace("+", "_plus")
    value = value.replace("/", "_")
    value = value.replace(".", "_point_")

    def replace_number(match):
        number = match.group(0)

        try:
            if "." in number:
                integer, decimal = number.split(".")
                integer_word = num2words(int(integer))
                decimal_word = "_".join(
                    num2words(int(d))
                    for d in decimal
                )
                return f"{integer_word}_point_{decimal_word}"
            else:
                return num2words(int(number))
        except Exception:
            return number

    # replace numbers by English words
    value = re.sub(r"\d+(?:\.\d+)?", replace_number, value)

    # make Prolog-friendly
    value = value.replace(" ", "_")
    value = value.replace("-", "_")

    value = re.sub(r"[^A-Za-z0-9_]", "_", value)
    value = re.sub(r"_+", "_", value)

    return value.strip("_")


def bif_to_problog(bif_file: str) -> str:
    """
    Convert a BIF Bayesian network into a ProbLog program.

    Parameters
    ----------
    bif_file : str
        Path to the .bif file.

    Returns
    -------
    str
        ProbLog program.
    """
    reader = BIFReader(bif_file)
    model = reader.get_model()


    problog_lines = []
    ordered_nodes = list(nx.topological_sort(model))
    for node in ordered_nodes:
        cpd = model.get_cpds(node)
        child = normalize_identifier(cpd.variable)
        child_states = [
                    normalize_identifier(s)
                    for s in cpd.state_names[cpd.variable]
        ]
        parents = cpd.variables[1:] 

        parent_state_lists = [cpd.state_names[p] for p in parents]
        parent_assignments = list(product(*parent_state_lists))

        # --------------------------------------------------
        # CPD header
        # --------------------------------------------------

        problog_lines.append("")
        problog_lines.append("% --------------------------------------------------")
        problog_lines.append(
            f"% probability ( {child}"
            + (f" | {', '.join(parents)}" if parents else "")
            + " )"
        )
        problog_lines.append("% --------------------------------------------------")
        problog_lines.append("")

        # --------------------------------------------------
        # Rules grouped by outcome value
        # --------------------------------------------------

        for row_idx, child_state in enumerate(child_states):
            for col_idx, assignment in enumerate(parent_assignments):

                body = ", ".join(
                    f"{normalize_identifier(parent)}({ normalize_identifier(state)})"
                    for parent, state in zip(parents, assignment)
                )

                prob = cpd.values[
                    (row_idx,) + tuple(
                        parent_state_lists[i].index(assignment[i])
                        for i in range(len(parents))
                    )
                ]

                rule = (
                    f"{prob}::{child}({child_state})"
                    f"{f' :- {body}' if body else ''}."
                )

                problog_lines.append(rule.lower())

            # empty line between outcome groups
            problog_lines.append("")

    return '\n'.join(problog_lines)
   

if __name__ == "__main__":
    prob_log_program = bif_to_problog("./healthcare/child.bif")

    with open("./healthcare/child2.problog", "w") as f:
        f.write(prob_log_program)