from __future__ import annotations

import csv
import io
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from app.config import settings
from app.schemas.analytics import (
    AnalyticsAiUsageSummary,
    AnalyticsBreakdownItem,
    AnalyticsErrorRecord,
    AnalyticsEventRecord,
    AnalyticsMetricCard,
    AnalyticsNewsItem,
    AnalyticsNewsSummaryOut,
    AnalyticsPhotoRecord,
    AnalyticsPhotosHistoryOut,
    AnalyticsPhotosMismatchOut,
    AnalyticsPhotosSummaryOut,
    AnalyticsSourceStatus,
    AnalyticsSummaryOut,
    AnalyticsSystemHealthOut,
    AnalyticsThreadStat,
    AnalyticsTimeBucket,
    AnalyticsTimeseriesOut,
    AnalyticsUserStat,
    AnalyticsUsersTopOut,
)


AI_USAGE_PATTERN = re.compile(
    r"\[(?P<timestamp>[^\]]+)\]\s+"
    r"(?:(?:user=(?P<user_id>\d+))\s+)?"
    r"(?:(?:model=(?P<model>[^\s]+))\s+)?"
    r"prompt=(?P<prompt>\d+)\s+"
    r"completion=(?P<completion>\d+)\s+"
    r"total=(?P<total>\d+)\s+"
    r"cost=\$(?P<cost>\d+(?:\.\d+)?)"
)


@dataclass(slots=True)
class AnalyticsFilters:
    period: str = '30d'
    user_id: int | None = None
    chat_id: int | None = None
    thread_id: int | None = None
    event: str | None = None
    module: str | None = None
    limit: int = 25
    offset: int = 0


def _resolve_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path.cwd() / candidate


def _parse_datetime(value: object) -> datetime | None:
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace('Z', '+00:00')
    candidates = (
        normalized,
        normalized.replace('T', ' '),
    )
    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    patterns = (
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%d',
    )
    for pattern in patterns:
        try:
            dt = datetime.strptime(text, pattern)
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat()


def _period_range(period: str) -> tuple[str, datetime, datetime]:
    now = datetime.now(timezone.utc)
    normalized = (period or '30d').lower()
    if normalized == 'today':
        start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    elif normalized == '7d':
        start = now - timedelta(days=7)
    elif normalized == '90d':
        start = now - timedelta(days=90)
    else:
        normalized = '30d'
        start = now - timedelta(days=30)
    return normalized, start, now


def _event_module(event_type: str, meta: object) -> str:
    if isinstance(meta, dict):
        module_value = meta.get('module') or meta.get('source')
        if module_value:
            return str(module_value)
    if event_type == 'photo':
        return 'photos'
    if event_type == 'doc':
        return 'documents'
    if event_type.startswith('reaction'):
        return 'engagement'
    if event_type in {'cmd', 'msg_text', 'callback', 'caption', 'video', 'audio', 'voice', 'sticker'}:
        return 'bot'
    return 'core'


def _safe_json_load(path: Path | None) -> object:
    resolved = _resolve_path(path)
    if resolved is None or not resolved.exists():
        return None
    try:
        return json.loads(resolved.read_text(encoding='utf-8'))
    except Exception:
        return None


def _source_status(key: str, label: str, path: Path | None, records: int, note: str | None = None) -> AnalyticsSourceStatus:
    resolved = _resolve_path(path)
    available = bool(resolved and resolved.exists())
    updated_at = None
    if available and resolved is not None:
        updated_at = _to_iso(datetime.fromtimestamp(resolved.stat().st_mtime, tz=timezone.utc))
    return AnalyticsSourceStatus(
        key=key,
        label=label,
        path=str(resolved or ''),
        available=available,
        records=records,
        updated_at=updated_at,
        note=note,
    )


