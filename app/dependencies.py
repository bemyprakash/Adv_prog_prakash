"""
Reusable dependencies for role-based access.
"""
from fastapi import Depends, HTTPException, status
from . import auth, models

def require_role(role: models.RoleEnum):
    def role_checker(user=Depends(auth.get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

def require_any_role(roles):
    def role_checker(user=Depends(auth.get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
