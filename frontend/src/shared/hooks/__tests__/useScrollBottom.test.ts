import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useScrollBottom } from "../useScrollBottom";

// Мокаем requestAnimationFrame
const mockRAF = vi.fn((cb: FrameRequestCallback) => {
  setTimeout(cb, 16);
  return 1;
});

const mockCancelRAF = vi.fn();

describe("useScrollBottom", () => {
  beforeEach(() => {
    global.requestAnimationFrame = mockRAF;
    global.cancelAnimationFrame = mockCancelRAF;
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it("should return contentRef", () => {
    const { result } = renderHook(() => useScrollBottom([1, "test"]));

    expect(result.current.contentRef).toBeDefined();
    expect(result.current.contentRef.current).toBeNull();
  });

  it("should trigger scroll when dependencies change", () => {
    const { rerender } = renderHook(
      ({ deps }) => useScrollBottom(deps),
      {
        initialProps: { deps: [1, "test"] },
      }
    );

    expect(mockRAF).toHaveBeenCalled();

    // Изменяем зависимости
    rerender({ deps: [2, "test2"] });

    // requestAnimationFrame должен быть вызван снова
    expect(mockRAF).toHaveBeenCalledTimes(2);
  });

  it("should handle empty dependencies array", () => {
    const { result } = renderHook(() => useScrollBottom([]));

    expect(result.current.contentRef).toBeDefined();
  });
});

