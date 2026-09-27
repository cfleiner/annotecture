import ipywidgets as widgets
from problog_etc import run_problog_program

HTML_SPINNER = """
    <div style="display:flex;align-items:center;gap:10px">
      <div style="
          border:4px solid #ddd;
          border-top:4px solid #0078D4;
          border-radius:50%;
          width:20px;
          height:20px;
          animation: spin 1s linear infinite;">
      </div>
      <span>Running inference...</span>
    </div>
    
    <style>
    @keyframes spin {
      0%   { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    </style>
"""

def create_query_tab(var_domains):
    query_widgets = {}
    query_buttons = []
    for var in var_domains.keys():
        btn = widgets.ToggleButton(
            value=False,
            description=var,
            tooltip=f"Query {var}",
            layout=widgets.Layout(width="auto"),
        )

        query_widgets[var] = btn
        query_buttons.append(btn)

    query_layout = (
        widgets.FlowLayout(query_buttons)
        if hasattr(widgets, "FlowLayout")
        else widgets.GridBox(
            query_buttons,
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 220px)",
                grid_gap="8px",
            ),
        )
    )
    
    query_tab = widgets.VBox([
        widgets.HTML("<b>Select query variables</b>"),
        query_layout,
    ])

    return query_tab, query_widgets


def create_evidence_tab(var_domains):
    evidence_widgets = {}
    accordions = []

    for var, vals in var_domains.items():
        tb = widgets.ToggleButtons(
            options=["<unknown>"] + list(vals),
            description="",
            style={"button_width": "auto"},
            layout=widgets.Layout(width="auto"),
        )

        evidence_widgets[var] = tb

        box = widgets.VBox([tb])
        accordions.append(box)

    evidence_accordion = widgets.Accordion(children=accordions)

    for i, var in enumerate(var_domains.keys()):
        evidence_accordion.set_title(i, var)

    evidence_tab = widgets.VBox([evidence_accordion])

    return evidence_tab, evidence_widgets


def create_ui(var_domains):
    # --------------------------------------------------
    # Tabs
    # --------------------------------------------------
    query_tab, query_widgets = create_query_tab(var_domains)
    evidence_tab, evidence_widgets = create_evidence_tab(var_domains)
    tabs = widgets.Tab(children=[query_tab, evidence_tab])
    tabs.set_title(0, "Query")
    tabs.set_title(1, "Evidence")

    # --------------------------------------------------
    # Spinner
    # --------------------------------------------------
    spinner = widgets.HTML(HTML_SPINNER)
    spinner.layout.display = "none"
   
    # --------------------------------------------------
    # Run Button
    # --------------------------------------------------
    run_button = widgets.Button(
        description="Run Inference",
        button_style="success",
        icon="play"
    )
    
    # --------------------------------------------------
    # Main Layout
    # --------------------------------------------------
    ui = widgets.VBox([
        tabs,
        spinner,
        run_button
    ])
    return ui, spinner, run_button, evidence_widgets, query_widgets





def run_inference(btn, problog_file, var_domains, spinner, output, evidence_widgets, query_widgets):
    spinner.layout.display = ""
    btn.layout.display = "none"

    output.clear_output()
    
    evidence_lines = []
    query_lines = []

    for pred, widget in evidence_widgets.items():

        value = widget.value

        if value != "<unknown>":
            evidence_lines.append(
                f"evidence({pred}({value}), true)."
            )

    for pred, widget in query_widgets.items():

        if widget.value:
            for val in var_domains[pred]:
                query_lines.append(
                    f"query({pred}({val}))."
                )

    with output:

        print("Evidence")
        print("-------------------")

        
        for line in evidence_lines:
            print(line)

        print()

        # ----------------------------------
        # Load base ProbLog program
        # ----------------------------------

        with open(problog_file) as f:
            program = f.read()

        # Add evidence and queries
        program += "\n\n"
        program += "\n".join(evidence_lines)
        program += "\n"
        program += "\n".join(query_lines)

        print("\n".join(run_problog_program(program)))

        spinner.layout.display = "none"
        btn.layout.display = ""