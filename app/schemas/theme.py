from pydantic import BaseModel


class ThemePublishResponse(BaseModel):
    theme_id: str
    status: str
