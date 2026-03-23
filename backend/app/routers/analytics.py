from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.models.enums import UserRole
from app.schemas.analytics import (
    AnalyticsNewsSummaryOut,
    AnalyticsPhotosHistoryOut,
    AnalyticsPhotosMismatchOut,
    AnalyticsPhotosSummaryOut,
    AnalyticsSummaryOut,
    AnalyticsSystemHealthOut,
    AnalyticsTimeseriesOut,
    AnalyticsUsersTopOut,
)
from app.security.permissions import require_roles
from app.services.analytics_service import (
    AnalyticsFilters,
    export_analytics_csv,
    export_analytics_xlsx,
    get_analytics_summary,
    get_event_timeseries,
    get_news_summary,
    get_photos_history,
    get_photos_mismatch,
    get_photos_summary,
    get_system_health,
    get_top_users,
)

router = APIRouter(
    prefix='/analytics',
    tags=['analytics'],
    dependencies=[Depends(require_roles(UserRole.MANAGER))],
)


def _filters(
    period: str = Query(default='30d'),
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
    thread_id: int | None = Query(default=None),
    event: str | None = Query(default=None),
    module: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> AnalyticsFilters:
    return AnalyticsFilters(
        period=period,
        user_id=user_id,
        chat_id=chat_id,
        thread_id=thread_id,
        event=event,
        module=module,
        limit=limit,
        offset=offset,
    )


@router.get('/summary', response_model=AnalyticsSummaryOut)
def analytics_summary(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsSummaryOut:
    return get_analytics_summary(filters)


@router.get('/events/timeseries', response_model=AnalyticsTimeseriesOut)
def analytics_timeseries(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsTimeseriesOut:
    return get_event_timeseries(filters)


@router.get('/users/top', response_model=AnalyticsUsersTopOut)
def analytics_users_top(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsUsersTopOut:
    return get_top_users(filters)


@router.get('/photos/summary', response_model=AnalyticsPhotosSummaryOut)
def analytics_photos_summary(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsPhotosSummaryOut:
    return get_photos_summary(filters)


@router.get('/photos/history', response_model=AnalyticsPhotosHistoryOut)
def analytics_photos_history(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsPhotosHistoryOut:
    return get_photos_history(filters)


@router.get('/photos/mismatch', response_model=AnalyticsPhotosMismatchOut)
def analytics_photos_mismatch(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsPhotosMismatchOut:
    return get_photos_mismatch(filters)


@router.get('/news/summary', response_model=AnalyticsNewsSummaryOut)
def analytics_news_summary(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsNewsSummaryOut:
    return get_news_summary(filters)


@router.get('/system/health', response_model=AnalyticsSystemHealthOut)
def analytics_system_health(filters: AnalyticsFilters = Depends(_filters)) -> AnalyticsSystemHealthOut:
    return get_system_health(filters)


@router.get('/export.csv')
def analytics_export_csv(filters: AnalyticsFilters = Depends(_filters)) -> Response:
    return Response(
        content=export_analytics_csv(filters),
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="analytics-export.csv"'},
    )


@router.get('/export.xlsx')
def analytics_export_xlsx(filters: AnalyticsFilters = Depends(_filters)) -> Response:
    return Response(
        content=export_analytics_xlsx(filters),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="analytics-export.xlsx"'},
    )

