import { BaseApi } from "./BaseApi";
import type { AggregateClicksResponse, ClicksResponse } from "./types";

export class ClicksApi extends BaseApi {
	async getForLink(linkId: string): Promise<ClicksResponse> {
		return this.get<ClicksResponse>(`/links/${linkId}/clicks`);
	}

	async getAggregate(): Promise<AggregateClicksResponse> {
		return this.get<AggregateClicksResponse>("/clicks/aggregate");
	}
}
