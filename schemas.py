
from pydantic import BaseModel, Field
from typing import List


class Education(BaseModel):
    degree: str = "Not provided"
    institution: str = "Not provided"
    graduation_year: str = "Not provided"


class Experience(BaseModel):
    job_title: str = "Not provided"
    company: str = "Not provided"
    duration: str = "Not provided"
    description: str = "Not provided"


class ResumeAnalysis(BaseModel):
    name: str = "Not provided"
    email: str = "Not provided"
    phone: str = "Not provided"

    summary: str = "Not provided"

    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)

    missing_fields: List[str] = Field(default_factory=list)
    completeness_score: int = Field(default=0, ge=0, le=100)
