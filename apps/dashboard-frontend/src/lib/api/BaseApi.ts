import axios, { type AxiosInstance } from "axios";

// Shared axios instance so all API classes share the same auth token
const sharedClient: AxiosInstance = axios.create({
	baseURL: import.meta.env.VITE_API_URL || "/api",
});

export function setAuthToken(token: string | null) {
	if (token) {
		sharedClient.defaults.headers.common.Authorization = `Bearer ${token}`;
	} else {
		sharedClient.defaults.headers.common.Authorization = undefined;
	}
}

export abstract class BaseApi {
	protected async get<T>(url: string, params?: object): Promise<T> {
		const { data } = await sharedClient.get<T>(url, { params });
		return data;
	}

	protected async post<T>(url: string, body?: object): Promise<T> {
		const { data } = await sharedClient.post<T>(url, body);
		return data;
	}

	protected async patch<T>(url: string, body?: object): Promise<T> {
		const { data } = await sharedClient.patch<T>(url, body);
		return data;
	}

	protected async delete(url: string): Promise<void> {
		await sharedClient.delete(url);
	}
}
