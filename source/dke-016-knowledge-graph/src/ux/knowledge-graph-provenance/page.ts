import type { GraphEdge, GraphNode, KnowledgeGraphSnapshot } from "./types.js";

export function renderKnowledgeGraphExplorer(snapshot: KnowledgeGraphSnapshot): string {
  const node = snapshot.nodes[0];
  const edge = snapshot.edges[0];
  return `
    <section class="ux-kg" aria-labelledby="kg-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-003</p>
          <h1 id="kg-title">${escapeHtml(snapshot.summary.title)}</h1>
          <div class="ux-workspace-meta">
            <span>${escapeHtml(snapshot.summary.selectedSource)}</span>
            <span>${snapshot.summary.nodeCount} nodes</span>
            <span>${snapshot.summary.edgeCount} edges</span>
            <span>Refreshed ${escapeHtml(formatTimestamp(snapshot.summary.lastRefreshedAt))}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(toTitle(snapshot.summary.status))}</span>
      </header>
      <section class="ux-workspace-actions" aria-label="Graph actions">
        <button type="button">Refresh Graph</button><button type="button">Load Provenance</button><button type="button">Reset View</button>
      </section>
      <section class="ux-kg-grid">
        <article class="ux-panel ux-kg-graph-panel"><h2>Graph Visualization</h2>${renderGraph(snapshot.nodes, snapshot.edges)}</article>
        <article class="ux-panel"><h2>Graph Filters</h2><div class="ux-filter-grid">${Object.entries(snapshot.filters).map(([key, value]) => `<label>${escapeHtml(toTitle(key))}<span>${escapeHtml(value)}</span></label>`).join("")}</div></article>
        <article class="ux-panel">${renderNodeInspector(node)}</article>
        <article class="ux-panel">${renderEdgeInspector(edge, snapshot.nodes)}</article>
        <article class="ux-panel ux-kg-timeline-panel"><h2>Provenance Timeline</h2><ol class="ux-timeline">${snapshot.timeline.map((event) => `<li data-status="complete"><div><strong>${escapeHtml(event.title)}</strong><span>${escapeHtml(formatTimestamp(event.timestamp))} - ${escapeHtml(event.sourceModule)}</span><p>${escapeHtml(event.detail)}</p></div><span class="ux-activity-badge">${escapeHtml(toTitle(event.type))}</span></li>`).join("")}</ol></article>
      </section>
    </section>
  `;
}

function renderGraph(nodes: readonly GraphNode[], edges: readonly GraphEdge[]): string {
  return `<div class="ux-graph-canvas" aria-label="Knowledge graph visualization"><svg viewBox="0 0 760 240" role="img" aria-label="Decision provenance graph">${edges.map((edge) => {
    const source = nodes.find((item) => item.id === edge.sourceNodeId);
    const target = nodes.find((item) => item.id === edge.targetNodeId);
    if (!source || !target) return "";
    return `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" class="ux-graph-edge" /><text x="${(source.x + target.x) / 2}" y="${(source.y + target.y) / 2 - 8}" class="ux-graph-edge-label">${escapeHtml(edge.label)}</text>`;
  }).join("")}${nodes.map((node) => `<g><circle cx="${node.x}" cy="${node.y}" r="22" class="ux-graph-node" /><text x="${node.x}" y="${node.y + 40}" text-anchor="middle" class="ux-graph-node-label">${escapeHtml(node.label)}</text></g>`).join("")}</svg></div>`;
}

function renderNodeInspector(node: GraphNode): string {
  return `<h2>Node Inspector</h2><dl class="ux-inspector-list"><div><dt>Node ID</dt><dd>${escapeHtml(node.id)}</dd></div><div><dt>Label</dt><dd>${escapeHtml(node.label)}</dd></div><div><dt>Type</dt><dd>${escapeHtml(node.type)}</dd></div><div><dt>Confidence</dt><dd>${Math.round(node.confidence * 100)}%</dd></div><div><dt>Source Module</dt><dd>${escapeHtml(node.sourceModule)}</dd></div><div><dt>Governance Status</dt><dd>${escapeHtml(node.governanceStatus)}</dd></div><div><dt>Related Decisions</dt><dd>${escapeHtml(node.relatedDecisions.join(", "))}</dd></div><div><dt>Metadata</dt><dd>${escapeHtml(Object.entries(node.metadata).map(([key, value]) => `${key}: ${value}`).join("; "))}</dd></div></dl>`;
}

function renderEdgeInspector(edge: GraphEdge, nodes: readonly GraphNode[]): string {
  const source = nodes.find((node) => node.id === edge.sourceNodeId)?.label ?? edge.sourceNodeId;
  const target = nodes.find((node) => node.id === edge.targetNodeId)?.label ?? edge.targetNodeId;
  return `<h2>Edge Inspector</h2><dl class="ux-inspector-list"><div><dt>Edge ID</dt><dd>${escapeHtml(edge.id)}</dd></div><div><dt>Source Node</dt><dd>${escapeHtml(source)}</dd></div><div><dt>Target Node</dt><dd>${escapeHtml(target)}</dd></div><div><dt>Relationship</dt><dd>${escapeHtml(edge.relationshipType)}</dd></div><div><dt>Confidence</dt><dd>${Math.round(edge.confidence * 100)}%</dd></div><div><dt>Provenance Reference</dt><dd>${escapeHtml(edge.provenanceReference)}</dd></div><div><dt>Timestamp</dt><dd>${escapeHtml(formatTimestamp(edge.timestamp))}</dd></div></dl>`;
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true }).format(date).replace(" am", " AM").replace(" pm", " PM");
}

function toTitle(value: string): string {
  return value.replaceAll("-", " ").replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}
