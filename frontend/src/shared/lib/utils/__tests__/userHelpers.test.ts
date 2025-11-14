import { describe, it, expect } from "vitest";
import {
  getUserInitials,
  getDisplayName,
  capitalizeFirst,
} from "../userHelpers";

describe("userHelpers", () => {
  describe("getUserInitials", () => {
    it("should return first letter for single name", () => {
      expect(getUserInitials("John")).toBe("J");
      expect(getUserInitials("Иван")).toBe("И");
    });

    it("should return first and last initial for full name", () => {
      expect(getUserInitials("John Doe")).toBe("JD");
      expect(getUserInitials("Иван Петров")).toBe("ИП");
    });

    it("should handle multiple words correctly", () => {
      expect(getUserInitials("John Michael Doe")).toBe("JD");
      expect(getUserInitials("Иван Петрович Сидоров")).toBe("ИС");
    });

    it("should handle extra spaces", () => {
      expect(getUserInitials("  John  Doe  ")).toBe("JD");
      expect(getUserInitials("Иван   Петров")).toBe("ИП");
    });

    it("should return uppercase initials", () => {
      expect(getUserInitials("john doe")).toBe("JD");
      expect(getUserInitials("иван петров")).toBe("ИП");
    });

    it("should handle empty string", () => {
      expect(getUserInitials("")).toBe("");
    });
  });

  describe("getDisplayName", () => {
    it("should return name as is for single word", () => {
      expect(getDisplayName("John")).toBe("John");
      expect(getDisplayName("Иван")).toBe("Иван");
    });

    it("should return first and last name for two words", () => {
      expect(getDisplayName("John Doe")).toBe("John Doe");
      expect(getDisplayName("Иван Петров")).toBe("Иван Петров");
    });

    it("should swap first and last for three or more words", () => {
      expect(getDisplayName("Ivanov Ivan Petrovich")).toBe("Ivan Ivanov");
      expect(getDisplayName("Иванов Иван Петрович")).toBe("Иван Иванов");
    });

    it("should handle extra spaces", () => {
      expect(getDisplayName("  John  Doe  ")).toBe("John Doe");
      expect(getDisplayName("Иванов   Иван   Петрович")).toBe("Иван Иванов");
    });
  });

  describe("capitalizeFirst", () => {
    it("should capitalize first letter", () => {
      expect(capitalizeFirst("hello")).toBe("Hello");
      expect(capitalizeFirst("world")).toBe("World");
    });

    it("should handle already capitalized strings", () => {
      expect(capitalizeFirst("Hello")).toBe("Hello");
      expect(capitalizeFirst("WORLD")).toBe("WORLD");
    });

    it("should handle empty string", () => {
      expect(capitalizeFirst("")).toBe("");
    });

    it("should handle single character", () => {
      expect(capitalizeFirst("a")).toBe("A");
      expect(capitalizeFirst("A")).toBe("A");
    });

    it("should handle strings with numbers", () => {
      expect(capitalizeFirst("123abc")).toBe("123abc");
      expect(capitalizeFirst("abc123")).toBe("Abc123");
    });
  });
});

