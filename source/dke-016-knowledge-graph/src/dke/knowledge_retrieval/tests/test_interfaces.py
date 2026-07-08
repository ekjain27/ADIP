import knowledge_retrieval.interfaces as interfaces


def test_interfaces_export_adapter_contracts():
    assert hasattr(interfaces, "KnowledgeStore")
    assert hasattr(interfaces, "SemanticSearchProvider")
    assert hasattr(interfaces, "GraphSearchProvider")
    assert hasattr(interfaces, "EvidenceProvider")


def test_public_apis_are_exported_from_init():
    expected = {
        "retrieve",
        "retrieve_entity",
        "retrieve_context",
        "retrieve_related",
        "retrieve_evidence",
        "retrieve_subgraph",
        "expand_entity",
        "DKE016KnowledgeGraphAdapter",
        "DKE017ContextAdapter",
        "context_to_reasoning_input",
    }
    assert expected.issubset(set(__import__("knowledge_retrieval").__all__))
