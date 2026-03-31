import { BaseApi } from "./BaseApi";
import type {
	CreateLinkRequest,
	Link,
	LinkListResponse,
	UpdateLinkRequest,
} from "./types";

export class LinksApi extends BaseApi {
	async list(
		page = 1,
		limit = 20,
		search?: string,
		sortBy?: string,
		sortOrder?: string,
		status?: string,
	): Promise<LinkListResponse> {
		return this.get<LinkListResponse>("/links", {
			page,
			limit,
			search,
			sort_by: sortBy,
			sort_order: sortOrder,
			status,
		});
	}

	async getById(id: string): Promise<Link> {
		return this.get<Link>(`/links/${id}`);
	}

	async create(body: CreateLinkRequest): Promise<Link> {
		return this.post<Link>("/links", body);
	}

	async update(id: string, body: UpdateLinkRequest): Promise<Link> {
		return this.patch<Link>(`/links/${id}`, body);
	}

	async remove(id: string): Promise<void> {
		return this.delete(`/links/${id}`);
	}
}
