"""Rate-limit dependencies, keyed by client IP address."""

from collections.abc import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.rate_limit import SlidingWindowLimiter, parse_rate

limiter = SlidingWindowLimiter()


def rate_limit(scope: str, rate_setting: str) -> Callable[[Request], None]:
    """Build a dependency allowing `settings.<rate_setting>` requests per client IP.

    Every request counts (successful or not), so failed logins and invalid
    applications are limited too. The setting is read on each request.
    """

    def dependency(request: Request) -> None:
        if not settings.rate_limit_enabled:
            return
        limit, window = parse_rate(getattr(settings, rate_setting))
        client_ip = request.client.host if request.client else "unknown"
        retry_after = limiter.hit(f"{scope}:{client_ip}", limit, window)
        if retry_after is not None:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests, please try again later",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency


login_rate_limit = rate_limit("login", "rate_limit_login")
apply_rate_limit = rate_limit("apply", "rate_limit_apply")
