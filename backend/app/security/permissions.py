from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.enums import UserRole
from app.models.user import User


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role == UserRole.SUPERADMIN:
            return user
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return user

    return _checker
