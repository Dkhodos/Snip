import { BaseApi } from "./BaseApi";

export class SeedApi extends BaseApi {
	async seed(): Promise<{ message: string; links_created: number }> {
		return this.post("/dev/seed");
	}
}