def _load_events(filters: AnalyticsFilters) -> tuple[list[AnalyticsEventRecord], list[AnalyticsSourceStatus]]:
    path = _resolve_path(settings.analytics_events_file)
    normalized_period, start, end = _period_range(filters.period)
    if path is None or not path.exists():
        return [], [_source_status('events', 'analytics_log.jsonl', settings.analytics_events_file, 0, 'Файл событий не найден')]

    events: list[AnalyticsEventRecord] = []
    total_records = 0
    with path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            total_records += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            dt = _parse_datetime(payload.get('dt') or payload.get('ts'))
            if dt is None or dt < start or dt > end:
                continue
            event_type = str(payload.get('event') or 'unknown')
            meta = payload.get('meta') if isinstance(payload.get('meta'), dict) else {}
            record = AnalyticsEventRecord(
                ts=float(payload.get('ts')) if payload.get('ts') is not None else None,
                dt=_to_iso(dt),
                event=event_type,
                module=_event_module(event_type, meta),
                user_id=payload.get('user_id'),
                username=payload.get('username'),
                chat_id=payload.get('chat_id'),
                thread_id=payload.get('thread_id'),
                message_id=payload.get('message_id'),
                meta=meta,
            )
            if filters.user_id is not None and record.user_id != filters.user_id:
                continue
            if filters.chat_id is not None and record.chat_id != filters.chat_id:
                continue
            if filters.thread_id is not None and record.thread_id != filters.thread_id:
                continue
            if filters.event and record.event != filters.event:
                continue
            if filters.module and record.module != filters.module:
                continue
            events.append(record)

    events.sort(key=lambda item: item.dt or '', reverse=True)
    return events, [_source_status('events', 'analytics_log.jsonl', settings.analytics_events_file, total_records, f'Период: {normalized_period}')]


def _load_photo_history() -> tuple[list[dict[str, object]], AnalyticsSourceStatus]:
    payload = _safe_json_load(settings.analytics_photo_history_file)
    if not isinstance(payload, dict):
        return [], _source_status('photos', 'photo_history.json', settings.analytics_photo_history_file, 0, 'История фото не подключена')

    rows: list[dict[str, object]] = []
    for photo_id, item in payload.items():
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                'photo_id': str(photo_id),
                'timestamp': item.get('timestamp'),
                'caption': item.get('caption'),
                'reply': item.get('reply'),
                'status': item.get('status') or 'ok',
            }
        )
    rows.sort(key=lambda row: _to_iso(_parse_datetime(row.get('timestamp'))) or '', reverse=True)
    return rows, _source_status('photos', 'photo_history.json', settings.analytics_photo_history_file, len(rows))


def _load_mismatch_log() -> tuple[list[dict[str, object]], AnalyticsSourceStatus]:
    payload = _safe_json_load(settings.analytics_mismatch_file)
    if not isinstance(payload, dict):
        return [], _source_status('mismatch', 'mismatch_log.json', settings.analytics_mismatch_file, 0, 'Mismatch-лог не подключён')

    rows: list[dict[str, object]] = []
    for photo_id, item in payload.items():
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                'photo_id': str(photo_id),
                'timestamp': item.get('timestamp'),
                'caption': item.get('caption'),
                'reply': item.get('reply'),
                'status': str(item.get('status') or 'mismatch'),
            }
        )
    rows.sort(key=lambda row: _to_iso(_parse_datetime(row.get('timestamp'))) or '', reverse=True)
    return rows, _source_status('mismatch', 'mismatch_log.json', settings.analytics_mismatch_file, len(rows))


def _load_news_cache() -> tuple[list[dict[str, object]], AnalyticsSourceStatus]:
    payload = _safe_json_load(settings.analytics_news_cache_file)
    if not isinstance(payload, dict):
        return [], _source_status('news_cache', 'news_cache.json', settings.analytics_news_cache_file, 0, 'Кэш новостей не подключён')

    rows: list[dict[str, object]] = []
    for news_id, item in payload.items():
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                'news_id': str(news_id),
                'title': str(item.get('title') or 'Без заголовка'),
                'link': item.get('link'),
                'published': item.get('published'),
                'ts': item.get('ts'),
            }
        )
    rows.sort(key=lambda row: _to_iso(_parse_datetime(row.get('ts') or row.get('published'))) or '', reverse=True)
    return rows, _source_status('news_cache', 'news_cache.json', settings.analytics_news_cache_file, len(rows))


