from pydantic import BaseModel, ConfigDict
from typing import Literal

class PodcastPlot(BaseModel):
    model_config = ConfigDict(extra='allow')
    topic: str
    tone: str
    level: str

class PodcastChapter(BaseModel):
    model_config = ConfigDict(extra='allow')
    chapter_title: str
    chapter_summary: str
    include: str
    avoid: str
    length: str
    backreferences: str

class PodcastConfig(BaseModel):
    model_config = ConfigDict(extra='allow')
    project_title: str
    plot: PodcastPlot
    chapters: list[PodcastChapter]
    system_prompt: str

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str