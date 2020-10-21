import uuid
from typing import Tuple, Dict, List
from collections import deque
import networkx as nx

from .parsing import (
    Configuration,
    ConfigurationSyncStep,
    ConfigurationSyncStepTo,
    SyncPayload,
)
from .exceptions import DuplicateDestinationException

SyncData = Tuple[Dict[str, ConfigurationSyncStep], Dict[str, List[str]]]

unique_step_names = set()
unique_sync_names = set()


def make_step_name() -> str:
    """Returns a unique step name"""
    name = str(uuid.uuid4())
    if name in unique_step_names:
        return make_step_name()
    unique_step_names.add(name)
    return name


def make_sync_name(step: ConfigurationSyncStep, to: ConfigurationSyncStepTo) -> str:
    """Assembles a unique SyncPayload name which can be displayed to the user"""
    return f"[{step.name}]{step.from_field} -> {to.destination}"


def assemble_sync_data(configuration: Configuration) -> SyncData:
    sync_names_to_sync_payloads: Dict[str, SyncPayload] = {}
    sync_step_mapping: Dict[str, ConfigurationSyncStep] = {}

    for step in configuration.sync_steps:
        step: ConfigurationSyncStep = step

        # generating names if missing and avoids doubles
        if step.name is None:
            step.name = make_step_name()

        if step.before is None:
            step.before = []

        for to in step.to_fields:
            to: ConfigurationSyncStepTo = to
            entry_name = make_sync_name(step, to)
            if entry_name in sync_names_to_sync_payloads:
                raise DuplicateDestinationException(
                    f"A destination '{to.destination}' was already defined "
                    f"for step '{step.from_field}'"
                )
            sync_names_to_sync_payloads[entry_name] = SyncPayload(
                from_field=step.from_field, to_field=to
            )
            sync_step_mapping[step.name] = step

    graph = nx.DiGraph()

    nodes_list = list(sync_names_to_sync_payloads.keys())

    graph.add_nodes_from(nodes_list)
    # print("____NODES:", nodes_list)
    for step in configuration.sync_steps:
        step: ConfigurationSyncStep = step

        for to in step.to_fields:
            to: ConfigurationSyncStepTo = to

            # compute all of them from the predecessors
            node_edges = []
            for before_step_name in step.before:
                target = make_sync_name(step, to)

                before_step: ConfigurationSyncStep = sync_step_mapping[before_step_name]
                for before_to in before_step.to_fields:
                    before_to: ConfigurationSyncStepTo = before_to

                    source = make_sync_name(before_step, before_to)
                    node_edges.append((source, target))

            if len(node_edges) > 0:
                graph.add_edges_from(node_edges)
                # print(node_edges, ",")

    predecessors: Dict[str, List[str]] = {}
    for node in nodes_list:
        predecessors[node] = [x for x in graph.predecessors(node)]

    # print("Predecessors:", predecessors)

    if not nx.is_directed_acyclic_graph(graph):
        raise Exception(
            f"Please remove cyclic dependencies. Check predecessors:\n{predecessors}"
        )

    return sync_names_to_sync_payloads, predecessors