import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";
import { MessageList } from "../messageList";
import type { MessageData } from "@/shared/types/message";

vi.mock("@/shared/hooks/useScrollBottom", () => ({
  useScrollBottom: () => ({
    contentRef: { current: null },
  }),
}));

vi.mock("../message", () => ({
  Message: ({ content, isUser }: { content: string; isUser: boolean }) => (
    <div data-testid={`message-${isUser ? "user" : "assistant"}`}>
      {content}
    </div>
  ),
}));

vi.mock("../chatEmptyState", () => ({
  ChatEmptyState: ({ isCompact }: { isCompact?: boolean }) => (
    <div data-testid="chat-empty-state" data-compact={isCompact}>
      Empty State
    </div>
  ),
}));

describe("MessageList", () => {
  const mockMessages: MessageData[] = [
    {
      id: "1",
      content: "Hello",
      isUser: true,
      tag: "general",
    },
    {
      id: "2",
      content: "Hi there!",
      isUser: false,
      tag: "general",
    },
  ];

  it("should render empty state when no messages", () => {
    const { getByTestId } = render(<MessageList messages={[]} />);
    expect(getByTestId("chat-empty-state")).toBeInTheDocument();
  });

  it("should render messages when provided", () => {
    const { getByText } = render(<MessageList messages={mockMessages} />);
    expect(getByText("Hello")).toBeInTheDocument();
    expect(getByText("Hi there!")).toBeInTheDocument();
  });

  it("should render user and assistant messages correctly", () => {
    const { getByTestId } = render(<MessageList messages={mockMessages} />);
    expect(getByTestId("message-user")).toBeInTheDocument();
    expect(getByTestId("message-assistant")).toBeInTheDocument();
  });

  it("should pass isCompact prop to empty state", () => {
    const { getByTestId } = render(<MessageList messages={[]} isCompact={true} />);
    const emptyState = getByTestId("chat-empty-state");
    expect(emptyState).toHaveAttribute("data-compact", "true");
  });

  it("should handle isLoading prop", () => {
    const { rerender, getByText } = render(
      <MessageList messages={mockMessages} isLoading={false} />
    );
    expect(getByText("Hello")).toBeInTheDocument();

    rerender(<MessageList messages={mockMessages} isLoading={true} />);
    expect(getByText("Hello")).toBeInTheDocument();
  });

  it("should render all messages in order", () => {
    const manyMessages: MessageData[] = Array.from({ length: 5 }, (_, i) => ({
      id: `msg-${i}`,
      content: `Message ${i}`,
      isUser: i % 2 === 0,
      tag: "general",
    }));

    const { getByText } = render(<MessageList messages={manyMessages} />);

    manyMessages.forEach((msg) => {
      expect(getByText(msg.content)).toBeInTheDocument();
    });
  });
});
