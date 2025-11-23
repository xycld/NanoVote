from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional

DurationOption = Literal["3m", "30m", "1h", "6h", "1d", "3d", "7d", "10d"]


class PollOption(BaseModel):
    id: int
    text: str
    votes: int = 0


class CreatePollRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="投票标题")
    options: List[str] = Field(..., min_length=2, max_length=20, description="选项列表")
    duration: DurationOption = Field(default="1d", description="持续时长")

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        # 去除空白并限制长度
        cleaned = [opt.strip()[:50] for opt in v if opt.strip()]

        if len(cleaned) < 2:
            raise ValueError("至少需要2个有效选项")

        if len(cleaned) != len(set(cleaned)):
            raise ValueError("选项不能重复")

        return cleaned

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空")
        return v


class CreatePollResponse(BaseModel):
    poll_id: str
    url: str
    expires_at: int


class PollResponse(BaseModel):
    poll_id: str
    title: str
    options: List[PollOption]
    total_votes: int
    expires_at: int
    has_voted: bool = False
    voted_for: Optional[int] = None


class VoteRequest(BaseModel):
    option_id: int = Field(..., ge=1, description="选项ID")


class VoteResponse(BaseModel):
    success: bool
    options: List[PollOption]
    total_votes: int
