from __future__ import annotations

from tortoise.transactions import in_transaction

from ..db.models import Partnership, User


async def pair(user_a: User, user_b: User) -> tuple[Partnership, Partnership]:
    """Create or reactivate a bidirectional partnership between *user_a* and *user_b*.

    Two rows are maintained (one per direction) so look-ups remain trivial.
    Returns (a_to_b, b_to_a).
    """
    a_id = user_a.user_id
    b_id = user_b.user_id

    async with in_transaction():
        # Try to fetch any existing rows in either direction.
        ab = await Partnership.filter(user_id_a=a_id, user_id_b=b_id).first()
        ba = await Partnership.filter(user_id_a=b_id, user_id_b=a_id).first()

        if ab is None:
            ab = await Partnership.create(user_id_a=a_id, user_id_b=b_id, active=True)
        elif not ab.active:
            ab.active = True
            await ab.save(update_fields=["active"])

        if ba is None:
            ba = await Partnership.create(user_id_a=b_id, user_id_b=a_id, active=True)
        elif not ba.active:
            ba.active = True
            await ba.save(update_fields=["active"])

    return ab, ba


async def unpair(user_a: User, user_b: User) -> None:
    """Deactivate both directional rows for the partnership."""
    a_id = user_a.user_id
    b_id = user_b.user_id
    async with in_transaction():
        await Partnership.filter(user_id_a=a_id, user_id_b=b_id).update(active=False)
        await Partnership.filter(user_id_a=b_id, user_id_b=a_id).update(active=False)


async def partner_of(user: User) -> User | None:
    """Return the partner User for *user* (where this user is user_id_a), or None."""
    row = await Partnership.filter(user_id_a=user.user_id, active=True).first()
    if row is None:
        return None
    return await User.filter(user_id=row.user_id_b).first()


async def notify_pairs(user: User) -> list[User]:
    """Return the list of active partners for *user*.

    Currently returns at most one partner (where this user is user_id_a),
    but typed as a list for future N-way support.
    """
    partner = await partner_of(user)
    if partner is None:
        return []
    return [partner]
