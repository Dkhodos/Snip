import { describe, expect, it } from "vitest";
import { formatDate } from "../helpers";

describe("formatDate", () => {
	it("formats a date string as 'Mon D'", () => {
		expect(formatDate("2025-01-15")).toBe("Jan 15");
	});

	it("formats December correctly", () => {
		expect(formatDate("2025-12-01")).toBe("Dec 1");
	});

	it("formats a full ISO datetime string", () => {
		expect(formatDate("2025-06-03T14:30:00Z")).toBe("Jun 3");
	});

	it("does not pad single-digit days", () => {
		expect(formatDate("2025-03-05")).toBe("Mar 5");
	});

	it("handles all months", () => {
		const expected = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		];
		for (let i = 0; i < 12; i++) {
			const month = String(i + 1).padStart(2, "0");
			const result = formatDate(`2025-${month}-10`);
			expect(result).toBe(`${expected[i]} 10`);
		}
	});
});
