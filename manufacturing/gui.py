import json
from IPython.display import Javascript, display
import ipywidgets as widgets
from rdflib import Graph
from rdf_etc import run_query_file
from convert import resolve_consensus, resolve_order

def create_ui(case_ids):

    available = widgets.SelectMultiple(
        options=case_ids,
        description="Cases:"
    )

    selected = widgets.Select(
        options=[],
        rows=10,
        description="Order:"
    )

    add_btn = widgets.Button(description="Add →")
    remove_btn = widgets.Button(description="Remove")
    up_btn = widgets.Button(description="▲ Up")
    down_btn = widgets.Button(description="▼ Down")

    conflict_resolution = widgets.RadioButtons(
        options=["consensus", "order"],
        value="consensus",
        description="Conflict:"
    )

    
    generate_btn = widgets.Button(
        description="Generate KB",
        button_style="success"
    )

    ui = widgets.VBox([
        widgets.HBox([
            available,
            widgets.VBox([add_btn]),
            selected,
            widgets.VBox([up_btn, down_btn, remove_btn])
        ]),
        conflict_resolution,
        generate_btn
    ])

    return (
        ui,
        available,
        selected,
        conflict_resolution,
        add_btn,
        remove_btn,
        up_btn,
        down_btn,
        generate_btn,
    )

def add_cases(_, available, selected):
    current = list(selected.options)
    for item in available.value:
        if item not in current:
            current.append(item)
    selected.options = current


def remove_case(_, selected):
    if selected.value is None:
        return

    current = list(selected.options)
    current.remove(selected.value)
    selected.options = current


def move_up(_, selected):
    if selected.value is None:
        return

    current = list(selected.options)
    idx = current.index(selected.value)

    if idx > 0:
        current[idx], current[idx - 1] = current[idx - 1], current[idx]
        selected.options = current
        selected.value = current[idx - 1]


def move_down(_, selected):
    if selected.value is None:
        return

    current = list(selected.options)
    idx = current.index(selected.value)

    if idx < len(current) - 1:
        current[idx], current[idx + 1] = current[idx + 1], current[idx]
        selected.options = current
        selected.value = current[idx + 1]


def generate_kb(
    _,
    graph,
    selected,
    conflict_resolution,
    output
):
    cases = list(selected.options)

    results = run_query_file(
        graph,
        "kb_template.rq",
        {"CASES": ", ".join(f"<{c}>" for c in cases)}
    )

    rules = [
        {
            "case": str(row.case),
            "content": str(row.content)
        }
        for row in results
    ]

    if conflict_resolution.value == "consensus":
        kb_rules, errors = resolve_consensus(rules)
    else:
        kb_rules, errors = resolve_order(rules, cases)

    with output:
        output.clear_output()

        if errors:
            print("ERRORS:")
            for e in errors:
                print(" -", e)

        placeholder = "// EFFECT RULES ARE INSERTED BELOW"

        rule_strings = [
            effect + " := {" + ",\n\t".join(relations) + "}."
            for effect, relations in kb_rules.items()
        ]

        with open("kb_template.idp", encoding="utf8") as f:
            kb = f.read()

        kb = kb.replace(
            placeholder,
            placeholder + "\n" + "\n\n".join(rule_strings)
        )
        
        open_interactive_consultant(kb)
        print("\n\n".join(rule_strings))


def open_interactive_consultant(kb: str):
    kb_json = json.dumps(kb)

    display(Javascript(f"""
    (async () => {{
        // Load lz-string if needed
        if (typeof window.LZString === "undefined") {{
            await new Promise((resolve, reject) => {{
                const script = document.createElement("script");
                script.src =
                    "https://cdn.jsdelivr.net/npm/lz-string@1.5.0/libs/lz-string.min.js";
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            }});
        }}

        const compressed =
            window.LZString.compressToEncodedURIComponent({kb_json});

        const url =
            "https://interactive-consultant.idp-z3.be/?"
            + compressed
            + "&ic=true";

        const a = document.createElement("a");
        a.href = url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";

        document.body.appendChild(a);
        a.click();
        a.remove();
    }})();
    """))
