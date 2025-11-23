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
    allow_multiple: bool = Field(default=False, description="是否允许多选")
    min_selection: Optional[int] = Field(default=None, ge=1, description="最少选择数")
    max_selection: Optional[int] = Field(default=None, ge=1, description="最多选择数")

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

    @field_validator("max_selection")
    @classmethod
    def validate_max_selection(cls, v: Optional[int], info) -> Optional[int]:
        if v is not None and 'min_selection' in info.data:
            min_sel = info.data.get('min_selection')
            if min_sel is not None and v < min_sel:
                raise ValueError("最多选择数不能小于最少选择数")
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
    voted_for: Optional[int | List[int]] = None
    allow_multiple: bool = False
    min_selection: Optional[int] = None
    max_selection: Optional[int] = None


class VoteRequest(BaseModel):
    option_id: Optional[int] = Field(default=None, ge=1, description="选项ID（单选）")
    option_ids: Optional[List[int]] = Field(default=None, description="选项ID列表（多选）")

    @field_validator("option_ids")
    @classmethod
    def validate_option_ids(cls, v: Optional[List[int]], info) -> Optional[List[int]]:
        # 确保至少提供了 option_id 或 option_ids 之一
        option_id = info.data.get('option_id')
        if option_id is None and (v is None or len(v) == 0):
            raise ValueError("必须提供 option_id 或 option_ids")

        # 如果同时提供了两者，报错
        if option_id is not None and v is not None and len(v) > 0:
            raise ValueError("不能同时提供 option_id 和 option_ids")

        # 验证选项 ID 唯一性
        if v is not None and len(v) != len(set(v)):
            raise ValueError("选项ID不能重复")

        return v


class VoteResponse(BaseModel):
    success: bool
    options: List[PollOption]
    total_votes: int
