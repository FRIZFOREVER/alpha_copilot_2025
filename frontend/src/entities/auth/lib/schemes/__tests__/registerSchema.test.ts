import { describe, it, expect } from "vitest";
import { RegisterSchema } from "../registerSchema";

describe("RegisterSchema", () => {
  describe("valid inputs", () => {
    it("should validate correct registration data", () => {
      const result = RegisterSchema.safeParse({
        login: "test@example.com",
        username: "John Doe",
        password: "password123",
      });

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.login).toBe("test@example.com");
        expect(result.data.username).toBe("John Doe");
        expect(result.data.password).toBe("password123");
      }
    });

    it("should trim whitespace from inputs", () => {
      const result = RegisterSchema.safeParse({
        login: "  test@example.com  ",
        username: "  John Doe  ",
        password: "  password123  ",
      });

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.login).toBe("test@example.com");
        expect(result.data.username).toBe("John Doe");
        expect(result.data.password).toBe("password123");
      }
    });
  });

  describe("invalid email", () => {
    it("should reject invalid email format", () => {
      const result = RegisterSchema.safeParse({
        login: "invalid-email",
        username: "John Doe",
        password: "password123",
      });

      expect(result.success).toBe(false);
    });

    it("should reject empty email", () => {
      const result = RegisterSchema.safeParse({
        login: "",
        username: "John Doe",
        password: "password123",
      });

      expect(result.success).toBe(false);
    });
  });

  describe("invalid username", () => {
    it("should reject empty username", () => {
      const result = RegisterSchema.safeParse({
        login: "test@example.com",
        username: "",
        password: "password123",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("обязательно");
      }
    });

    it("should reject username longer than 254 characters", () => {
      const longUsername = "a".repeat(255);
      const result = RegisterSchema.safeParse({
        login: "test@example.com",
        username: longUsername,
        password: "password123",
      });

      expect(result.success).toBe(false);
    });
  });

  describe("invalid password", () => {
    it("should reject password shorter than 8 characters", () => {
      const result = RegisterSchema.safeParse({
        login: "test@example.com",
        username: "John Doe",
        password: "short",
      });

      expect(result.success).toBe(false);
    });

    it("should reject empty password", () => {
      const result = RegisterSchema.safeParse({
        login: "test@example.com",
        username: "John Doe",
        password: "",
      });

      expect(result.success).toBe(false);
    });
  });
});

