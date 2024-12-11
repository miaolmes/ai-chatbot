import type { Message } from "ai";
import { Configuration, ChatApi, ChatCompletionRequest, FilesApi } from "./generated";

export class APIClient {
    private chatApi: ChatApi;
    private filesApi: FilesApi

    constructor(basePath?: string) {
        const configuration = new Configuration({
            basePath,
        });

        this.chatApi = new ChatApi(configuration);
        this.filesApi = new FilesApi(configuration);
    }

    async createChatCompletion(request: ChatCompletionRequest) {
        try {
            const response =
                await this.chatApi.createChatCompletion(request);
            return response.data;
        } catch (error) {
            console.error("Failed to create chat completion:", error);
            throw error;
        }
    }

    async getChats() {
        try {
            const response = await this.chatApi.getChats();
            return response.data;
        } catch (error) {
            console.error("Failed to get chats:", error);
            throw error;
        }
    }

    async getChat(chatId: string) {
        try {
            const response = await this.chatApi.getChat(chatId);
            return response.data;
        } catch (error) {
            return null;
        }
    }

    async deleteChat(chatId: string) {
        try {
            await this.chatApi.deleteChat(chatId);
        } catch (error) {
            console.error("Failed to delete chat:", error);
            throw error;
        }
    }

    async getMessages(chatId: string) {
        try {
            const response =
                await this.chatApi.getMessages(chatId);
            return response.data;
        } catch (error) {
            console.error("Failed to get messages:", error);
            throw error;
        }
    }

    async createMessage(chatId: string, message: Message) {
        try {
            const response = await this.chatApi.createMessage(
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

    async uploadFile(chatId: string, file: File) {
        try {
            const response = await this.filesApi.uploadFile(
                chatId,
                file,
            );
            return response.data;
        } catch (error) {
            console.error("Failed to upload file:", error);
            throw error;
        }
    }
}

// 创建一个默认的API客户端实例
export const apiClient = new APIClient(process.env.CHATBOT_API_BASE);
