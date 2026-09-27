from string import Template
from rdflib import Graph, Namespace, BNode, Literal, RDF
from rdflib.namespace import Namespace
from rdflib.collection import Collection

from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
from yfiles_jupyter_graphs import GraphWidget
from IPython.display import display

PROV = Namespace("http://www.w3.org/ns/prov#")
EX = Namespace("http://www.example.com/")
OA = Namespace("http://www.w3.org/ns/oa#")
AS = Namespace("https://www.w3.org/ns/activitystreams#")

def run_query_file(graph: str | Graph, filepath: str, substitution_mapping: dict = {}):
    with open(filepath, mode="r", encoding="utf8") as f:
        content = f.read()

    query = Template(content).substitute(substitution_mapping)
    return run_query(graph, query)
    

def run_query(graph: str | Graph, query: str):
    if isinstance(graph, str):
        g = Graph()
        g.parse(graph)
    else:
        g = graph
    return g.query(query)

def convert_and_targets(graph):

    for s, p, o in list(graph.triples((None, EX.hasTarget, None))):

        if not isinstance(o, Literal):
            continue

        text = str(o)

        if " AND " not in text:
            continue

        items = [part.strip() for part in text.split(" AND ")]

        composite = BNode()
        graph.add((s, OA.hasTarget, composite))
        graph.add((composite, RDF.type, OA.Composite))

        rdf_list = BNode()
        graph.add((composite, AS.items, rdf_list))

        uris = [EX[item] for item in items]

        # Create RDF list
        Collection(graph, rdf_list, uris)

        # Remove old statement
        graph.remove((s, p, o))

    return graph
    
def add_inferred_provenance(g: Graph):
    """
    Adds:
    1. FormalRepresentation -> Claim:
       prov:wasDerivedFrom

    2. FormalRepresentation -> FormalRepresentation:
       prov:wasRevisionOf

       Claim -> Claim:
       prov:wasRevisionOf

    3. FormalRepresentations with the same target:
       prov:alternateOf
    """

    # Collect all formal representations and claims
    formal_reps = set(g.subjects(RDF.type, Namespace("http://www.example.com/")["FormalRepresentation"]))
    claims = set(g.subjects(RDF.type, Namespace("http://www.example.com/")["Claim"]))

    # Map annotation -> target source
    targets = {}

    for subj, _, specific_resource in g.triples((None, OA.hasTarget, None)):
        source = next(g.objects(specific_resource, OA.hasSource), None)
        if source:
            targets[subj] = source

    # Rule 1 + Rule 2
    for source_rep, target in targets.items():

        # FormalRepresentation -> Claim
        if source_rep in formal_reps and target in claims:
            g.add((source_rep, PROV.wasDerivedFrom, target))

        # FormalRepresentation -> FormalRepresentation
        if source_rep in formal_reps and target in formal_reps:
            g.add((source_rep, PROV.wasRevisionOf, target))

        # Claim -> Claim
        if source_rep in claims and target in claims:
            g.add((source_rep, PROV.wasRevisionOf, target))

    # Rule 3
    # Find formal representations sharing the same target
    target_to_reps = {}

    for fr in formal_reps:
        target = targets.get(fr)
        if target:
            target_to_reps.setdefault(target, []).append(fr)

    for target, reps in target_to_reps.items():
        if len(reps) < 2:
            continue

        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                g.add((reps[i], PROV.alternateOf, reps[j]))
                g.add((reps[j], PROV.alternateOf, reps[i]))

    return g

def add_namespaces(g: Graph) -> Graph:
    g.bind("ex", Namespace("http://www.example.com/"))
    g.bind("foaf", Namespace("http://xmlns.com/foaf/0.1/"))
    g.bind("oa", Namespace("http://www.w3.org/ns/oa#"))
    g.bind("as", Namespace("https://www.w3.org/ns/activitystreams#"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    return g


def show_rdf_graph(g):
    nodes = {}
    edges = []

    for s, p, o in g:
        s = str(s)
        p = str(p)
        o = str(o)

        nodes.setdefault(
            s,
            {"id": s, "label": s.rsplit("/", 1)[-1]}
        )

        nodes.setdefault(
            o,
            {"id": o, "label": o.rsplit("/", 1)[-1]}
        )

        edges.append({
            "id": f"{s}|{p}|{o}",
            "start": s,
            "end": o,
            "label": p.rsplit("/", 1)[-1]
        })

    w = GraphWidget()

    w.nodes = list(nodes.values())
    w.edges = edges

    w.node_id_mapping = lambda n: n["id"]
    w.node_label_mapping = lambda n: n["label"]

    w.edge_source_mapping = lambda e: e["start"]
    w.edge_target_mapping = lambda e: e["end"]
    w.edge_label_mapping = lambda e: e["label"]

    display(w)