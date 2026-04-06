import type { Link } from "@/lib/api";
import { TestWrapper } from "@/test/wrapper";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { OgPreviewDialog } from "../OgPreviewDialog";

const { mockGetOgImageUrl, mockGenerateOgImage } = vi.hoisted(() => ({
	mockGetOgImageUrl: vi.fn(),
	mockGenerateOgImage: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
	linksApi: {
		getOgImageUrl: (...args: unknown[]) => mockGetOgImageUrl(...args),
		generateOgImage: (...args: unknown[]) => mockGenerateOgImage(...args),
	},
}));

function makeLink(overrides: Partial<Link> = {}): Link {
	return {
		id: "link-1",
		org_id: "org1",
		short_code: "abc",
		target_url: "https://example.com",
		title: "My Link",
		click_count: 5,
		is_active: true,
		created_by: null,
		created_at: "2025-01-01T00:00:00Z",
		expires_at: null,
		...overrides,
	};
}

describe("OgPreviewDialog", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders dialog title and link name when open", async () => {
		mockGetOgImageUrl.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});

		render(
			<TestWrapper>
				<OgPreviewDialog open link={makeLink()} onOpenChange={vi.fn()} />
			</TestWrapper>,
		);

		expect(screen.getByText("OG Image Preview")).toBeInTheDocument();
		expect(screen.getByText("My Link")).toBeInTheDocument();
	});

	it("does not call getOgImageUrl when closed", () => {
		render(
			<TestWrapper>
				<OgPreviewDialog
					open={false}
					link={makeLink()}
					onOpenChange={vi.fn()}
				/>
			</TestWrapper>,
		);

		// Query should be disabled when dialog is closed
		expect(mockGetOgImageUrl).not.toHaveBeenCalled();
	});

	it("shows Regenerate and Copy URL buttons", async () => {
		mockGetOgImageUrl.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});

		render(
			<TestWrapper>
				<OgPreviewDialog open link={makeLink()} onOpenChange={vi.fn()} />
			</TestWrapper>,
		);

		expect(
			screen.getByRole("button", { name: /regenerate/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /copy url/i }),
		).toBeInTheDocument();
	});

	it("calls generateOgImage when Regenerate is clicked", async () => {
		mockGetOgImageUrl.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});
		mockGenerateOgImage.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});

		render(
			<TestWrapper>
				<OgPreviewDialog open link={makeLink()} onOpenChange={vi.fn()} />
			</TestWrapper>,
		);

		await userEvent.click(screen.getByRole("button", { name: /regenerate/i }));

		await waitFor(() => {
			expect(mockGenerateOgImage).toHaveBeenCalledWith("link-1");
		});
	});

	it("closes dialog when Close is clicked", async () => {
		mockGetOgImageUrl.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});
		const onOpenChange = vi.fn();

		render(
			<TestWrapper>
				<OgPreviewDialog open link={makeLink()} onOpenChange={onOpenChange} />
			</TestWrapper>,
		);

		// Two "Close" buttons exist (X icon + footer); the footer one has visible text content
		const closeButtons = screen.getAllByRole("button", { name: /close/i });
		// biome-ignore lint/style/noNonNullAssertion: guaranteed by getAllByRole returning 2 elements
		const footerClose = closeButtons.find(
			(btn) => btn.textContent?.trim() === "Close",
		)!;
		await userEvent.click(footerClose);

		expect(onOpenChange).toHaveBeenCalledWith(false);
	});

	it("renders with short_code in description when title is absent", async () => {
		mockGetOgImageUrl.mockResolvedValue({
			og_image_url: "https://cdn.example.com/abc.png",
		});

		render(
			<TestWrapper>
				<OgPreviewDialog
					open
					link={makeLink({ title: null })}
					onOpenChange={vi.fn()}
				/>
			</TestWrapper>,
		);

		expect(screen.getByText("abc")).toBeInTheDocument();
	});
});
