from pydantic import BaseModel, Field
from typing import List, Optional, Union


class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant', or 'system').")
    content: str = Field(..., description="The content of the message.")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="The model to use for generating completions (e.g., 'gpt-3.5-turbo').")
    messages: List[Message] = Field(..., description="A list of messages describing the conversation history.")
    max_tokens: Optional[int] = Field(None, description="The maximum number of tokens to generate in the response.")
    temperature: Optional[float] = Field(
        1.0, ge=0, le=2,
        description="Sampling temperature. Higher values make output more random; lower values make it more deterministic."
    )
    top_p: Optional[float] = Field(
        1.0, ge=0, le=1,
        description="Nucleus sampling probability. The model considers results of tokens with top_p probability mass."
    )
    stream: Optional[bool] = Field(
        False, description="Whether to return a stream of data for the response. Defaults to False."
    )
    stop: Optional[Union[str, List[str]]] = Field(
        None, description="Optional stop sequences where the model will stop generating further tokens."
    )
    presence_penalty: Optional[float] = Field(
        0.0, ge=-2, le=2, description="Penalty for new tokens based on whether they appear in the text so far."
    )
    frequency_penalty: Optional[float] = Field(
        0.0, ge=-2, le=2, description="Penalty for new tokens based on their frequency in the text so far."
    )
    user: Optional[str] = Field(
        None, description="Unique identifier for the end-user. This helps OpenAI monitor and detect abuse."
    )
