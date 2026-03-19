"""FastAPI application for Doctorate Reader.

Endpoints:
  POST   /api/v1/profiles              — create researcher profile
  GET    /api/v1/profiles/{id}         — retrieve profile
  PUT    /api/v1/profiles/{id}         — update profile
  DELETE /api/v1/profiles/{id}         — delete profile
  POST   /api/v1/newsletters           — queue newsletter generation (returns job_id)
  GET    /api/v1/newsletters/{job_id}  — poll for result
  GET    /api/v1/health                — health check
"""
import threading
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from doctorate_reader.schemas import UserProfile
from doctorate_reader.workflows.newsletter import build_newsletter_html
from doctorate_reader.api import database


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="Doctorate Reader API",
    version="1.0.0",
    description="Generate personalised academic newsletters using OpenAlex + local LLM.",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# In-memory job store  (replace with Redis/DB for multi-worker deployments)
# ---------------------------------------------------------------------------

_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ProfileRequest(BaseModel):
    interests: List[str] = Field(..., min_length=1)
    research_line: Optional[str] = None
    example_docs: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    id: str
    interests: List[str]
    research_line: Optional[str] = None
    example_docs: Optional[List[str]] = None


class NewsletterRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    profile_id: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=20)
    num_results: int = Field(default=20, ge=1, le=100)
    min_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    only_open_access: bool = False


class NewsletterJobResponse(BaseModel):
    job_id: str


class NewsletterResultResponse(BaseModel):
    status: str          # "pending" | "done" | "error"
    html: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _run_newsletter(
    job_id: str,
    topic: str,
    user_profile: Optional[UserProfile],
    top_n: int,
    num_results: int,
    min_year: Optional[int],
    only_open_access: bool,
) -> None:
    try:
        html = build_newsletter_html(
            topic=topic,
            num_results=num_results,
            top_n=top_n,
            min_year=min_year,
            only_open_access=only_open_access,
            user_profile=user_profile,
        )
        with _jobs_lock:
            _jobs[job_id] = {"status": "done", "html": html}
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id] = {"status": "error", "error": str(exc)}


# ---------------------------------------------------------------------------
# Routes — profiles
# ---------------------------------------------------------------------------

@app.post("/api/v1/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(req: ProfileRequest) -> ProfileResponse:
    profile = UserProfile(
        interests=req.interests,
        research_line=req.research_line,
        example_docs=req.example_docs,
    )
    profile_id = database.create_profile(profile)
    return ProfileResponse(id=profile_id, **req.model_dump())


@app.get("/api/v1/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str) -> ProfileResponse:
    profile = database.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        id=profile_id,
        interests=profile.interests,
        research_line=profile.research_line,
        example_docs=profile.example_docs,
    )


@app.put("/api/v1/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: str, req: ProfileRequest) -> ProfileResponse:
    profile = UserProfile(
        interests=req.interests,
        research_line=req.research_line,
        example_docs=req.example_docs,
    )
    if not database.update_profile(profile_id, profile):
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(id=profile_id, **req.model_dump())


@app.delete("/api/v1/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str) -> None:
    if not database.delete_profile(profile_id):
        raise HTTPException(status_code=404, detail="Profile not found")


# ---------------------------------------------------------------------------
# Routes — newsletters
# ---------------------------------------------------------------------------

@app.post("/api/v1/newsletters", response_model=NewsletterJobResponse, status_code=202)
def create_newsletter(req: NewsletterRequest) -> NewsletterJobResponse:
    user_profile: Optional[UserProfile] = None
    if req.profile_id:
        user_profile = database.get_profile(req.profile_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {"status": "pending"}

    thread = threading.Thread(
        target=_run_newsletter,
        args=(job_id, req.topic, user_profile, req.top_n, req.num_results, req.min_year, req.only_open_access),
        daemon=True,
    )
    thread.start()
    return NewsletterJobResponse(job_id=job_id)


@app.get("/api/v1/newsletters/{job_id}", response_model=NewsletterResultResponse)
def get_newsletter(job_id: str) -> NewsletterResultResponse:
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return NewsletterResultResponse(**job)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/v1/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
