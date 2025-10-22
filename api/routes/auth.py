"""
Auth and setup routes for GitHub App installation callback
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

# This router is intended to be mounted at prefix '/auth'
router = APIRouter()


@router.get("")
async def auth_index():
    return {"status": "ok", "message": "Auth endpoints available", "endpoints": ["/auth/callback", "/auth/setup"]}


@router.get("/setup")
async def setup_landing(next: Optional[str] = None):
    """Simple landing endpoint GitHub can redirect to after app creation.
    We optionally redirect to a provided 'next' URL, otherwise return JSON.
    """
    if next:
        return RedirectResponse(url=next)
    return {"status": "ok", "message": "PR Copilot setup complete"}


@router.get("/callback")
async def auth_callback(code: Optional[str] = None, installation_id: Optional[str] = None, setup_action: Optional[str] = None):
    """Handle GitHub App post-install redirect.
    For GitHub Apps, this is not an OAuth exchange we need to complete.
    We just acknowledge and guide the user.
    """
    return JSONResponse(
        content={
            "status": "received",
            "code_provided": bool(code),
            "installation_id": installation_id,
            "setup_action": setup_action,
            "next_steps": "Install the app on a repository and open a PR to test webhooks."
        }
    )