def _load_news_drafts() -> tuple[dict[str, str], AnalyticsSourceStatus]:
    payload = _safe_json_load(settings.analytics_news_drafts_file)
    if not isinstance(payload, dict):
        return {}, _source_status('news_drafts', 'news_drafts.json', settings.analytics_news_drafts_file, 0, 'Черновики новостей не подключены')
    drafts = {str(key): str(value) for key, value in payload.items()}
    return drafts, _source_status('news_drafts', 'news_drafts.json', settings.analytics_news_drafts_file, len(drafts))


def _load_ai_usage() -> tuple[list[dict[str, object]], AnalyticsSourceStatus]:
    path = _resolve_path(settings.analytics_ai_usage_file)
    if path is None or not path.exists():
        return [], _source_status('ai_usage', 'ai_usage_log.txt', settings.analytics_ai_usage_file, 0, 'Лог AI-расхода не найден')

    text = path.read_text(encoding='utf-8')
    entries: list[dict[str, object]] = []
    for match in AI_USAGE_PATTERN.finditer(text):
        entries.append(
            {
                'timestamp': match.group('timestamp'),
                'user_id': int(match.group('user_id')) if match.group('user_id') else None,
                'model': match.group('model') or 'unknown',
                'prompt': int(match.group('prompt')),
                'completion': int(match.group('completion')),
                'total': int(match.group('total')),
                'cost': float(match.group('cost')),
            }
        )
    entries.sort(key=lambda row: _to_iso(_parse_datetime(row.get('timestamp'))) or '', reverse=True)
    return entries, _source_status('ai_usage', 'ai_usage_log.txt', settings.analytics_ai_usage_file, len(entries))


def _load_runtime_metrics() -> tuple[dict[str, object], AnalyticsSourceStatus]:
    payload = _safe_json_load(settings.analytics_runtime_metrics_file)
    if not isinstance(payload, dict):
        return {}, _source_status('runtime_metrics', 'runtime_metrics.json', settings.analytics_runtime_metrics_file, 0, 'Runtime-метрики процесса не подключены')
    return payload, _source_status('runtime_metrics', 'runtime_metrics.json', settings.analytics_runtime_metrics_file, len(payload))


def _filter_records_by_period(rows: list[dict[str, object]], period: str, timestamp_key: str) -> list[dict[str, object]]:
    _, start, end = _period_range(period)
    result = []
    for row in rows:
        dt = _parse_datetime(row.get(timestamp_key))
        if dt is None:
            continue
        if start <= dt <= end:
            result.append(row)
    return result


def _breakdown(counter: Counter[str]) -> list[AnalyticsBreakdownItem]:
    items = [AnalyticsBreakdownItem(key=key, label=key.replace('_', ' ').title(), value=value) for key, value in counter.most_common()]
    return items


def _truncate(value: object, limit: int = 140) -> str:
    text = str(value or '').strip()
    if len(text) <= limit:
        return text
    return f'{text[:limit - 1]}…'


def _is_error_event(event: AnalyticsEventRecord) -> bool:
    if 'err' in event.event or 'error' in event.event:
        return True
    status = event.meta.get('status')
    return str(status).lower() in {'error', 'err', 'failed', 'mismatch'}


def _news_category(title: str) -> str:
    normalized = title.lower()
    if any(token in normalized for token in ('маркиров', 'честн', 'gtin', 'км')):
        return 'Маркировка'
    if any(token in normalized for token in ('тамож', 'импорт', 'вэд', 'китай')):
        return 'ВЭД и импорт'
    if any(token in normalized for token in ('штраф', 'наруш', 'изъят', 'провер')):
        return 'Контроль и риски'
    if any(token in normalized for token in ('закон', 'постанов', 'правил', 'обязательн')):
        return 'Регулирование'
    return 'Прочее'


