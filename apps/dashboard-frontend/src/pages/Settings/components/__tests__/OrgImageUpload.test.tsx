import { TestWrapper } from "@/test/wrapper";
import {
	cleanup,
	fireEvent,
	render,
	screen,
	waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MAX_FILE_SIZE, OrgImageUpload, validateFile } from "../OrgImageUpload";

const mockSetLogo = vi.fn();

const { mockUseOrganization } = vi.hoisted(() => ({
	mockUseOrganization: vi.fn(),
}));

vi.mock("@clerk/react", () => ({
	useOrganization: () => mockUseOrganization(),
}));

function makeOrg(overrides: Record<string, unknown> = {}) {
	return {
		name: "Acme Inc",
		slug: "acme",
		imageUrl: "https://img.clerk.com/default.png",
		hasImage: false,
		setLogo: mockSetLogo,
		...overrides,
	};
}

function renderComponent() {
	return render(
		<TestWrapper>
			<OrgImageUpload />
		</TestWrapper>,
	);
}

function makeFile(name: string, type: string, sizeBytes = 1024): File {
	const content = new Uint8Array(sizeBytes);
	return new File([content], name, { type });
}

afterEach(() => {
	cleanup();
});

beforeEach(() => {
	vi.clearAllMocks();
});

describe("validateFile", () => {
	it("accepts valid image types", () => {
		for (const type of ["image/jpeg", "image/png", "image/gif", "image/webp"]) {
			expect(validateFile(makeFile("img", type))).toBeNull();
		}
	});

	it("rejects unsupported types", () => {
		expect(validateFile(makeFile("doc.pdf", "application/pdf"))).toBe(
			"Please upload a JPEG, PNG, GIF, or WebP image.",
		);
		expect(validateFile(makeFile("file.svg", "image/svg+xml"))).toBe(
			"Please upload a JPEG, PNG, GIF, or WebP image.",
		);
	});

	it("rejects files over max size", () => {
		const oversized = makeFile("big.png", "image/png", MAX_FILE_SIZE + 1);
		expect(validateFile(oversized)).toBe("Image must be under 10 MB.");
	});

	it("accepts files at exactly max size", () => {
		const exact = makeFile("ok.png", "image/png", MAX_FILE_SIZE);
		expect(validateFile(exact)).toBeNull();
	});
});

describe("OrgImageUpload", () => {
	it("renders skeleton while loading", () => {
		mockUseOrganization.mockReturnValue({
			organization: null,
			membership: null,
			isLoaded: false,
		});
		renderComponent();
		expect(screen.queryByText("Organization image")).not.toBeInTheDocument();
	});

	it("renders nothing when no organization", () => {
		mockUseOrganization.mockReturnValue({
			organization: null,
			membership: null,
			isLoaded: true,
		});
		const { container } = renderComponent();
		expect(container.innerHTML).toBe("");
	});

	it("shows upload button for admins", () => {
		mockUseOrganization.mockReturnValue({
			organization: makeOrg(),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();
		expect(
			screen.getByRole("button", { name: /upload image/i }),
		).toBeInTheDocument();
	});

	it("hides upload controls for non-admins", () => {
		mockUseOrganization.mockReturnValue({
			organization: makeOrg(),
			membership: { role: "org:member" },
			isLoaded: true,
		});
		renderComponent();
		expect(screen.getAllByText("Organization image").length).toBeGreaterThan(0);
		expect(
			screen.queryByRole("button", { name: /upload image/i }),
		).not.toBeInTheDocument();
	});

	it("shows remove button only when org has a custom image", () => {
		mockUseOrganization.mockReturnValue({
			organization: makeOrg({ hasImage: true }),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();
		expect(screen.getByRole("button", { name: /remove/i })).toBeInTheDocument();
	});

	it("hides remove button when org has no custom image", () => {
		mockUseOrganization.mockReturnValue({
			organization: makeOrg({ hasImage: false }),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();
		expect(
			screen.queryByRole("button", { name: /remove/i }),
		).not.toBeInTheDocument();
	});

	it("calls setLogo on valid file upload", async () => {
		const user = userEvent.setup();
		mockSetLogo.mockResolvedValue(makeOrg({ hasImage: true }));
		mockUseOrganization.mockReturnValue({
			organization: makeOrg(),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();

		const file = makeFile("logo.png", "image/png");
		const input = document.querySelector(
			'input[type="file"]',
		) as HTMLInputElement;
		await user.upload(input, file);

		await waitFor(() => {
			expect(mockSetLogo).toHaveBeenCalledWith({ file });
		});
	});

	it("shows validation error for unsupported file type", async () => {
		mockUseOrganization.mockReturnValue({
			organization: makeOrg(),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();

		const file = makeFile("doc.pdf", "application/pdf");
		const input = document.querySelector(
			'input[type="file"]',
		) as HTMLInputElement;

		// fireEvent bypasses the accept attribute filter that userEvent respects
		fireEvent.change(input, { target: { files: [file] } });

		await waitFor(() => {
			expect(
				screen.getByText("Please upload a JPEG, PNG, GIF, or WebP image."),
			).toBeInTheDocument();
		});
		expect(mockSetLogo).not.toHaveBeenCalled();
	});

	it("shows error when setLogo fails", async () => {
		const user = userEvent.setup();
		mockSetLogo.mockRejectedValue(new Error("Network error"));
		mockUseOrganization.mockReturnValue({
			organization: makeOrg(),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();

		const file = makeFile("logo.png", "image/png");
		const input = document.querySelector(
			'input[type="file"]',
		) as HTMLInputElement;
		await user.upload(input, file);

		await waitFor(() => {
			expect(screen.getByText("Network error")).toBeInTheDocument();
		});
	});

	it("calls setLogo with null on remove", async () => {
		const user = userEvent.setup();
		mockSetLogo.mockResolvedValue(makeOrg({ hasImage: false }));
		mockUseOrganization.mockReturnValue({
			organization: makeOrg({ hasImage: true }),
			membership: { role: "org:admin" },
			isLoaded: true,
		});
		renderComponent();

		await user.click(screen.getByRole("button", { name: /remove/i }));

		await waitFor(() => {
			expect(mockSetLogo).toHaveBeenCalledWith({ file: null });
		});
	});
});
