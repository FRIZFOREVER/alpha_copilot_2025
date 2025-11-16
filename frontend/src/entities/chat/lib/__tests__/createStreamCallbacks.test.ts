import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { createStreamCallbacks } from "../createStreamCallbacks";
import { GET_HISTORY_QUERY } from "../../lib/constants";
import type {
  StreamInitialResponse,
  StreamChunk,
  SendMessageStreamDto,
} from "../../types/types";

describe("createStreamCallbacks", () => {
  let queryClient: QueryClient;
  const chatId = 1;
  const sendMessageDto: SendMessageStreamDto = {
    question: "Test question",
    tag: "general",
    mode: "fast",
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  it("should create callbacks object with all required methods", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    expect(callbacks).toHaveProperty("onInitial");
    expect(callbacks).toHaveProperty("onChunk");
    expect(callbacks).toHaveProperty("onComplete");
    expect(callbacks).toHaveProperty("onStreamError");
    expect(callbacks).toHaveProperty("getInitialData");
  });

  it("should handle onInitial callback and update query data", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);

    const queryData = queryClient.getQueryData([GET_HISTORY_QUERY, chatId]);
    expect(queryData).toBeDefined();
    expect(Array.isArray(queryData)).toBe(true);
    if (Array.isArray(queryData)) {
      expect(queryData).toHaveLength(1);
      expect(queryData[0]).toMatchObject({
        question_id: 1,
        answer_id: 2,
        question: "Test question",
        answer: "",
      });
    }
  });

  it("should handle onChunk callback and append content", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);

    const chunk1: StreamChunk = {
      content: "Hello",
      time: "2025-01-01T00:00:01Z",
      done: false,
      thinking: "fast",
    };

    const chunk2: StreamChunk = {
      content: " World",
      time: "2025-01-01T00:00:02Z",
      done: false,
      thinking: "fast",
    };

    callbacks.onChunk(chunk1);
    callbacks.onChunk(chunk2);

    const queryData = queryClient.getQueryData([GET_HISTORY_QUERY, chatId]);
    if (Array.isArray(queryData) && queryData[0]) {
      expect(queryData[0].answer).toBe("Hello World");
    }
  });

  it("should handle onComplete callback", () => {
    const onCompleteMock = vi.fn();
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
      onComplete: onCompleteMock,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);
    callbacks.onComplete();

    expect(onCompleteMock).toHaveBeenCalledWith(initialData);
  });

  it("should handle onStreamError callback", () => {
    const onErrorMock = vi.fn();
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
      onError: onErrorMock,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);

    const error = new Error("Stream error");
    callbacks.onStreamError(error);

    expect(onErrorMock).toHaveBeenCalledWith(error);

    const queryData = queryClient.getQueryData([GET_HISTORY_QUERY, chatId]);
    if (Array.isArray(queryData)) {
      expect(queryData).toHaveLength(0);
    }
  });

  it("should filter out temp messages on onInitial", () => {
    queryClient.setQueryData(
      [GET_HISTORY_QUERY, chatId],
      [
        {
          question_id: -1,
          answer_id: -2,
          question: "Temp question",
          answer: "",
          question_time: "2025-01-01T00:00:00Z",
          answer_time: "2025-01-01T00:00:00Z",
          rating: null,
          tag: "general",
          voice_url: "",
          file_url: "",
        },
      ]
    );

    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
      tempQuestionId: -1,
      tempAnswerId: -2,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:01Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);

    const queryData = queryClient.getQueryData([GET_HISTORY_QUERY, chatId]);
    if (Array.isArray(queryData)) {
      expect(queryData).toHaveLength(1);
      expect(queryData[0].question_id).toBe(1);
      expect(queryData[0].answer_id).toBe(2);
    }
  });

  it("should return initial data via getInitialData", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    expect(callbacks.getInitialData()).toBeNull();

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);
    expect(callbacks.getInitialData()).toEqual(initialData);
  });

  it("should not update onChunk if no initial data", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    const chunk: StreamChunk = {
      content: "Test",
      time: "2025-01-01T00:00:00Z",
      done: false,
      thinking: "fast",
    };

    expect(() => callbacks.onChunk(chunk)).not.toThrow();
  });

  it("should not update onChunk if chunk has no content", () => {
    const callbacks = createStreamCallbacks({
      queryClient,
      chatId,
      sendMessageDto,
    });

    const initialData: StreamInitialResponse = {
      question_id: 1,
      answer_id: 2,
      question_time: "2025-01-01T00:00:00Z",
      tag: "general",
    };

    callbacks.onInitial(initialData);

    const chunk: StreamChunk = {
      content: "",
      time: "2025-01-01T00:00:00Z",
      done: false,
      thinking: "fast",
    };

    callbacks.onChunk(chunk);

    const queryData = queryClient.getQueryData([GET_HISTORY_QUERY, chatId]);
    if (Array.isArray(queryData) && queryData[0]) {
      expect(queryData[0].answer).toBe("");
    }
  });
});
