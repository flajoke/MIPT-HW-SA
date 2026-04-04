from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    message: str = Field(min_length=1)
