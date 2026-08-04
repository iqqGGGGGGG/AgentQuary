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


class UserProfileResponse(BaseModel):
    openid: str
    nickname: str
    avatar_url: str | None = None
    created_at: str


class UserProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=512)


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
