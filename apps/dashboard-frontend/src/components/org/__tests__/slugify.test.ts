import { describe, expect, it } from "vitest";
import { slugify } from "../slugify";

describe("slugify", () => {
	it.each([
		["Acme Corp", "acme-corp", "lowercases input"],
		["my org name", "my-org-name", "replaces spaces with hyphens"],
		["Hello! @World#", "hello-world", "removes special characters"],
		["a---b", "a-b", "collapses consecutive hyphens"],
		["-hello-", "hello", "strips leading and trailing hyphens"],
		["", "", "returns empty string for empty input"],
		["@#$%", "", "handles only special characters"],
		["team-42", "team-42", "preserves numbers"],
		[
			"My Team 123",
			"my-team-123",
			"handles mixed case with numbers and spaces",
		],
	])("%s → %s (%s)", (input, expected) => {
		expect(slugify(input)).toBe(expected);
	});
});
