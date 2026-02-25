from pydantic import BaseModel


class CustomParameters(BaseModel):
    example: str
    isTrue: bool
