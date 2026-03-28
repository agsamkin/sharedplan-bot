import secrets
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Space, User, UserSpace


async def create_space(session: AsyncSession, user_id: int, name: str) -> Space:
    """Создать пространство и назначить создателя администратором."""
    invite_code = await _generate_invite_code(session)
    space = Space(name=name, invite_code=invite_code, created_by=user_id)
    session.add(space)
    await session.flush()

    membership = UserSpace(user_id=user_id, space_id=space.id, role="admin")
    session.add(membership)
    await session.flush()
    return space


async def _generate_invite_code(session: AsyncSession, max_attempts: int = 5) -> str:
    """Генерация уникального invite-кода с retry при коллизии."""
    for _ in range(max_attempts):
        code = secrets.token_urlsafe(6)
        existing = await session.scalar(
            select(Space.id).where(Space.invite_code == code)
        )
        if existing is None:
            return code
    raise RuntimeError("Не удалось сгенерировать уникальный invite-код")


async def get_user_spaces(session: AsyncSession, user_id: int) -> list[dict]:
    """Список пространств пользователя с ролью и количеством участников."""
    member_count_subq = (
        select(func.count())
        .where(UserSpace.space_id == Space.id)
        .correlate(Space)
        .scalar_subquery()
        .label("member_count")
    )
    stmt = (
        select(
            Space.id,
            Space.name,
            UserSpace.role,
            member_count_subq,
        )
        .join(UserSpace, Space.id == UserSpace.space_id)
        .where(UserSpace.user_id == user_id)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "role": row.role,
            "member_count": row.member_count,
        }
        for row in rows
    ]


async def get_space_by_invite_code(
    session: AsyncSession, invite_code: str
) -> Space | None:
    """Найти пространство по invite-коду."""
    return await session.scalar(
        select(Space).where(Space.invite_code == invite_code)
    )


async def get_space_by_id(session: AsyncSession, space_id: UUID) -> Space | None:
    """Найти пространство по ID."""
    return await session.get(Space, space_id)


async def join_space(
    session: AsyncSession, user_id: int, space_id: UUID
) -> UserSpace | None:
    """Добавить пользователя в пространство. Возвращает None если уже участник."""
    existing = await session.get(UserSpace, (user_id, space_id))
    if existing is not None:
        return None
    membership = UserSpace(user_id=user_id, space_id=space_id, role="member")
    session.add(membership)
    await session.flush()
    return membership


async def get_space_members(session: AsyncSession, space_id: UUID) -> list[dict]:
    """Список участников пространства с информацией о пользователях."""
    stmt = (
        select(User.id, User.first_name, User.username, UserSpace.role, UserSpace.joined_at)
        .join(UserSpace, User.id == UserSpace.user_id)
        .where(UserSpace.space_id == space_id)
        .order_by(UserSpace.role, User.first_name)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "user_id": row.id,
            "first_name": row.first_name,
            "username": row.username,
            "role": row.role,
            "joined_at": row.joined_at.isoformat() if row.joined_at else None,
        }
        for row in rows
    ]


async def check_admin(session: AsyncSession, space_id: UUID, user_id: int) -> bool:
    """Проверить, является ли пользователь администратором пространства."""
    membership = await session.get(UserSpace, (user_id, space_id))
    return membership is not None and membership.role == "admin"


async def find_member_by_username(
    session: AsyncSession, space_id: UUID, username: str
) -> dict | None:
    """Найти участника пространства по username."""
    stmt = (
        select(User.id, User.first_name, User.username, UserSpace.role)
        .join(UserSpace, User.id == UserSpace.user_id)
        .where(UserSpace.space_id == space_id, func.lower(User.username) == username.lower())
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        return None
    return {
        "user_id": row.id,
        "first_name": row.first_name,
        "username": row.username,
        "role": row.role,
    }


async def kick_member(
    session: AsyncSession, space_id: UUID, target_user_id: int
) -> None:
    """Удалить участника из пространства."""
    await session.execute(
        delete(UserSpace).where(
            UserSpace.user_id == target_user_id,
            UserSpace.space_id == space_id,
        )
    )
    await session.flush()


async def delete_space(session: AsyncSession, space_id: UUID) -> None:
    """Удалить пространство (каскадно удаляет events, reminders, memberships)."""
    space = await session.get(Space, space_id)
    if space:
        await session.delete(space)
        await session.flush()
