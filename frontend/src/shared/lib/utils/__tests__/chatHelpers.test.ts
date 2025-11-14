import { describe, it, expect } from "vitest";
import { getChatIcon, getChatInitial } from "../chatHelpers";

describe("chatHelpers", () => {
  describe("getChatIcon", () => {
    it("should return a color class based on chat ID", () => {
      const colors = [
        "bg-blue-500",
        "bg-purple-500",
        "bg-green-500",
        "bg-orange-500",
        "bg-pink-500",
        "bg-indigo-500",
      ];

      // Тестируем несколько ID
      expect(colors).toContain(getChatIcon("0"));
      expect(colors).toContain(getChatIcon("1"));
      expect(colors).toContain(getChatIcon("5"));
      expect(colors).toContain(getChatIcon("10"));
    });

    it("should cycle through colors correctly", () => {
      const color0 = getChatIcon("0");
      const color6 = getChatIcon("6"); // 6 % 6 = 0
      expect(color0).toBe(color6);
    });

    it("should handle string IDs", () => {
      const result = getChatIcon("123");
      expect(result).toMatch(/^bg-\w+-\d+$/);
    });
  });

  describe("getChatInitial", () => {
    it("should return first letter in uppercase", () => {
      expect(getChatInitial("hello")).toBe("H");
      expect(getChatInitial("world")).toBe("W");
      expect(getChatInitial("test")).toBe("T");
    });

    it("should handle already uppercase letters", () => {
      expect(getChatInitial("Hello")).toBe("H");
      expect(getChatInitial("WORLD")).toBe("W");
    });

    it("should handle single character", () => {
      expect(getChatInitial("a")).toBe("A");
      expect(getChatInitial("Z")).toBe("Z");
    });

    it("should handle empty string", () => {
      expect(getChatInitial("")).toBe("");
    });
  });
});

