from pydantic import BaseModel, Field


class GenerateQuestionsRequest(BaseModel):
    resume_text: str
    difficulty: str
    num_questions: int = Field(default=5, ge=1, le=20)


class GenerateQuestionsResponse(BaseModel):
    questions: list[str]


class EvaluationItem(BaseModel):
    question: str
    answer: str


class EvaluateRequest(BaseModel):
    difficulty: str
    items: list[EvaluationItem] = Field(default_factory=list, min_length=1)


class PerQuestionFeedback(BaseModel):
    question_index: int = Field(ge=1)
    score: int = Field(ge=0, le=100)
    feedback: str


class EvaluateResponse(BaseModel):
    total_score: int = Field(ge=0, le=100)
    overall_feedback: str
    per_question: list[PerQuestionFeedback]