def _news_source(link: object) -> str:
    host = urlparse(str(link or '')).netloc or 'unknown'
    return host.replace('www.', '')


def get_analytics_summary(filters: AnalyticsFilters) -> AnalyticsSummaryOut:
    events, event_sources = _load_events(filters)
    photos, photo_source = _load_photo_history()
    mismatches, mismatch_source = _load_mismatch_log()
    news_cache, news_source = _load_news_cache()
    drafts, drafts_source = _load_news_drafts()
    runtime_metrics, runtime_source = _load_runtime_metrics()

    filtered_photos = _filter_records_by_period(photos, filters.period, 'timestamp')
    filtered_mismatches = _filter_records_by_period(mismatches, filters.period, 'timestamp')
    filtered_news = _filter_records_by_period(news_cache, filters.period, 'ts')

    event_breakdown = Counter(record.event for record in events)
    module_breakdown = Counter(record.module for record in events)
    active_users = len({record.user_id for record in events if record.user_id is not None})
    error_count = len([record for record in events if _is_error_event(record)]) + len(
        [item for item in filtered_mismatches if str(item.get('status')).lower() != 'ok']
    )

    cards = [
        AnalyticsMetricCard(key='events', label='Total events', value=len(events), secondary='События из bot analytics', tone='brand'),
        AnalyticsMetricCard(key='users', label='Active users', value=active_users, secondary='Уникальные user_id за период'),
        AnalyticsMetricCard(key='photos', label='Photos processed', value=len(filtered_photos), secondary='История фото-анализов'),
        AnalyticsMetricCard(key='errors', label='Errors count', value=error_count, secondary='Ошибки и mismatch-сигналы', tone='danger' if error_count else 'success'),
        AnalyticsMetricCard(
            key='kms',
            label='KMS ok / err',
            value=f"{runtime_metrics.get('kms_ok', 0)} / {runtime_metrics.get('kms_err', 0)}",
            secondary='Runtime-снимок процесса' if runtime_metrics else 'Недоступно без snapshot',
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='tg',
            label='TG send ok / err',
            value=f"{runtime_metrics.get('tg_msg_ok', 0)} / {runtime_metrics.get('tg_msg_err', 0)}",
            secondary='Сообщения Telegram' if runtime_metrics else 'Недоступно без snapshot',
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='latency',
            label='Latency p50 / p95',
            value=f"{runtime_metrics.get('kms_p50_ms', 0)} / {runtime_metrics.get('kms_p95_ms', 0)}",
            secondary='мс',
            unit='ms',
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='news',
            label='News found / drafts',
            value=f'{len(filtered_news)} / {len(drafts)}',
            secondary='Найдено в кэше / есть черновик',
        ),
    ]

    highlights = [
        f"За период {filters.period} собрано {len(events)} событий и {len(filtered_photos)} фото-кейсов.",
        f"Топ-модуль по активности: {module_breakdown.most_common(1)[0][0] if module_breakdown else 'нет данных'}.",
        'Runtime-метрики KMS/TG приходят только из snapshot-файла. Для продовой точности стоит писать их в persistent storage.'
        if not runtime_metrics
        else 'Runtime-метрики подключены через snapshot-файл.',
    ]

    period, start, end = _period_range(filters.period)
    return AnalyticsSummaryOut(
        period=period,
        range_start=_to_iso(start),
        range_end=_to_iso(end),
        cards=cards,
        event_breakdown=_breakdown(event_breakdown),
        module_breakdown=_breakdown(module_breakdown),
        source_status=event_sources + [photo_source, mismatch_source, news_source, drafts_source, runtime_source],
        highlights=highlights,
    )


