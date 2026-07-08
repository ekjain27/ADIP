import type { ReasoningQuery, ReasoningResult } from "../domain/models.js";
import type { GraphReasoningService } from "../services/index.js";

export class KnowledgeGraphReasoningController {
  constructor(private readonly service: GraphReasoningService) {}

  async reason(body: ReasoningQuery): Promise<ReasoningResult> {
    return this.service.reason(body);
  }

  async paths(body: ReasoningQuery): Promise<ReasoningResult["paths"]> {
    return (await this.service.reason(body)).paths;
  }

  async rules(body: ReasoningQuery): Promise<ReasoningResult["conclusions"]> {
    return (await this.service.reason(body)).conclusions;
  }

  async conflicts(body: ReasoningQuery): Promise<ReasoningResult["conflicts"]> {
    return (await this.service.reason(body)).conflicts;
  }

  async missingLinks(body: ReasoningQuery): Promise<ReasoningResult["missingLinkSuggestions"]> {
    return (await this.service.reason(body)).missingLinkSuggestions;
  }

  async explain(body: ReasoningQuery): Promise<ReasoningResult["explanation"]> {
    return (await this.service.reason(body)).explanation;
  }
}
