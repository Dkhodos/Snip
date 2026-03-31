import type { Link, LinkListResponse } from "@/lib/api";
import { TestWrapper } from "@/test/wrapper";
import {
	cleanup,
	render,
	screen,
	waitFor,
	within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LinksPage } from "../LinksPage";

const { mockList } = vi.hoisted(() => ({
	mockList: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
	linksApi: {
		list: (...args: unknown[]) => mockList(...args),
		create: vi.fn(),
		update: vi.fn(),
		remove: vi.fn(),
	},
}));

function makeLink(overrides: Partial<Link> = {}): Link {
	return {
		id: "1",
		org_id: "org1",
		short_code: "abc123",
		target_url: "https://example.com",
		title: "Test Link",
		click_count: 42,
		is_active: true,
		created_by: null,
		created_at: new Date().toISOString(),
		expires_at: null,
		...overrides,
	};
}

function mockResponse(
	items: Link[] = [makeLink()],
	total = items.length,
): LinkListResponse {
	return { items, total, page: 1, limit: 20 };
}

afterEach(() => {
	cleanup();
	document.body.removeAttribute("data-scroll-locked");
	document.body.style.removeProperty("pointer-events");
});

beforeEach(() => {
	vi.clearAllMocks();
	mockList.mockResolvedValue(mockResponse());
});

function renderPage() {
	return render(
		<TestWrapper>
			<LinksPage />
		</TestWrapper>,
	);
}

describe("LinksPage", () => {
	it("displays link data in the table", async () => {
		renderPage();
		expect(await screen.findByText("Test Link")).toBeInTheDocument();
		expect(screen.getByText("abc123")).toBeInTheDocument();
		expect(screen.getByText("https://example.com")).toBeInTheDocument();
		expect(screen.getByText("42")).toBeInTheDocument();
	});

	it("shows empty state when no links", async () => {
		mockList.mockResolvedValue(mockResponse([]));
		renderPage();
		expect(
			await screen.findByText("No links found. Create your first link!"),
		).toBeInTheDocument();
	});

	it("shows Active badge for active link", async () => {
		renderPage();
		await screen.findByText("Test Link");
		const table = screen.getByRole("table");
		expect(within(table).getByText("Active")).toBeInTheDocument();
	});

	it("shows Inactive badge for inactive link", async () => {
		mockList.mockResolvedValue(
			mockResponse([makeLink({ id: "inactive-1", is_active: false })]),
		);
		renderPage();
		await screen.findByText("Test Link");
		const table = screen.getByRole("table");
		expect(within(table).getByText("Inactive")).toBeInTheDocument();
	});

	it("shows Expired badge for expired link", async () => {
		mockList.mockResolvedValue(
			mockResponse([
				makeLink({ id: "expired-1", expires_at: "2020-01-01T00:00:00Z" }),
			]),
		);
		renderPage();
		await screen.findByText("Test Link");
		const table = screen.getByRole("table");
		expect(within(table).getByText("Expired")).toBeInTheDocument();
	});

	it("shows Create Link button that opens dialog", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		renderPage();
		await screen.findByText("Test Link");

		const createBtn = screen.getByRole("button", { name: /create link/i });
		await user.click(createBtn);

		expect(screen.getByText("Add a new shortened link.")).toBeInTheDocument();
	});

	it("filters by status when clicking filter buttons", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		renderPage();
		await screen.findByText("Test Link");

		mockList.mockClear();
		mockList.mockResolvedValue(mockResponse([]));

		// The filter buttons are outside the table
		const filterContainer = screen.getByText("All")
			.parentElement as HTMLElement;
		const activeFilterBtn = within(filterContainer).getByText("Active");
		await user.click(activeFilterBtn);

		await waitFor(() => {
			expect(mockList).toHaveBeenCalledWith(
				1,
				20,
				undefined,
				"created_at",
				"desc",
				"active",
			);
		});
	});

	it("debounces search input", async () => {
		vi.useFakeTimers({ shouldAdvanceTime: true });
		const user = userEvent.setup({
			advanceTimers: vi.advanceTimersByTime,
			pointerEventsCheck: 0,
		});
		renderPage();
		await screen.findByText("Test Link");

		mockList.mockClear();
		mockList.mockResolvedValue(mockResponse([]));

		const searchInput = screen.getByPlaceholderText("Search links...");
		await user.type(searchInput, "hello");

		vi.advanceTimersByTime(350);

		await waitFor(() => {
			expect(mockList).toHaveBeenCalledWith(
				1,
				20,
				"hello",
				"created_at",
				"desc",
				undefined,
			);
		});
		vi.useRealTimers();
	});

	it("toggles sort order when clicking same column", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		renderPage();
		await screen.findByText("Test Link");

		mockList.mockClear();
		mockList.mockResolvedValue(mockResponse());

		const createdHeader = screen.getByRole("button", { name: /created/i });
		await user.click(createdHeader);

		await waitFor(() => {
			expect(mockList).toHaveBeenCalledWith(
				1,
				20,
				undefined,
				"created_at",
				"asc",
				undefined,
			);
		});
	});

	it("changes sort column when clicking a different column", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		renderPage();
		await screen.findByText("Test Link");

		mockList.mockClear();
		mockList.mockResolvedValue(mockResponse());

		const titleHeader = screen.getByRole("button", { name: /title/i });
		await user.click(titleHeader);

		await waitFor(() => {
			expect(mockList).toHaveBeenCalledWith(
				1,
				20,
				undefined,
				"title",
				"asc",
				undefined,
			);
		});
	});

	it("shows pagination when more than one page", async () => {
		mockList.mockResolvedValue({
			items: [makeLink()],
			total: 40,
			page: 1,
			limit: 20,
		});
		renderPage();
		await screen.findByText("Test Link");

		expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
		expect(screen.getByRole("button", { name: /next/i })).not.toBeDisabled();
	});

	it("hides pagination when only one page", async () => {
		renderPage();
		await screen.findByText("Test Link");
		expect(screen.queryByText(/Page \d+ of/)).not.toBeInTheDocument();
	});

	it("shows dash for link with no title", async () => {
		mockList.mockResolvedValue(mockResponse([makeLink({ title: null })]));
		renderPage();
		expect(await screen.findByText("\u2014")).toBeInTheDocument();
	});
});
