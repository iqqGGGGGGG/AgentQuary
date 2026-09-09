from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Question(BaseModel):
    id: int
    type: str = Field(pattern="^(single_choice|true_false)$")
    question: str
    options: list[str]
    answer: int = Field(ge=0)
    explanation: str

    @model_validator(mode="after")
    def validate_options_and_answer(self):
        expected = 4 if self.type == "single_choice" else 2
        if len(self.options) != expected:
            raise ValueError(f"{self.type} 必须包含 {expected} 个选项")
        if self.answer >= len(self.options):
            raise ValueError("answer 超出选项范围")
        return self


class GenerateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=12_000)
    question_count: int = Field(default=10, ge=5, le=20)
    excluded_questions: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str):
        if not value.strip():
            raise ValueError("content 不能为空")
        return value


class GenerateResponse(BaseModel):
    session_id: str
    topic: str
    questions: list[Question]
    search_used: bool = False
    needs_clarification: bool = False
    domain_options: list[str] = Field(default_factory=list)


class ReportRequest(BaseModel):
    topic: str
    questions: list[dict]
    user_answers: list[int]
    duration_seconds: int = Field(ge=0)


class ReportResponse(BaseModel):
    accuracy: float = Field(ge=0, le=1)
    correct_count: int = Field(ge=0)
    total_count: int = Field(ge=0)
    mastered: list[str]
    weak: list[str]
    summary: str
    encouragement: str


class ExampleTopic(BaseModel):
    id: int
    title: str
    category: str
    description: str


class QuizOutputSchema(BaseModel):
    topic: str
    questions: list[Question] = Field(min_length=1, max_length=20)


class ReportOutputSchema(BaseModel):
    summary: str = Field(min_length=20, max_length=200)
    encouragement: str = Field(min_length=5, max_length=50)


# ── User Schemas ──

class LoginRequest(BaseModel):
    code: str = Field(min_length=1)


class LoginResponse(BaseModel):
    openid: str
    nickname: str
    avatar_url: str | None = None
    is_new: bool = False
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    openid: str
    nickname: str
    avatar_url: str | None = None
    created_at: str


class UserProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=512)

    @field_validator("nickname")
    @classmethod
    def nickname_must_not_be_blank(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("nickname 不能为空")
        return value.strip() if value is not None else None


class AvatarUploadRequest(BaseModel):
    data: str = Field(min_length=1, max_length=3_000_000)
    file_type: Literal["png", "jpg", "jpeg", "webp"]


class UserStatsResponse(BaseModel):
    total_quizzes: int = 0
    total_questions: int = 0
    avg_accuracy: float = 0.0
    best_streak: int = 0
    learning_days: int = 0


class HistorySaveRequest(BaseModel):
    session_id: str
    topic: str
    accuracy: float = Field(ge=0, le=1)
    total_questions: int = Field(ge=0)
    correct_count: int = Field(ge=0)
    duration_seconds: int = Field(ge=0)
    questions: list[dict] | None = None
    user_answers: list[dict] | None = None
    summary: str | None = None


class HistoryItemResponse(BaseModel):
    id: int
    session_id: str
    topic: str
    accuracy: float
    total_questions: int
    correct_count: int
    duration_seconds: int
    summary: str | None = None
    created_at: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItemResponse]
    total: int


# ── Level Schemas ──

class LevelInfoResponse(BaseModel):
    xp: int
    level: int
    level_name: str
    current_level_xp: int
    next_level_xp: int
    progress: float


# ── Calendar Schemas ──

class CalendarDay(BaseModel):
    date: str
    count: int
    high: bool = False


class LearningCalendarResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarDay]
    current_streak: int


# ── Achievement Schemas ──

class AchievementResponse(BaseModel):
    id: int
    key: str
    name: str
    description: str
    icon: str
    condition_type: str
    condition_value: int
    sort_order: int
    unlocked: bool = False
    unlocked_at: str | None = None


class AchievementListResponse(BaseModel):
    items: list[AchievementResponse]
    unlocked_count: int
    total_count: int


# ── Wrong Question Schemas ──

class WrongQuestionItem(BaseModel):
    record_id: int
    question_id: int
    topic: str
    question: str
    your_answer: str
    correct_answer: str
    explanation: str
    created_at: str


class WrongQuestionListResponse(BaseModel):
    items: list[WrongQuestionItem]
    total: int
    topic_count: int


# ── Trends Schemas ──

class TrendDay(BaseModel):
    date: str
    count: int
    accuracy: float = 0.0


class TrendsResponse(BaseModel):
    days: list[TrendDay]


# ── Domain Schemas ──

class DomainStat(BaseModel):
    domain: str
    icon: str
    accuracy: float
    count: int


class DomainsResponse(BaseModel):
    domains: list[DomainStat]


# ── Preferences Schemas ──

class PreferencesUpdate(BaseModel):
    preferences: list[str] = Field(max_length=20)


class PreferencesResponse(BaseModel):
    preferences: list[str]


# ── Goal Schemas ──

class GoalUpdate(BaseModel):
    daily_goal: int = Field(ge=1, le=10)


class GoalResponse(BaseModel):
    daily_goal: int
    today_count: int


# ── Extended History Save Response ──

class HistorySaveResponse(BaseModel):
    id: int
    session_id: str
    topic: str
    accuracy: float
    total_questions: int
    correct_count: int
    duration_seconds: int
    summary: str | None = None
    created_at: str
    xp_earned: int = 0
    new_level: int | None = None
    new_achievements: list[AchievementResponse] = []


# ── Document Schemas ──

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    text_length: int
    created_at: str
    text_preview: str | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
