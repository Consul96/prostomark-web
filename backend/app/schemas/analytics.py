from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyticsBreakdownItem(BaseModel):
    key: str
    label: str
    value: int | float


class AnalyticsMetricCard(BaseModel):
    key: str
    label: str
    value: int | float | str | None
    secondary: str | None = None
    unit: str | None = None
    tone: str = 'neutral'
    available: bool = True


class AnalyticsSourceStatus(BaseModel):
    key: str
    label: str
    path: str
    available: bool
    records: int = 0
    updated_at: str | None = None
    note: str | None = None


class AnalyticsEventRecord(BaseModel):
    ts: float | None = None
    dt: str | None = None
    event: str
    module: str
    user_id: int | None = None
    username: str | None = None
    chat_id: int | None = None
    thread_id: int | None = None
    message_id: int | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class AnalyticsTimeBucket(BaseModel):
    date: str
    total: int
    breakdown: dict[str, int] = Field(default_factory=dict)


class AnalyticsSummaryOut(BaseModel):
    period: str
    range_start: str | None = None
    range_end: str | None = None
    cards: list[AnalyticsMetricCard]
    event_breakdown: list[AnalyticsBreakdownItem]
    module_breakdown: list[AnalyticsBreakdownItem]
    source_status: list[AnalyticsSourceStatus]
    highlights: list[str]


class AnalyticsTimeseriesOut(BaseModel):
    period: str
    range_start: str | None = None
    range_end: str | None = None
    buckets: list[AnalyticsTimeBucket]
    event_breakdown: list[AnalyticsBreakdownItem]
    module_breakdown: list[AnalyticsBreakdownItem]
    events: list[AnalyticsEventRecord]
    total_events: int
    limit: int
    offset: int
    has_more: bool


class AnalyticsUserStat(BaseModel):
    user_id: int | None = None
    username: str
    total_events: int
    photos: int = 0
    commands: int = 0
    callbacks: int = 0
    errors: int = 0
    last_seen_at: str | None = None


class AnalyticsThreadStat(BaseModel):
    thread_id: int
    total_events: int
    unique_users: int
    last_seen_at: str | None = None


class AnalyticsUsersTopOut(BaseModel):
    top_users: list[AnalyticsUserStat]
    top_threads: list[AnalyticsThreadStat]


class AnalyticsPhotoRecord(BaseModel):
    photo_id: str
    timestamp: str | None = None
    caption: str | None = None
    status: str = 'ok'
    reply_preview: str | None = None


class AnalyticsPhotosSummaryOut(BaseModel):
    total_photo_analyses: int
    ok_feedback: int
    mismatch_feedback: int
    captionless_count: int
    recent_cases: list[AnalyticsPhotoRecord]


class AnalyticsPhotosHistoryOut(BaseModel):
    items: list[AnalyticsPhotoRecord]
    total: int
    limit: int
    offset: int
    has_more: bool


class AnalyticsPhotosMismatchOut(BaseModel):
    items: list[AnalyticsPhotoRecord]
    total: int
    limit: int
    offset: int
    has_more: bool


class AnalyticsNewsItem(BaseModel):
    news_id: str
    title: str
    source: str
    category: str
    link: str | None = None
    published_at: str | None = None
    cached_at: str | None = None
    has_draft: bool = False


class AnalyticsNewsSummaryOut(BaseModel):
    total_found: int
    total_drafts: int
    total_published: int
    by_category: list[AnalyticsBreakdownItem]
    by_source: list[AnalyticsBreakdownItem]
    recent_items: list[AnalyticsNewsItem]
    notes: list[str]


class AnalyticsErrorRecord(BaseModel):
    scope: str
    source: str
    message: str
    created_at: str | None = None
    severity: str = 'warning'


class AnalyticsAiUsageSummary(BaseModel):
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    last_request_at: str | None = None


class AnalyticsSystemHealthOut(BaseModel):
    metrics: list[AnalyticsMetricCard]
    recent_errors: list[AnalyticsErrorRecord]
    anomalies: list[str]
    ai_usage: AnalyticsAiUsageSummary
    source_status: list[AnalyticsSourceStatus]

