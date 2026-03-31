import { TestWrapper } from "@/test/wrapper";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StatsCards } from "../components/StatsCards";

const { mockGetStats } = vi.hoisted(() => ({
	mockGetStats: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
	statsApi: { getStats: () => mockGetStats() },
}));

describe("StatsCards", () => {
	it("displays all four stat values", async () => {
		mockGetStats.mockResolvedValue({
			total_links: 25,
			total_clicks: 1500,
			active_links: 20,
			expired_links: 5,
		});

		render(
			<TestWrapper>
				<StatsCards />
			</TestWrapper>,
		);

		expect(await screen.findByText("25")).toBeInTheDocument();
		expect(screen.getByText("1500")).toBeInTheDocument();
		expect(screen.getByText("20")).toBeInTheDocument();
		expect(screen.getByText("5")).toBeInTheDocument();
	});

	it("displays correct labels", async () => {
		mockGetStats.mockResolvedValue({
			total_links: 0,
			total_clicks: 0,
			active_links: 0,
			expired_links: 0,
		});

		render(
			<TestWrapper>
				<StatsCards />
			</TestWrapper>,
		);

		expect(await screen.findByText("Total Links")).toBeInTheDocument();
		expect(screen.getByText("Total Clicks")).toBeInTheDocument();
		expect(screen.getByText("Active Links")).toBeInTheDocument();
		expect(screen.getByText("Expired Links")).toBeInTheDocument();
	});

	it("shows zeros when stats are all zero", async () => {
		mockGetStats.mockResolvedValue({
			total_links: 0,
			total_clicks: 0,
			active_links: 0,
			expired_links: 0,
		});

		render(
			<TestWrapper>
				<StatsCards />
			</TestWrapper>,
		);

		expect(await screen.findByText("Total Links")).toBeInTheDocument();
		const zeros = screen.getAllByText("0");
		expect(zeros.length).toBe(4);
	});
});
