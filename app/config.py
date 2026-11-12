"""Application configuration via environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # Core
    app_name: str = "Uptime Pro"
    env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./uptime.db")
    # Redis (for rate limiting / queue)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_starter: str = os.getenv("STRIPE_PRICE_STARTER", "")
    stripe_price_team: str = os.getenv("STRIPE_PRICE_TEAM", "")
    stripe_price_business: str = os.getenv("STRIPE_PRICE_BUSINESS", "")
    # Email (Resend)
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    email_from: str = os.getenv("EMAIL_FROM", "alerts@uptimepro.app")
    # SMS (Twilio)
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    # Slack
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    # Observability
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    # CORS
    cors_origins: list[str] = field(default_factory=lambda: os.getenv(
        "CORS_ORIGINS", "*").split(","))
    # Checker
    checker_regions: list[str] = field(default_factory=lambda: os.getenv(
        "CHECKER_REGIONS", "us-east,eu-west").split(","))
    checker_concurrency: int = int(os.getenv("CHECKER_CONCURRENCY", "50"))


settings = Settings()


def is_production() -> bool:
    return settings.env == "production"


def services_configured() -> dict[str, bool]:
    return {
        "database": bool(settings.database_url),
        "stripe": bool(settings.stripe_secret_key),
        "email": bool(settings.resend_api_key),
        "sms": bool(settings.twilio_account_sid and settings.twilio_auth_token),
        "slack": bool(settings.slack_webhook_url),
        "sentry": bool(settings.sentry_dsn),
        "redis": bool(settings.redis_url),
    }
