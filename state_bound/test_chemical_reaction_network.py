from state_bound.chemical_reaction_network import (
    ReactionNode,
    evaluate_reaction_network,
)


def test_catalyst_improves_evidence_without_creating_authority():
    node = ReactionNode("verify", 0.9, 0.0, 1.0, 0.4)
    plain = evaluate_reaction_network((node,))
    catalyzed = evaluate_reaction_network((node,), catalyst=0.8)
    assert catalyzed.network_reactivity > plain.network_reactivity
    assert catalyzed.mode in {"UNKNOWN", "PROCEED"}
    assert "decision=PROCEED" not in plain.trace or plain.mode != "PROCEED"


def test_hard_inhibitor_stops_chain():
    nodes = (
        ReactionNode("prepare", 0.95, 0.0, 1.0, 1.0, 0.2),
        ReactionNode("execute", 0.95, 0.9, 1.0, 1.0, 0.2),
    )
    result = evaluate_reaction_network(nodes)
    assert result.mode == "INHIBIT"
    assert result.weakest_node == "execute"


def test_downstream_consequence_propagates_pressure():
    nodes = (
        ReactionNode("a", 1.0, 0.0, 1.0, 1.0, 0.9),
        ReactionNode("b", 1.0, 0.0, 1.0, 1.0, 0.9),
    )
    result = evaluate_reaction_network(nodes)
    assert result.cascade_pressure >= 0.60
    assert result.mode == "HOLD"


def test_weakest_link_controls_network():
    nodes = (
        ReactionNode("strong", 1.0, 0.0, 1.0, 1.0),
        ReactionNode("weak", 0.8, 0.0, 0.3, 0.4),
        ReactionNode("strong-2", 1.0, 0.0, 1.0, 1.0),
    )
    result = evaluate_reaction_network(nodes)
    assert result.weakest_node == "weak"
    assert result.mode in {"HOLD", "UNKNOWN"}


def test_replay_is_deterministic():
    nodes = (
        ReactionNode("a", 0.8, 0.1, 0.9, 0.8, 0.1),
        ReactionNode("b", 0.9, 0.0, 0.95, 0.9, 0.2),
    )
    assert evaluate_reaction_network(nodes, catalyst=0.2) == evaluate_reaction_network(
        nodes, catalyst=0.2
    )
