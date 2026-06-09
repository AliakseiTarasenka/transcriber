"use client";

import { useCallback, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import { streamSummary } from "@/services/transcriberApi";
import type { ChatMessage, ChatSession, MessageMeta } from "@/types/chat";
import type { SummarizeRequest } from "@/types/api";

export function useChatSession() {
  const [session, setSession] = useState<ChatSession>({
    messages: [],
    isStreaming: false,
    currentMessageId: null,
  });

  const addUserMessage = useCallback((content: string) => {
    const message: ChatMessage = {
      id: uuidv4(),
      role: "user",
      content,
      timestamp: new Date(),
      status: "done",
    };

    setSession((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));

    return message.id;
  }, []);

  const addAssistantMessage = useCallback(() => {
    const message: ChatMessage = {
      id: uuidv4(),
      role: "assistant",
      content: "",
      timestamp: new Date(),
      status: "sending",
    };

    setSession((prev) => ({
      ...prev,
      messages: [...prev.messages, message],
      currentMessageId: message.id,
    }));

    return message.id;
  }, []);

  const updateMessage = useCallback((id: string, updates: Partial<ChatMessage>) => {
    setSession((prev) => ({
      ...prev,
      messages: prev.messages.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg)),
    }));
  }, []);

  const appendToMessage = useCallback((id: string, text: string) => {
    setSession((prev) => ({
      ...prev,
      messages: prev.messages.map((msg) =>
        msg.id === id ? { ...msg, content: msg.content + text } : msg
      ),
    }));
  }, []);

  const startStreaming = useCallback(
    async (request: SummarizeRequest) => {
      // Add user message
      const userMessage = `Summarize this video: ${request.url}\n\n${request.prompt || ""}`;
      addUserMessage(userMessage);

      // Add assistant message (empty, will be filled by stream)
      const assistantId = addAssistantMessage();

      setSession((prev) => ({ ...prev, isStreaming: true }));

      const abortController = new AbortController();

      try {
        await streamSummary(
          request,
          {
            onLoading: (message) => {
              updateMessage(assistantId, {
                content: `⏳ ${message}`,
                status: "streaming",
              });
            },
            onMeta: (meta) => {
              const messageMeta: MessageMeta = {
                transcriptChars: meta.chars,
                originalChars: meta.original_chars,
                language: meta.lang,
                segments: meta.segments,
                truncated: meta.truncated,
              };
              updateMessage(assistantId, {
                content: "", // Clear loading message
                meta: messageMeta,
                status: "streaming",
              });
            },
            onText: (text) => {
              appendToMessage(assistantId, text);
            },
            onDone: () => {
              updateMessage(assistantId, { status: "done" });
              setSession((prev) => ({
                ...prev,
                isStreaming: false,
                currentMessageId: null,
              }));
            },
            onError: (error) => {
              updateMessage(assistantId, {
                status: "error",
                error,
                content: "", // Clear any partial content
              });
              setSession((prev) => ({
                ...prev,
                isStreaming: false,
                currentMessageId: null,
              }));
            },
          },
          abortController.signal
        );
      } catch (error) {
        updateMessage(assistantId, {
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        });
        setSession((prev) => ({
          ...prev,
          isStreaming: false,
          currentMessageId: null,
        }));
      }

      return () => abortController.abort();
    },
    [addUserMessage, addAssistantMessage, updateMessage, appendToMessage]
  );

  const cancel = useCallback(() => {
    // The abort happens in the startStreaming closure
    // Just update UI state
    setSession((prev) => ({
      ...prev,
      isStreaming: false,
      currentMessageId: null,
    }));
  }, []);

  const clearHistory = useCallback(() => {
    setSession({
      messages: [],
      isStreaming: false,
      currentMessageId: null,
    });
  }, []);

  return {
    session,
    startStreaming,
    cancel,
    clearHistory,
  };
}
