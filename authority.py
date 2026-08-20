from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .reason_codes import ReasonCode


@dataclass(frozen=True)
class Capability:
    capability_id: str
    principal: str
    action_type: str
    resource_scope: str
    purpose: str
    expires_at: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        now = now or datetime.now(timezone.utc)
        return now >= self.expires_at


class AuthorityError(PermissionError):
    pass


def authorize(*, principal: str, action_type: str, resource_scope: str, capabilities: tuple[Capability, ...]) -> Capability:
    for capability in capabilities:
        if capability.is_expired():
            continue
        if capability.principal != principal:
            continue
        if capability.action_type != action_type:
            continue
        if capability.resource_scope not in {resource_scope, "*"}:
            continue
        return capability
    raise AuthorityError(ReasonCode.AGN02_AUTHORIZATION_MISSING.value)


def deny_self_privilege(requesting_principal: str, requested_principal: str) -> None:
    if requesting_principal == requested_principal:
        raise AuthorityError(ReasonCode.AUT01_SELF_PRIVILEGE_ATTEMPT.value)
