import {
  type Message,
  StreamData,
  convertToCoreMessages,
  streamObject,
  streamText,
} from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";

import { customModel } from "@/lib/ai";
import { models } from "@/lib/ai/models";
import { systemPrompt } from "@/lib/ai/prompts";
import {
  generateUUID,
  getMostRecentUserMessage,
  sanitizeResponseMessages,
} from "@/lib/utils";

import { generateTitleFromUserMessage } from "../../actions";
import { apiClient } from "@/lib/api";

export const maxDuration = 60;

type AllowedTools =
  | "createDocument"
  | "updateDocument"
  | "requestSuggestions"
  | "getWeather";

const blocksTools: AllowedTools[] = [
  "createDocument",
  "updateDocument",
  "requestSuggestions",
];

const weatherTools: AllowedTools[] = ["getWeather"];

const allTools: AllowedTools[] = [...blocksTools, ...weatherTools];

const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY || "",
  baseURL: "http://127.0.0.1:8000/v1",
});

export async function POST(request: Request) {
  const {
    id,
    messages,
    modelId,
  }: { id: string; messages: Array<Message>; modelId: string } =
    await request.json();

  const model = models.find((model) => model.id === modelId);

  if (!model) {
    return new Response("Model not found", { status: 404 });
  }

  const coreMessages = convertToCoreMessages(messages);
  const userMessage = getMostRecentUserMessage(coreMessages);

  if (!userMessage) {
    return new Response("No user message found", { status: 400 });
  }

  const chat = await apiClient.getChat(id);

  // Save user message
  const userMessageId = generateUUID();
  await apiClient.createMessage(id, {
    id: userMessageId,
    role: "user",
    content: userMessage.content.toString(),
    createdAt: new Date(),
  });

  const streamingData = new StreamData();

  streamingData.append({
    type: "user-message-id",
    content: userMessageId,
  });

  const result = streamText({
    model: openai(model.apiIdentifier),
    system: systemPrompt,
    messages: coreMessages,
    onFinish: async ({ response }) => {
      const responseMessagesWithoutIncompleteToolCalls =
        sanitizeResponseMessages(response.messages);
      responseMessagesWithoutIncompleteToolCalls.forEach(
        (message) => {
          const messageId = generateUUID();

          if (message.role === 'assistant') {
            streamingData.appendMessageAnnotation({
              messageIdFromServer: messageId,
            });
          }
          console.log(message.role)
          console.log(message.content)
          apiClient.createMessage(id, {
            id: messageId,
            chatId: id,
            role: message.role,
            content: message.content[0].text,
            createdAt: new Date(),
          });
        });
      streamingData.close();
    },
    experimental_telemetry: {
      isEnabled: true,
      functionId: "stream-text",
    },
  });

  return result.toDataStreamResponse({
    data: streamingData,
  });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) {
    return new Response("Not Found", { status: 404 });
  }

  try {
    await apiClient.deleteChat(id);
    return new Response("Chat deleted", { status: 200 });
  } catch (error) {
    return new Response("An error occurred while processing your request", {
      status: 500,
    });
  }
}
