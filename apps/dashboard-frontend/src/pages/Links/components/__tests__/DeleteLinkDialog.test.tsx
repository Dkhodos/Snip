import type { Link } from "@/lib/api";
import { TestWrapper } from "@/test/wrapper";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DeleteLinkDialog } from "../DeleteLinkDialog";

const { mockRemove } = vi.hoisted(() => ({
	mockRemove: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
	linksApi: {
		remove: (...args: unknown[]) => mockRemove(...args),
	},
}));

function makeLink(overrides: Partial<Link> = {}): Link {
	return {
		id: "link-1",
		org_id: "org1",
		short_code: "abc",
		target_url: "https://example.com",
		title: "My Link",
		click_count: 0,
		is_active: true,
		created_by: null,
		created_at: "2025-01-01T00:00:00Z",
		expires_at: null,
		...overrides,
	};
}

beforeEach(() => {
	vi.clearAllMocks();
});

describe("DeleteLinkDialog", () => {
	it("shows link title in confirmation message", () => {
		render(
			<TestWrapper>
				<DeleteLinkDialog
					open
					onOpenChange={() => {}}
					link={makeLink({ title: "Important Link" })}
				/>
			</TestWrapper>,
		);
		expect(screen.getByText("Important Link")).toBeInTheDocument();
	});

	it("shows short_code when title is null", () => {
		render(
			<TestWrapper>
				<DeleteLinkDialog
					open
					onOpenChange={() => {}}
					link={makeLink({ title: null, short_code: "xyz789" })}
				/>
			</TestWrapper>,
		);
		expect(screen.getByText("xyz789")).toBeInTheDocument();
	});

	it("calls remove on delete click", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		mockRemove.mockResolvedValue(undefined);
		const onOpenChange = vi.fn();

		render(
			<TestWrapper>
				<DeleteLinkDialog open onOpenChange={onOpenChange} link={makeLink()} />
			</TestWrapper>,
		);

		await user.click(screen.getByRole("button", { name: /^delete$/i }));

		await waitFor(() => {
			expect(mockRemove).toHaveBeenCalledWith("link-1");
		});
	});

	it("closes dialog on successful delete", async () => {
		const user = userEvent.setup({ pointerEventsCheck: 0 });
		mockRemove.mockResolvedValue(undefined);
		const onOpenChange = vi.fn();

		render(
			<TestWrapper>
				<DeleteLinkDialog open onOpenChange={onOpenChange} link={makeLink()} />
			</TestWrapper>,
		);

		await user.click(screen.getByRole("button", { name: /^delete$/i }));

		await waitFor(() => {
			expect(onOpenChange).toHaveBeenCalledWith(false);
		});
	});

	it("has a cancel button", () => {
		render(
			<TestWrapper>
				<DeleteLinkDialog open onOpenChange={() => {}} link={makeLink()} />
			</TestWrapper>,
		);
		expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
	});
});
