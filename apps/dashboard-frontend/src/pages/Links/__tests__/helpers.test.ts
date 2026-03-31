import type { Link } from "@/lib/api";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getLinkStatus, getRelativeTime } from "../helpers";

function makeLink(overrides: Partial<Link> = {}): Link {
	return {
		id: "1",
		org_id: "org1",
		short_code: "abc",
		target_url: "https://example.com",
		title: "Test",
		click_count: 0,
		is_active: true,
		created_by: null,
		created_at: "2025-01-01T00:00:00Z",
		expires_at: null,
		...overrides,
	};
}

describe("getRelativeTime", () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2025-06-15T12:00:00Z"));
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it.each([
		["2025-06-15T11:59:30Z", "just now", "less than 1 minute ago"],
		["2025-06-15T11:55:00Z", "5m ago", "minutes ago"],
		["2025-06-15T09:00:00Z", "3h ago", "hours ago"],
		["2025-06-13T12:00:00Z", "2d ago", "days ago"],
		["2025-05-25T12:00:00Z", "3w ago", "weeks ago"],
		["2025-06-15T11:00:00Z", "1h ago", "exactly 60 minutes"],
		["2025-06-14T12:00:00Z", "1d ago", "exactly 24 hours"],
		["2025-06-08T12:00:00Z", "1w ago", "exactly 7 days"],
	])("returns '%s' for %s", (input, expected) => {
		expect(getRelativeTime(input)).toBe(expected);
	});

	it("returns locale date for 28+ days ago", () => {
		const result = getRelativeTime("2025-05-01T12:00:00Z");
		expect(result).not.toContain("w ago");
		expect(result).toBeTruthy();
	});
});

describe("getLinkStatus", () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2025-06-15T12:00:00Z"));
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it.each<[Partial<Link>, { label: string; variant: string }, string]>([
		[
			{ is_active: true, expires_at: null },
			{ label: "Active", variant: "success" },
			"active link with no expiry",
		],
		[
			{ is_active: true, expires_at: "2025-12-31T00:00:00Z" },
			{ label: "Active", variant: "success" },
			"active link with future expiry",
		],
		[
			{ is_active: false },
			{ label: "Inactive", variant: "secondary" },
			"inactive link",
		],
		[
			{ is_active: true, expires_at: "2025-01-01T00:00:00Z" },
			{ label: "Expired", variant: "warning" },
			"active link with past expiry",
		],
		[
			{ is_active: false, expires_at: "2025-01-01T00:00:00Z" },
			{ label: "Inactive", variant: "secondary" },
			"inactive takes precedence over expired",
		],
	])("returns correct status for %s (%s)", (overrides, expected) => {
		expect(getLinkStatus(makeLink(overrides))).toEqual(expected);
	});
});
