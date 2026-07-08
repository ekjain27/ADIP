import knowledge_retrieval as kr


class FakeDKE016Graph:
    def __init__(self):
        self.nodes = [
            {
                "id": "supplier",
                "canonicalName": "Supplier A",
                "type": "supplier",
                "aliases": ["Supplier Alpha"],
                "attributes": {"region": "NA"},
                "confidence": 0.91,
                "sourceIds": ["source-1"],
            },
            {"id": "factory", "canonicalName": "Factory B", "type": "factory", "aliases": [], "attributes": {}, "confidence": 0.86},
        ]
        self.edges = [
            {
                "id": "edge-1",
                "sourceNodeId": "supplier",
                "targetNodeId": "factory",
                "relationType": "depends_on",
                "confidence": 0.82,
                "weight": 0.7,
                "evidenceIds": ["evidence-1"],
            }
        ]
        self.evidence = [
            {
                "id": "evidence-1",
                "nodeId": "supplier",
                "sourceId": "contract",
                "sourceType": "document",
                "excerpt": "Supplier A supports Factory B",
                "confidence": 0.88,
            }
        ]

    def getNodeById(self, node_id):
        return next((node for node in self.nodes if node["id"] == node_id), None)

    def getNodeByCanonicalName(self, canonical_name):
        return next((node for node in self.nodes if node["canonicalName"] == canonical_name), None)

    def getEdgesBySourceNode(self, source_node_id):
        return [edge for edge in self.edges if edge["sourceNodeId"] == source_node_id]

    def getEdgesByTargetNode(self, target_node_id):
        return [edge for edge in self.edges if edge["targetNodeId"] == target_node_id]


def test_dke016_adapter_behavior_using_fake_graph_data():
    adapter = kr.DKE016KnowledgeGraphAdapter(FakeDKE016Graph())
    engine = kr.KnowledgeRetrievalEngine(store=adapter)
    context = engine.retrieve_context(kr.RetrievalQuery(entities=("Supplier A",), mode=kr.RetrievalMode.HYBRID))
    assert context.facts[0].id == "supplier"
    assert context.relationships[0].id == "edge-1"
    assert context.evidence[0].id == "evidence-1"


def test_dke017_compatibility_using_fake_reasoning_input():
    node = kr.KnowledgeNode(id="supplier", name="Supplier A", type="supplier", confidence=91)
    relationship = kr.KnowledgeRelationship(id="edge-1", source_id="supplier", target_id="factory", relationship_type=kr.RelationshipType.DEPENDS_ON)
    evidence = kr.EvidenceItem(id="evidence-1", node_id="supplier", source="contract", excerpt="Supplier A supports Factory B")
    context = kr.ContextPackage(
        query=kr.RetrievalQuery(text="Supplier A", entities=("Supplier A",)),
        entities=("Supplier A",),
        facts=(node,),
        relationships=(relationship,),
        evidence=(evidence,),
        confidence=91,
    )
    reasoning_input = kr.context_to_reasoning_input(context)
    assert reasoning_input["metadata"]["source_module"] == "DKE-018"
    assert reasoning_input["metadata"]["target_module"] == "DKE-017"
    assert reasoning_input["facts"][0]["canonicalName"] == "Supplier A"
    assert reasoning_input["relationships"][0]["type"] == "depends_on"
    assert "search" not in reasoning_input
