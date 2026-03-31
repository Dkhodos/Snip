import { BaseApi } from "./BaseApi";
import type { StatsResponse } from "./types";

export class StatsApi extends BaseApi {
	async getStats(): Promise<StatsResponse> {
		return this.get<StatsResponse>("/stats");
	}
}