def get_event_timeseries(filters: AnalyticsFilters) -> AnalyticsTimeseriesOut:
    events, _ = _load_events(filters)
    period, start, end = _period_range(filters.period)
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for record in events:
        dt = _parse_datetime(record.dt)
        if dt is None:
            continue
        key = dt.date().isoformat()
        grouped[key]['__total__'] += 1
        grouped[key][record.event] += 1

    buckets: list[AnalyticsTimeBucket] = []
    cursor = start.date()
    end_date = end.date()
    while cursor <= end_date:
        key = cursor.isoformat()
        counter = grouped.get(key, Counter())
        breakdown = {event: count for event, count in counter.items() if event != '__total__'}
        buckets.append(AnalyticsTimeBucket(date=key, total=counter.get('__total__', 0), breakdown=breakdown))
        cursor += timedelta(days=1)

    paged = events[filters.offset : filters.offset + filters.limit]
    return AnalyticsTimeseriesOut(
        period=period,
        range_start=_to_iso(start),
        range_end=_to_iso(end),
        buckets=buckets,
        event_breakdown=_breakdown(Counter(record.event for record in events)),
        module_breakdown=_breakdown(Counter(record.module for record in events)),
        events=paged,
        total_events=len(events),
        limit=filters.limit,
        offset=filters.offset,
        has_more=filters.offset + filters.limit < len(events),
    )


def get_top_users(filters: AnalyticsFilters) -> AnalyticsUsersTopOut:
    events, _ = _load_events(filters)
    per_user: dict[int | None, dict[str, object]] = {}
    per_thread: dict[int, dict[str, object]] = {}

    for record in events:
        entry = per_user.setdefault(
            record.user_id,
            {
                'username': record.username or ('Unknown user' if record.user_id is None else str(record.user_id)),
                'total_events': 0,
                'photos': 0,
                'commands': 0,
                'callbacks': 0,
                'errors': 0,
                'last_seen_at': None,
            },
        )
        entry['total_events'] = int(entry['total_events']) + 1
        entry['photos'] = int(entry['photos']) + (1 if record.event == 'photo' else 0)
        entry['commands'] = int(entry['commands']) + (1 if record.event == 'cmd' else 0)
        entry['callbacks'] = int(entry['callbacks']) + (1 if record.event == 'callback' else 0)
        entry['errors'] = int(entry['errors']) + (1 if _is_error_event(record) else 0)
        last_seen = entry['last_seen_at']
        if last_seen is None or (record.dt and record.dt > str(last_seen)):
            entry['last_seen_at'] = record.dt

        if record.thread_id is not None:
            thread_entry = per_thread.setdefault(
                record.thread_id,
                {
                    'total_events': 0,
                    'users': set(),
                    'last_seen_at': None,
                },
            )
            thread_entry['total_events'] = int(thread_entry['total_events']) + 1
            users = thread_entry['users']
            if isinstance(users, set) and record.user_id is not None:
                users.add(record.user_id)
            if thread_entry['last_seen_at'] is None or (record.dt and record.dt > str(thread_entry['last_seen_at'])):
                thread_entry['last_seen_at'] = record.dt

    top_users = [
        AnalyticsUserStat(
            user_id=user_id,
            username=str(payload['username']),
            total_events=int(payload['total_events']),
            photos=int(payload['photos']),
            commands=int(payload['commands']),
            callbacks=int(payload['callbacks']),
            errors=int(payload['errors']),
            last_seen_at=str(payload['last_seen_at']) if payload['last_seen_at'] else None,
        )
        for user_id, payload in sorted(per_user.items(), key=lambda item: int(item[1]['total_events']), reverse=True)[:10]
    ]

    top_threads = [
        AnalyticsThreadStat(
            thread_id=thread_id,
            total_events=int(payload['total_events']),
            unique_users=len(payload['users']) if isinstance(payload['users'], set) else 0,
            last_seen_at=str(payload['last_seen_at']) if payload['last_seen_at'] else None,
        )
        for thread_id, payload in sorted(per_thread.items(), key=lambda item: int(item[1]['total_events']), reverse=True)[:10]
    ]
    return AnalyticsUsersTopOut(top_users=top_users, top_threads=top_threads)


