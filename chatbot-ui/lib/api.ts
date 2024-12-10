import type { Message } from "ai";
import { Configuration, ChatApi, ChatCompletionRequest } from "./generated";

export class APIClient {
    private chatApi: ChatApi;

    constructor(basePath?: string) {
        const configuration = new Configuration({
            basePath,
        });

        this.chatApi = new ChatApi(configuration);
    }

    async createChatCompletion(request: ChatCompletionRequest) {
        try {
            const response =
                await this.chatApi.createChatCompletionV1ChatCompletionsPost(request);
            return response.data;
        } catch (error) {
            console.error("Failed to create chat completion:", error);
            throw error;
        }
    }

    async getChats() {
        try {
            const response = await this.chatApi.getChatsV1ChatGet();
            return response.data;
        } catch (error) {
            console.error("Failed to get chats:", error);
            throw error;
        }
    }

    async getChat(chatId: string) {
        try {
            const response = await this.chatApi.getChatV1ChatChatIdGet(chatId);
            return response.data;
        } catch (error) {
            return null;
        }
    }

    async deleteChat(chatId: string) {
        try {
            await this.chatApi.deleteChatV1ChatChatIdDelete(chatId);
        } catch (error) {
            console.error("Failed to delete chat:", error);
            throw error;
        }
    }

    async getMessages(chatId: string) {
        try {
            const response =
                await this.chatApi.getMessagesV1ChatChatIdMessagesGet(chatId);
            return response.data;
        } catch (error) {
            console.error("Failed to get messages:", error);
            throw error;
        }
    }

    async createMessage(chatId: string, message: Message) {
        try {
            const response = await this.chatApi.createMessageV1ChatChatIdMessagesPost(
                chatId,
                {
                    role: message.role,
                    content: message.content,
                },
            );
            return response.data;
        } catch (error) {
            console.error("Failed to create message:", error);
            throw error;
        }
    }
}

// 创建一个默认的API客户端实例
export const apiClient = new APIClient("http://127.0.0.1:8000");
