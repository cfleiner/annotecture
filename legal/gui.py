from functools import partial
import ipywidgets as widgets

from pythen_etc import label_for

def create_facts_tab(predicates):
    fact_buttons = []

    for pred in sorted(predicates):
        btn = widgets.ToggleButton(
            description=label_for(pred),
            tooltip=pred,
            layout=widgets.Layout(width="auto"),
            style={"button_width": "initial"}
        )

        # store actual predicate value
        btn.predicate = pred

        fact_buttons.append(btn)

    facts_tab = widgets.VBox([
        widgets.HTML("<b>Select facts</b>"),
        widgets.GridBox(
            fact_buttons,
            layout=widgets.Layout(
                grid_template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                grid_gap="5px"
            )
        )
    ])

    return facts_tab, fact_buttons

   
def create_target_tab(predicates, evaluator, fact_buttons):
    target_dropdown = widgets.Dropdown(
        options=[
            (label_for(pred), pred)
            for pred in sorted(predicates)
        ],
        description="Target:",
        layout=widgets.Layout(width="600px")
    )

    evaluate_button = widgets.Button(
        description="Evaluate",
        button_style="success",
        icon="play"
    )

    output = widgets.Output()

    def on_evaluate_clicked(btn, evaluator):
        selected_facts = [
            b.predicate
            for b in fact_buttons
            if b.value
        ]

        target = target_dropdown.value


        result = evaluator.explain(selected_facts, target)

        with output:
            output.clear_output()
            print("####################\n")
            print(result)


    evaluate_button.on_click(partial(on_evaluate_clicked, evaluator=evaluator))

    target_tab = widgets.VBox([
        widgets.HTML("<b>Select target predicate</b>"),
        target_dropdown,
        evaluate_button,
        output
    ])

    return target_tab, target_dropdown, evaluate_button, output

def create_gui(predicates, facts, evaluator):
    facts_tab, fact_buttons  = create_facts_tab(predicates)
    target_tab, target_dropdown, evaluate_button, output = create_target_tab(predicates, evaluator, fact_buttons)
    
    
    tabs = widgets.Tab(children=[facts_tab, target_tab])
    tabs.set_title(0, "Facts")
    tabs.set_title(1, "Target predicates")


    return {
        "tabs": tabs,
        "facts": fact_buttons,
        "target": target_dropdown,
        "evaluate": evaluate_button,
        "output": output,
    }