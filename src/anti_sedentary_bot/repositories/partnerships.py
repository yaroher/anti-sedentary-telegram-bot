from __future__ import annotations

from tortoise.transactions import in_transaction

from ..db.models import Partnership, User


async def request_pair(requester: User, target: User) -> tuple[Partnership, Partnership]:
    """Create a pending bidirectional pairing. Both rows start accepted=False."""
    a_id = requester.user_id
    b_id = target.user_id

    async with in_transaction():
        ab = await Partnership.filter(user_id_a=a_id, user_id_b=b_id).first()
        ba = await Partnership.filter(user_id_a=b_id, user_id_b=a_id).first()

        if ab is None:
            ab = await Partnership.create(user_id_a=a_id, user_id_b=b_id, active=True, accepted=False)
        else:
            ab.active = True
            ab.accepted = False
            await ab.save(update_fields=["active", "accepted"])

        if ba is None:
            ba = await Partnership.create(user_id_a=b_id, user_id_b=a_id, active=True, accepted=False)
        else:
            ba.active = True
            ba.accepted = False
            await ba.save(update_fields=["active", "accepted"])

    return ab, ba


async def accept_pair(target: User, requester: User) -> bool:
    """Flip both directional rows to accepted=True. Returns True if a pending pair existed."""
    a_id = target.user_id
    b_id = requester.user_id
    async with in_transaction():
        ab_count = await Partnership.filter(
            user_id_a=a_id, user_id_b=b_id, active=True, accepted=False
        ).update(accepted=True)
        ba_count = await Partnership.filter(
            user_id_a=b_id, user_id_b=a_id, active=True, accepted=False
        ).update(accepted=True)
    return ab_count > 0 and ba_count > 0


async def decline_pair(target: User, requester: User) -> None:
    a_id = target.user_id
    b_id = requester.user_id
    async with in_transaction():
        await Partnership.filter(user_id_a=a_id, user_id_b=b_id).update(active=False)
        await Partnership.filter(user_id_a=b_id, user_id_b=a_id).update(active=False)


async def unpair(user_a: User, user_b: User) -> None:
    a_id = user_a.user_id
    b_id = user_b.user_id
    async with in_transaction():
        await Partnership.filter(user_id_a=a_id, user_id_b=b_id).update(active=False)
        await Partnership.filter(user_id_a=b_id, user_id_b=a_id).update(active=False)


async def partner_of(user: User) -> User | None:
    """Return the ACCEPTED partner (active=True, accepted=True), or None."""
    row = await Partnership.filter(user_id_a=user.user_id, active=True, accepted=True).first()
    if row is None:
        return None
    return await User.filter(user_id=row.user_id_b).first()


async def pending_request_to(target: User) -> User | None:
    """Return the requester User if *target* has an unaccepted pairing request waiting."""
    row = await Partnership.filter(user_id_a=target.user_id, active=True, accepted=False).first()
    if row is None:
        return None
    return await User.filter(user_id=row.user_id_b).first()


async def notify_pairs(user: User) -> list[User]:
    partner = await partner_of(user)
    return [partner] if partner else []
