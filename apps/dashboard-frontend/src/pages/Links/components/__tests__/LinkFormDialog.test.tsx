import type { Link } from "@/lib/api";
import { TestWrapper } from "@/test/wrapper";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { fireEvent } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LinkFormDialog } from "../LinkFormDialog";

const { mockCreate, mockUpdate } = vi.hoisted(() => ({
	mockCreate: vi.fn(),
	mockUpdate: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
	linksApi: {
		create: (...args: unknown[]) => mockCreate(...args),
		update: (...args: unknown[]) => mockUpdate(...args),
	},
}));

function makeLink(overrides: Partial<Link> = {}): Link {
	return {
		id: "link-1",
		org_id: "org1",
		short_code: "abc",
		target_url: "https://original.com",
		title: "Original Title",
		click_count: 0,
		is_active: true,
		created_by: null,
		created_at: "2025-01-01T00:00:00Z",
		expires_at: null,
		...overrides,
	};
}

afterEach(() => {
	cleanup();
	document.body.removeAttribute("data-scroll-locked");
	document.body.style.removeProperty("pointer-events");
});

beforeEach(() => {
	vi.clearAllMocks();
});

function renderDialog(link?: Link | null) {
	const onOpenChange = vi.fn();
	const result = render(
		<TestWrapper>
			<LinkFormDialog
				open
				onOpenChange={onOpenChange}
				link={link ?? undefined}
			/>
		</TestWrapper>,
	);
	return { ...result, onOpenChange };
}

function setInputValue(input: HTMLInputElement, value: string) {
	fireEvent.change(input, { target: { value } });
}

function getForm() {
	return screen
		.getByPlaceholderText("My awesome link")
		.closest("form") as HTMLFormElement;
}

describe("LinkFormDialog", () => {
	describe("Create mode", () => {
		it("shows 'Create Link' title and description", () => {
			renderDialog();
			expect(
				screen.getByRole("heading", { name: "Create Link" }),
			).toBeInTheDocument();
			expect(screen.getByText("Add a new shortened link.")).toBeInTheDocument();
		});

		it("shows custom short code field", () => {
			renderDialog();
			expect(screen.getByPlaceholderText("my-link")).toBeInTheDocument();
		});

		it("submits create with form data", async () => {
			mockCreate.mockResolvedValue(makeLink());
			renderDialog();

			setInputValue(
				screen.getByPlaceholderText("My awesome link") as HTMLInputElement,
				"New Link",
			);
			setInputValue(
				screen.getByPlaceholderText("https://example.com") as HTMLInputElement,
				"https://test.com",
			);
			setInputValue(
				screen.getByPlaceholderText("my-link") as HTMLInputElement,
				"my-code",
			);

			fireEvent.submit(getForm());

			await waitFor(() => {
				expect(mockCreate).toHaveBeenCalledWith({
					target_url: "https://test.com",
					title: "New Link",
					custom_short_code: "my-code",
				});
			});
		});

		it("omits custom_short_code when empty", async () => {
			mockCreate.mockResolvedValue(makeLink());
			renderDialog();

			setInputValue(
				screen.getByPlaceholderText("My awesome link") as HTMLInputElement,
				"Link",
			);
			setInputValue(
				screen.getByPlaceholderText("https://example.com") as HTMLInputElement,
				"https://x.com",
			);

			fireEvent.submit(getForm());

			await waitFor(() => {
				expect(mockCreate).toHaveBeenCalledWith(
					expect.objectContaining({ custom_short_code: undefined }),
				);
			});
		});

		it("shows error message on failure", async () => {
			mockCreate.mockRejectedValue(new Error("Server error"));
			renderDialog();

			setInputValue(
				screen.getByPlaceholderText("My awesome link") as HTMLInputElement,
				"Link",
			);
			setInputValue(
				screen.getByPlaceholderText("https://example.com") as HTMLInputElement,
				"https://x.com",
			);

			fireEvent.submit(getForm());

			expect(
				await screen.findByText(/failed to create link/i),
			).toBeInTheDocument();
		});
	});

	describe("Edit mode", () => {
		const link = makeLink();

		it("shows 'Edit Link' title", () => {
			renderDialog(link);
			expect(
				screen.getByRole("heading", { name: "Edit Link" }),
			).toBeInTheDocument();
			expect(
				screen.getByText("Update the link details below."),
			).toBeInTheDocument();
		});

		it("hides custom short code field", async () => {
			renderDialog(link);
			await waitFor(() => {
				expect(screen.getByPlaceholderText("My awesome link")).toHaveValue(
					"Original Title",
				);
			});
			expect(screen.queryByPlaceholderText("my-link")).not.toBeInTheDocument();
		});

		it("pre-fills form with link data", async () => {
			renderDialog(link);
			await waitFor(() => {
				expect(screen.getByPlaceholderText("My awesome link")).toHaveValue(
					"Original Title",
				);
			});
			expect(screen.getByPlaceholderText("https://example.com")).toHaveValue(
				"https://original.com",
			);
		});

		it("only sends changed fields on update", async () => {
			mockUpdate.mockResolvedValue(link);
			renderDialog(link);

			await waitFor(() => {
				expect(screen.getByPlaceholderText("My awesome link")).toHaveValue(
					"Original Title",
				);
			});

			setInputValue(
				screen.getByPlaceholderText("My awesome link") as HTMLInputElement,
				"Updated Title",
			);

			fireEvent.submit(getForm());

			await waitFor(() => {
				expect(mockUpdate).toHaveBeenCalledWith("link-1", {
					title: "Updated Title",
				});
			});
		});

		it("sends empty updates when nothing changed", async () => {
			mockUpdate.mockResolvedValue(link);
			renderDialog(link);

			await waitFor(() => {
				expect(screen.getByPlaceholderText("My awesome link")).toHaveValue(
					"Original Title",
				);
			});

			fireEvent.submit(getForm());

			await waitFor(() => {
				expect(mockUpdate).toHaveBeenCalledWith("link-1", {});
			});
		});

		it("shows error message on failure", async () => {
			mockUpdate.mockRejectedValue(new Error("Server error"));
			renderDialog(link);

			await waitFor(() => {
				expect(screen.getByPlaceholderText("My awesome link")).toHaveValue(
					"Original Title",
				);
			});

			setInputValue(
				screen.getByPlaceholderText("My awesome link") as HTMLInputElement,
				"New",
			);

			fireEvent.submit(getForm());

			expect(
				await screen.findByText(/failed to update link/i),
			).toBeInTheDocument();
		});
	});
});
