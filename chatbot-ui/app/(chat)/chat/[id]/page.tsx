import { cookies } from "next/headers";
import { Chat } from "@/components/chat";
import { DEFAULT_MODEL_NAME, models } from "@/lib/ai/models";
import { apiClient } from "@/lib/api";
import type { Message } from "ai";

export default async function Page(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;

  const cookieStore = await cookies();
  const modelIdFromCookie = cookieStore.get("model-id")?.value;
  const selectedModelId =
    models.find((model) => model.id === modelIdFromCookie)?.id || DEFAULT_MODEL_NAME;

  let initialMessages: Message[] = [];
  try {
    const chats = await apiClient.getMessages(id);
    for (const chat of chats) {
      initialMessages.push({
        id: chat.id,
        role: chat.role,
        content: chat.content,
        createdAt: chat.createdAt,
      });
    }
  } catch (error) {
    return new Response("Failed to get chats", { status: 500 });
  }

  return (
    <Chat
      id={id}
      initialMessages={initialMessages}
      selectedModelId={selectedModelId}
      selectedVisibilityType="public"
      isReadonly={false}
    />
  );
}
