import { describe, it, expect } from "vitest";
import { formatTime } from "../timeHelpers";

describe("timeHelpers", () => {
  describe("formatTime", () => {
    it("should format seconds correctly", () => {
      expect(formatTime(0)).toBe("00:00");
      expect(formatTime(30)).toBe("00:30");
      expect(formatTime(60)).toBe("01:00");
      expect(formatTime(90)).toBe("01:30");
      expect(formatTime(125)).toBe("02:05");
    });

    it("should handle large values", () => {
      expect(formatTime(3600)).toBe("60:00");
      expect(formatTime(3661)).toBe("61:01");
    });

    it("should pad minutes and seconds with zeros", () => {
      expect(formatTime(5)).toBe("00:05");
      expect(formatTime(65)).toBe("01:05");
      expect(formatTime(605)).toBe("10:05");
    });

    it("should handle edge cases", () => {
      expect(formatTime(59)).toBe("00:59");
      expect(formatTime(119)).toBe("01:59");
      expect(formatTime(3599)).toBe("59:59");
    });
  });
});