def get_photos_summary(filters: AnalyticsFilters) -> AnalyticsPhotosSummaryOut:
    photos, _ = _load_photo_history()
    mismatches, _ = _load_mismatch_log()
    filtered_photos = _filter_records_by_period(photos, filters.period, 'timestamp')
    filtered_mismatches = _filter_records_by_period(mismatches, filters.period, 'timestamp')
    recent = filtered_photos[:4]

    return AnalyticsPhotosSummaryOut(
        total_photo_analyses=len(filtered_photos),
        ok_feedback=len([item for item in filtered_mismatches if str(item.get('status')).lower() == 'ok']),
        mismatch_feedback=len([item for item in filtered_mismatches if str(item.get('status')).lower() != 'ok']),
        captionless_count=len([item for item in filtered_photos if not str(item.get('caption') or '').strip()]),
        recent_cases=[
            AnalyticsPhotoRecord(
                photo_id=str(item['photo_id']),
                timestamp=_to_iso(_parse_datetime(item.get('timestamp'))),
                caption=str(item.get('caption') or ''),
                status=str(item.get('status') or 'ok'),
                reply_preview=_truncate(item.get('reply')),
            )
            for item in recent
        ],
    )


def get_photos_history(filters: AnalyticsFilters) -> AnalyticsPhotosHistoryOut:
    photos, _ = _load_photo_history()
    filtered = _filter_records_by_period(photos, filters.period, 'timestamp')
    items = filtered[filters.offset : filters.offset + filters.limit]
    return AnalyticsPhotosHistoryOut(
        items=[
            AnalyticsPhotoRecord(
                photo_id=str(item['photo_id']),
                timestamp=_to_iso(_parse_datetime(item.get('timestamp'))),
                caption=str(item.get('caption') or ''),
                status=str(item.get('status') or 'ok'),
                reply_preview=_truncate(item.get('reply')),
            )
            for item in items
        ],
        total=len(filtered),
        limit=filters.limit,
        offset=filters.offset,
        has_more=filters.offset + filters.limit < len(filtered),
    )


def get_photos_mismatch(filters: AnalyticsFilters) -> AnalyticsPhotosMismatchOut:
    mismatches, _ = _load_mismatch_log()
    filtered = _filter_records_by_period(mismatches, filters.period, 'timestamp')
    items = filtered[filters.offset : filters.offset + filters.limit]
    return AnalyticsPhotosMismatchOut(
        items=[
            AnalyticsPhotoRecord(
                photo_id=str(item['photo_id']),
                timestamp=_to_iso(_parse_datetime(item.get('timestamp'))),
                caption=str(item.get('caption') or ''),
                status=str(item.get('status') or 'mismatch'),
                reply_preview=_truncate(item.get('reply')),
            )
            for item in items
        ],
        total=len(filtered),
        limit=filters.limit,
        offset=filters.offset,
        has_more=filters.offset + filters.limit < len(filtered),
    )


def get_news_summary(filters: AnalyticsFilters) -> AnalyticsNewsSummaryOut:
    news_cache, _ = _load_news_cache()
    drafts, _ = _load_news_drafts()
    filtered_news = _filter_records_by_period(news_cache, filters.period, 'ts')
    by_source = Counter()
    by_category = Counter()
    items: list[AnalyticsNewsItem] = []
    for item in filtered_news[:20]:
        title = str(item.get('title') or 'Без заголовка')
        source = _news_source(item.get('link'))
        category = _news_category(title)
        by_source[source] += 1
        by_category[category] += 1
        news_id = str(item['news_id'])
        items.append(
            AnalyticsNewsItem(
                news_id=news_id,
                title=title,
                source=source,
                category=category,
                link=str(item.get('link')) if item.get('link') else None,
                published_at=_to_iso(_parse_datetime(item.get('published'))),
                cached_at=_to_iso(_parse_datetime(item.get('ts'))),
                has_draft=news_id in drafts,
            )
        )

    notes = [
        'Published count сейчас не хранится в явном виде в кэше, поэтому раздел показывает found/draft и оставляет published=0 как безопасный fallback.',
    ]
    return AnalyticsNewsSummaryOut(
        total_found=len(filtered_news),
        total_drafts=len(drafts),
        total_published=0,
        by_category=_breakdown(by_category),
        by_source=_breakdown(by_source),
        recent_items=items,
        notes=notes,
    )


