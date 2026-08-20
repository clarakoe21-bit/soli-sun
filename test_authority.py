from datetime import datetime, timedelta, timezone
import pytest

from soli_sun.authority import Capability, AuthorityError, authorize, deny_self_privilege


def test_authority_requires_matching_capability():
    cap = Capability("c1", "MEMORIA", "READ_MEMORY", "u1", "CURRENT_RESPONSE")
    assert authorize(principal="MEMORIA", action_type="READ_MEMORY", resource_scope="u1", capabilities=(cap,)) == cap


def test_authority_denies_missing_capability():
    with pytest.raises(AuthorityError):
        authorize(principal="SOL_VOX", action_type="READ_MEMORY", resource_scope="u1", capabilities=())


def test_expired_capability_is_denied():
    cap = Capability("c1", "MEMORIA", "READ_MEMORY", "u1", "CURRENT_RESPONSE", datetime.now(timezone.utc)-timedelta(seconds=1))
    with pytest.raises(AuthorityError):
        authorize(principal="MEMORIA", action_type="READ_MEMORY", resource_scope="u1", capabilities=(cap,))


def test_self_privilege_attempt_is_blocked():
    with pytest.raises(AuthorityError, match="AUT01_SELF_PRIVILEGE_ATTEMPT"):
        deny_self_privilege("SOL_VOX", "SOL_VOX")
