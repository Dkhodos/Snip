import { BaseApi } from "./BaseApi";
import type { FeatureFlags } from "./types";

export class FlagsApi extends BaseApi {
	async getAll(): Promise<FeatureFlags> {
		return this.get<FeatureFlags>("/flags");
	}
}