def get_system_health(filters: AnalyticsFilters) -> AnalyticsSystemHealthOut:
    events, event_sources = _load_events(filters)
    _, photo_source = _load_photo_history()
    mismatches, mismatch_source = _load_mismatch_log()
    _, news_source = _load_news_cache()
    _, drafts_source = _load_news_drafts()
    ai_usage_entries, ai_usage_source = _load_ai_usage()
    runtime_metrics, runtime_source = _load_runtime_metrics()

    recent_errors: list[AnalyticsErrorRecord] = []
    for mismatch in mismatches[:10]:
        status = str(mismatch.get('status') or 'mismatch').lower()
        if status == 'ok':
            continue
        recent_errors.append(
            AnalyticsErrorRecord(
                scope='photos',
                source='mismatch_log.json',
                message=_truncate(mismatch.get('caption') or mismatch.get('reply') or 'Mismatch feedback'),
                created_at=_to_iso(_parse_datetime(mismatch.get('timestamp'))),
                severity='warning',
            )
        )

    for event in events:
        if not _is_error_event(event):
            continue
        recent_errors.append(
            AnalyticsErrorRecord(
                scope=event.module,
                source='analytics_log.jsonl',
                message=_truncate(event.meta.get('error') or event.meta.get('message') or event.event),
                created_at=event.dt,
                severity='critical' if 'err' in event.event or 'error' in event.event else 'warning',
            )
        )
        if len(recent_errors) >= 12:
            break

    total_prompt = sum(int(entry['prompt']) for entry in ai_usage_entries)
    total_completion = sum(int(entry['completion']) for entry in ai_usage_entries)
    total_tokens = sum(int(entry['total']) for entry in ai_usage_entries)
    total_cost = round(sum(float(entry['cost']) for entry in ai_usage_entries), 6)

    anomalies: list[str] = []
    if not runtime_metrics:
        anomalies.append('Нет snapshot-файла runtime-метрик. Счётчики KMS/TG показываются как unavailable.')
    if recent_errors:
        anomalies.append(f'За период найдено {len(recent_errors)} сигналов об ошибках или mismatch-кейсах.')
    if ai_usage_entries and total_cost > 1:
        anomalies.append(f'AI usage accumulated cost: ${total_cost:.4f}.')
    if not ai_usage_entries:
        anomalies.append('Лог AI usage пустой или не подключён.')

    metrics = [
        AnalyticsMetricCard(
            key='kms_delivery',
            label='KMS delivery ok / err',
            value=f"{runtime_metrics.get('kms_ok', 0)} / {runtime_metrics.get('kms_err', 0)}",
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='tg_message_delivery',
            label='TG msg ok / err',
            value=f"{runtime_metrics.get('tg_msg_ok', 0)} / {runtime_metrics.get('tg_msg_err', 0)}",
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='tg_document_delivery',
            label='TG doc ok / err',
            value=f"{runtime_metrics.get('tg_doc_ok', 0)} / {runtime_metrics.get('tg_doc_err', 0)}",
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='latency_p50',
            label='KMS p50',
            value=runtime_metrics.get('kms_p50_ms'),
            unit='ms',
            available=bool(runtime_metrics),
        ),
        AnalyticsMetricCard(
            key='latency_p95',
            label='KMS p95',
            value=runtime_metrics.get('kms_p95_ms'),
            unit='ms',
            available=bool(runtime_metrics),
        ),
    ]

    ai_usage = AnalyticsAiUsageSummary(
        total_requests=len(ai_usage_entries),
        total_prompt_tokens=total_prompt,
        total_completion_tokens=total_completion,
        total_tokens=total_tokens,
        total_cost_usd=total_cost,
        last_request_at=_to_iso(_parse_datetime(ai_usage_entries[0]['timestamp'])) if ai_usage_entries else None,
    )

    return AnalyticsSystemHealthOut(
        metrics=metrics,
        recent_errors=recent_errors[:10],
        anomalies=anomalies,
        ai_usage=ai_usage,
        source_status=event_sources + [photo_source, mismatch_source, news_source, drafts_source, ai_usage_source, runtime_source],
    )


