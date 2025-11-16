import { describe, it, expect } from "vitest";
import { LoginSchema } from "../loginSchema";

describe("LoginSchema", () => {
  describe("valid inputs", () => {
    it("should validate correct email and password", () => {
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: "password123",
      });

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.login).toBe("test@example.com");
        expect(result.data.password).toBe("password123");
      }
    });

    it("should trim whitespace from inputs", () => {
      const result = LoginSchema.safeParse({
        login: "  test@example.com  ",
        password: "  password123  ",
      });

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.login).toBe("test@example.com");
        expect(result.data.password).toBe("password123");
      }
    });
  });

  describe("invalid email", () => {
    it("should reject invalid email format", () => {
      const result = LoginSchema.safeParse({
        login: "invalid-email",
        password: "password123",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("корректный email");
      }
    });

    it("should reject empty email", () => {
      const result = LoginSchema.safeParse({
        login: "",
        password: "password123",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("обязателен");
      }
    });

    it("should reject email longer than 254 characters", () => {
      const longEmail = "a".repeat(250) + "@example.com";
      const result = LoginSchema.safeParse({
        login: longEmail,
        password: "password123",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("254 символа");
      }
    });
  });

  describe("invalid password", () => {
    it("should reject password shorter than 8 characters", () => {
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: "short",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("8 символов");
      }
    });

    it("should reject empty password", () => {
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: "",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("обязателен");
      }
    });

    it("should reject password longer than 128 characters", () => {
      const longPassword = "a".repeat(129);
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: longPassword,
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toContain("128 символов");
      }
    });
  });

  describe("edge cases", () => {
    it("should accept password with exactly 8 characters", () => {
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: "12345678",
      });

      expect(result.success).toBe(true);
    });

    it("should accept password with exactly 128 characters", () => {
      const password = "a".repeat(128);
      const result = LoginSchema.safeParse({
        login: "test@example.com",
        password: password,
      });

      expect(result.success).toBe(true);
    });

    it("should accept email with exactly 254 characters", () => {
      const email = "a".repeat(244) + "@example.com";
      const result = LoginSchema.safeParse({
        login: email,
        password: "password123",
      });

      expect(result.success).toBe(true);
    });
  });
});
