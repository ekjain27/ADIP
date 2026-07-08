import { performance } from "node:perf_hooks";
import { createKnowledgeGraphModule, type GraphConstructionInput, type LoggerPort } from "../index.js";

interface BenchmarkOptions {
  nodes: number;
  edgeFanout: number;
  batchSize: number;
}

class QuietLogger implements LoggerPort {
  debug(): void {}
  info(): void {}
  warn(): void {}
  error(): void {}
}

function readOptions(): BenchmarkOptions {
  return {
    nodes: Number(process.env.DKE_BENCH_NODES ?? "100000"),
    edgeFanout: Number(process.env.DKE_BENCH_EDGE_FANOUT ?? "1"),
    batchSize: Number(process.env.DKE_BENCH_BATCH_SIZE ?? "10000"),
  };
}

function createPayload(start: number, count: number, totalNodes: number, edgeFanout: number): GraphConstructionInput {
  const nodes = Array.from({ length: count }, (_, offset) => {
    const index = start + offset;
    return {
      id: `bench_node_${index}`,
      type: "concept" as const,
      canonicalName: String(index),
      aliases: [],
      attributes: { label: `Benchmark Node ${index}`, partition: Math.floor(index / 10000) },
      confidence: 0.9,
      sourceIds: [`bench_source_${index % 10}`],
    };
  });

  const edges = nodes.flatMap((node, offset) => {
    const index = start + offset;
    return Array.from({ length: edgeFanout }, (_, fanout) => {
      const target = start + ((offset + fanout + 1) % count);
      return {
        id: `bench_edge_${index}_${fanout}`,
        sourceNodeId: node.id,
        targetNodeId: `bench_node_${target}`,
        relationType: "related_to" as const,
        weight: 1,
        confidence: 0.8,
        evidenceIds: [],
      };
    });
  });

  return { nodes, edges, evidence: [] };
}

async function run(): Promise<void> {
  const options = readOptions();
  const module = createKnowledgeGraphModule({ logger: new QuietLogger() });
  const started = performance.now();

  for (let start = 0; start < options.nodes; start += options.batchSize) {
    const count = Math.min(options.batchSize, options.nodes - start);
    await module.controller.construct(createPayload(start, count, options.nodes, options.edgeFanout));
    const imported = start + count;
    const elapsedSeconds = (performance.now() - started) / 1000;
    console.info(JSON.stringify({
      importedNodes: imported,
      targetNodes: options.nodes,
      elapsedSeconds: Number(elapsedSeconds.toFixed(3)),
      nodesPerSecond: Number((imported / elapsedSeconds).toFixed(2)),
      metrics: module.metrics.snapshot(),
    }));
  }
}

await run();
