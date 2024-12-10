import { apiClient } from "@/lib/api";

export async function GET() {
  try {
    const chats = await apiClient.getChats();
    return new Response(JSON.stringify(chats), { status: 200 });
  } catch (error) {
    return new Response("Failed to get chats", { status: 500 });
  }
}