def _events_csv_rows(filters: AnalyticsFilters) -> list[list[object]]:
    events, _ = _load_events(filters)
    rows: list[list[object]] = [['dt', 'event', 'module', 'user_id', 'username', 'chat_id', 'thread_id', 'message_id', 'meta']]
    for record in events:
        rows.append(
            [
                record.dt or '',
                record.event,
                record.module,
                record.user_id or '',
                record.username or '',
                record.chat_id or '',
                record.thread_id or '',
                record.message_id or '',
                json.dumps(record.meta, ensure_ascii=False),
            ]
        )
    return rows


def export_analytics_csv(filters: AnalyticsFilters) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    for row in _events_csv_rows(filters):
        writer.writerow(row)
    return output.getvalue().encode('utf-8')


def _excel_cell(value: object, row_index: int, column_index: int) -> str:
    cell_ref = f'{_excel_column(column_index)}{row_index}'
    if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(float(value)):
        return f'<c r="{cell_ref}"><v>{value}</v></c>'
    text = escape(str(value if value is not None else ''))
    return f'<c r="{cell_ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def _excel_column(index: int) -> str:
    result = ''
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _sheet_xml(rows: list[list[object]]) -> str:
    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = ''.join(_excel_cell(value, row_index, column_index) for column_index, value in enumerate(row, start=1))
        xml_rows.append(f'<row r="{row_index}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        + ''.join(xml_rows)
        + '</sheetData></worksheet>'
    )


def export_analytics_xlsx(filters: AnalyticsFilters) -> bytes:
    summary = get_analytics_summary(filters)
    usage = get_event_timeseries(filters)
    photos = get_photos_summary(filters)
    news = get_news_summary(filters)
    system = get_system_health(filters)

    sheets = {
        'Summary': [['Metric', 'Value', 'Secondary']] + [[card.label, card.value, card.secondary or ''] for card in summary.cards],
        'Usage': _events_csv_rows(filters),
        'Photos': [
            ['Metric', 'Value'],
            ['Total photo analyses', photos.total_photo_analyses],
            ['OK feedback', photos.ok_feedback],
            ['Mismatch feedback', photos.mismatch_feedback],
            ['Captionless count', photos.captionless_count],
        ],
        'News': [['Metric', 'Value'], ['Total found', news.total_found], ['Drafts', news.total_drafts], ['Published', news.total_published]],
        'System': [
            ['Metric', 'Value', 'Secondary'],
            *[[metric.label, metric.value, metric.secondary or ''] for metric in system.metrics],
            [],
            ['AI usage requests', system.ai_usage.total_requests, ''],
            ['AI tokens total', system.ai_usage.total_tokens, ''],
            ['AI cost usd', system.ai_usage.total_cost_usd, ''],
        ],
        'Daily': [['Date', 'Total']] + [[bucket.date, bucket.total] for bucket in usage.buckets],
    }

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        + ''.join(
            f'<sheet name="{escape(name[:31])}" sheetId="{index}" r:id="rId{index}"/>'
            for index, name in enumerate(sheets.keys(), start=1)
        )
        + '</sheets></workbook>'
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + ''.join(
            f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
            for index, _ in enumerate(sheets.keys(), start=1)
        )
        + '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        + '</Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + ''.join(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for index, _ in enumerate(sheets.keys(), start=1)
        )
        + '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
        '<cellXfs count="1"><xf xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', content_types)
        archive.writestr('_rels/.rels', root_rels)
        archive.writestr('xl/workbook.xml', workbook_xml)
        archive.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        archive.writestr('xl/styles.xml', styles_xml)
        for index, rows in enumerate(sheets.values(), start=1):
            archive.writestr(f'xl/worksheets/sheet{index}.xml', _sheet_xml(rows))
    return buffer.getvalue()
