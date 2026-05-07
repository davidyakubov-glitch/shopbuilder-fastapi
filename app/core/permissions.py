from fastapi import HTTPException, status


def ensure_role(actual_role: str, allowed_roles: set[str]) -> None:
    if actual_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this resource.",
        )
