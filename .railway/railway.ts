import { defineRailway, postgres, preserve, project, service, volume } from "railway/iac";

export default defineRailway(() => {
  const Postgres = postgres("Postgres", { region: "iad" });
  const postgresVolume = volume("postgres-volume", { alerts: { usage: { "100": {}, "80": {}, "95": {} } }, allowOnlineResize: true, region: "iad", sizeMB: 500 });
  const api = service("api", {
    replicas: { "iad": 1 },
    healthcheck: "/api/health",
    env: { COOKIE_SECURE: preserve(), DATABASE_URL: preserve(), HTTP_TIMEOUT: preserve(), HTTP_VERIFY_SSL: preserve(), INGESTION_MAX_ITEMS: preserve(), INGESTION_MINUTE: preserve(), JWT_TTL_HOURS: preserve(), LEGAL_PER_DAY: preserve(), LLM_DAILY_CALL_LIMIT: preserve(), LLM_EFFORT: preserve(), LLM_MODEL: preserve(), LLM_PROVIDER: preserve(), LLM_REFUSAL_FALLBACK: preserve(), LLM_TIMEOUT: preserve(), PORT: preserve(), QUESTIONS_PER_DAY: preserve(), QUESTIONS_PER_HOUR: preserve(), ROLE: preserve(), SECRET_KEY: preserve(), SMTP_HOST: preserve(), TIMEZONE: preserve() },
  });
  const worker = service("worker", {
    replicas: { "iad": 1 },
    env: { COOKIE_SECURE: preserve(), DATABASE_URL: preserve(), HTTP_TIMEOUT: preserve(), HTTP_VERIFY_SSL: preserve(), INGESTION_HOUR: preserve(), INGESTION_MAX_ITEMS: preserve(), INGESTION_MINUTE: preserve(), JWT_TTL_HOURS: preserve(), LEGAL_PER_DAY: preserve(), LLM_DAILY_CALL_LIMIT: preserve(), LLM_EFFORT: preserve(), LLM_MODEL: preserve(), LLM_PROVIDER: preserve(), LLM_REFUSAL_FALLBACK: preserve(), LLM_TIMEOUT: preserve(), QUESTIONS_PER_DAY: preserve(), QUESTIONS_PER_HOUR: preserve(), ROLE: preserve(), SECRET_KEY: preserve(), SMTP_HOST: preserve(), TIMEZONE: preserve() },
  });
  const web = service("web", {
    replicas: { "iad": 1 },
    // railway up заливает корень репозитория, поэтому фронт собирался backend-
    // Dockerfile-ом и падал. rootDirectory переводит сборку в web/.
    rootDirectory: "web",
    env: { API_UPSTREAM: preserve() },
  });

  return project("respublicabot", {
    resources: [Postgres, api, worker, web, postgresVolume],
  });
});
