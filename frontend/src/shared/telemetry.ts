/**
 * Lightweight client diagnostics — no third-party SDK.
 *
 * Goals (see optimization brief §10):
 *  - Capture page-load timing from the Performance API (TTFB, DOMContentLoaded,
 *    load, frontend boot duration).
 *  - Record only *interesting* API events: slow requests (> SLOW_MS) and
 *    network/timeout errors. Fast successful requests are ignored to keep this
 *    cheap and privacy-preserving.
 *  - Never include tokens, request/response bodies, or personal data. Only a
 *    coarse endpoint label (method + path template), duration and outcome.
 *
 * Transport is abstracted behind `emit()`. Today it batches events and, if a
 * backend telemetry endpoint exists, ships them with `navigator.sendBeacon`
 * (fire-and-forget, survives page unload). If the endpoint is absent the events
 * are simply dropped in production and surfaced to the console in dev.
 *
 * BACKEND TODO: expose `POST /api/v1/telemetry/client` accepting
 *   { events: ClientTelemetryEvent[] }
 * returning 204. It must be unauthenticated-tolerant (best-effort), rate-limited,
 * and must NOT log the payload verbatim into anything sensitive. Until it exists,
 * set VITE_TELEMETRY_ENABLED=false (default) and nothing is sent.
 */

const SLOW_MS = 5_000;
const TELEMETRY_PATH = '/api/v1/telemetry/client';
const ENABLED = import.meta.env.VITE_TELEMETRY_ENABLED === 'true';
const DEV = import.meta.env.DEV;

export type TelemetryOutcome = 'ok' | 'timeout' | 'network' | 'error';

export interface ClientTelemetryEvent {
  type: 'navigation' | 'api';
  /** For api events: "GET /products". For navigation: "load". */
  label: string;
  /** Milliseconds. */
  durationMs: number;
  outcome?: TelemetryOutcome;
  /** HTTP status for api events, when available. */
  status?: number;
  at: number;
}

let queue: ClientTelemetryEvent[] = [];
let flushTimer: ReturnType<typeof setTimeout> | null = null;

function scheduleFlush() {
  if (flushTimer) return;
  flushTimer = setTimeout(flush, 4_000);
}

function flush() {
  flushTimer = null;
  if (queue.length === 0) return;
  const batch = queue;
  queue = [];

  if (DEV) {
    // Keep local development observable without any network call.
    // eslint-disable-next-line no-console
    console.debug('[telemetry]', batch);
  }
  if (!ENABLED) return;

  try {
    const body = JSON.stringify({ events: batch });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(TELEMETRY_PATH, new Blob([body], { type: 'application/json' }));
    } else {
      void fetch(TELEMETRY_PATH, { method: 'POST', body, keepalive: true, headers: { 'Content-Type': 'application/json' } });
    }
  } catch {
    /* diagnostics must never throw into app code */
  }
}

function push(event: ClientTelemetryEvent) {
  queue.push(event);
  if (queue.length >= 20) flush();
  else scheduleFlush();
}

/** Record an API call. Only slow calls and failures are kept. */
export function recordApi(params: {
  label: string;
  durationMs: number;
  outcome: TelemetryOutcome;
  status?: number;
}) {
  if (params.outcome === 'ok' && params.durationMs < SLOW_MS) return;
  push({ type: 'api', at: Date.now(), ...params });
}

/** Capture navigation timing once the page has fully loaded. */
export function captureNavigationTiming() {
  if (typeof performance === 'undefined' || !performance.getEntriesByType) return;
  const record = () => {
    const [nav] = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
    if (!nav) return;
    const marks = {
      ttfb: Math.round(nav.responseStart - nav.requestStart),
      domContentLoaded: Math.round(nav.domContentLoadedEventEnd - nav.startTime),
      load: Math.round(nav.loadEventEnd - nav.startTime),
      // Time from navigation start until the first byte of our JS executed.
      boot: Math.round((performance.now())),
    };
    push({ type: 'navigation', label: 'load', durationMs: marks.load, at: Date.now() });
    if (DEV) {
      // eslint-disable-next-line no-console
      console.debug('[telemetry] navigation', marks);
    }
  };

  if (document.readyState === 'complete') record();
  else window.addEventListener('load', () => setTimeout(record, 0), { once: true });
  window.addEventListener('pagehide', flush, { once: true });
}
