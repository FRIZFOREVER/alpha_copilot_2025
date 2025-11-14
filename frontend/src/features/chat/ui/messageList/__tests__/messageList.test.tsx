import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageList, MessageData } from "../messageList";

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
    render(<MessageList messages={[]} />);
    expect(screen.getByTestId("chat-empty-state")).toBeInTheDocument();
  });

  it("should render messages when provided", () => {
    render(<MessageList messages={mockMessages} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
  });

  it("should render user and assistant messages correctly", () => {
    render(<MessageList messages={mockMessages} />);
    expect(screen.getByTestId("message-user")).toBeInTheDocument();
    expect(screen.getByTestId("message-assistant")).toBeInTheDocument();
  });

  it("should pass isCompact prop to empty state", () => {
    render(<MessageList messages={[]} isCompact={true} />);
    const emptyState = screen.getByTestId("chat-empty-state");
    expect(emptyState).toHaveAttribute("data-compact", "true");
  });

  it("should handle isLoading prop", () => {
    const { rerender } = render(
      <MessageList messages={mockMessages} isLoading={false} />
    );
    expect(screen.getByText("Hello")).toBeInTheDocument();

    rerender(<MessageList messages={mockMessages} isLoading={true} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("should render all messages in order", () => {
    const manyMessages: MessageData[] = Array.from({ length: 5 }, (_, i) => ({
      id: `msg-${i}`,
      content: `Message ${i}`,
      isUser: i % 2 === 0,
      tag: "general",
    }));

    render(<MessageList messages={manyMessages} />);

    manyMessages.forEach((msg) => {
      expect(screen.getByText(msg.content)).toBeInTheDocument();
    });
  });
});
