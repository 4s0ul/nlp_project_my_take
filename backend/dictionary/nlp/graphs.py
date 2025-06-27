from typing import List, Dict, Any
import networkx as nx
from networkx.classes import DiGraph
from networkx.readwrite import json_graph
from dictionary.nlp.triplets import TripletData


async def serialize_graph(graph: DiGraph) -> Dict[str, Any]:
    return json_graph.node_link_data(graph)


async def deserialize_graph(graph_data: Dict[str, Any]) -> nx.DiGraph:
    return json_graph.node_link_graph(graph_data)


async def create_graph() -> DiGraph:
    return nx.DiGraph()


async def add_triplets_to_graph(graph: DiGraph, triplets: List[TripletData]) -> DiGraph:
    for triplet in triplets:
        graph.add_node(triplet.subject, type=triplet.subject_type)
        graph.add_node(triplet.object, type=triplet.object_type)
        graph.add_edge(
            triplet.subject,
            triplet.object,
            predicate=triplet.predicate,
            predicate_type=triplet.predicate_type,
            position=triplet.position,
        )

    return graph


async def remove_triplets_from_graph(
    graph: nx.DiGraph, triplets: List[TripletData]
) -> DiGraph:
    for triplet in triplets:
        if graph.has_edge(triplet.subject, triplet.object):
            edge_data = graph.get_edge_data(triplet.subject, triplet.object)
            if (
                edge_data.get("predicate") == triplet.predicate
                and edge_data.get("predicate_type") == triplet.predicate_type
            ):
                graph.remove_edge(triplet.subject, triplet.object)

                if (
                    graph.in_degree(triplet.subject) == 0
                    and graph.out_degree(triplet.subject) == 0
                ):
                    graph.remove_node(triplet.subject)
                if (
                    graph.in_degree(triplet.object) == 0
                    and graph.out_degree(triplet.object) == 0
                ):
                    graph.remove_node(triplet.object)
    return graph
