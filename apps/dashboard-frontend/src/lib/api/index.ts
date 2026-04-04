export { setAuthToken } from "./BaseApi";
export * from "./types";

import { ClicksApi } from "./ClicksApi";
import { FlagsApi } from "./FlagsApi";
import { LinksApi } from "./LinksApi";
import { StatsApi } from "./StatsApi";

export const linksApi = new LinksApi();
export const clicksApi = new ClicksApi();
export const statsApi = new StatsApi();
export const flagsApi = new FlagsApi();
