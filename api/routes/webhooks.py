"""
GitHub webhook handlers
"""

import json
import logging
import os
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.database import get_db
from api.services.github_client import GitHubClient
from workers.process_pr import process_pull_request
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()

SINGLE_PROCESS = os.getenv("SINGLE_PROCESS", "false").lower() == "true"


@router.post("/github")
async def handle_github_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle GitHub webhook events
    """
    
    try:
        # Get raw body and headers
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        
        logger.info(f"Received GitHub webhook: {event_type}")
        
        # Initialize GitHub client for verification
        github_client = GitHubClient()
        
        # Verify webhook signature
        if not github_client.verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload = json.loads(body.decode('utf-8'))
        installation_id = payload.get("installation", {}).get("id")
        
        # Handle different event types
        if event_type == "pull_request":
            return await _handle_pull_request_event(payload, installation_id, db)
        elif event_type == "issue_comment":
            return await _handle_issue_comment_event(payload, installation_id, db)
        else:
            logger.info(f"Ignoring webhook event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _handle_pull_request_event(payload: dict, installation_id: int | None, db: Session) -> JSONResponse:
    """Handle pull request webhook events"""
    
    action = payload.get("action")
    pr_data = payload.get("pull_request", {})
    
    logger.info(f"Processing PR event: {action}")
    
    # Only process opened and synchronize events for now
    if action in ["opened", "synchronize"]:
        # Attach installation_id for downstream
        pr_data["_installation_id"] = installation_id
        
        if SINGLE_PROCESS:
            logger.info("SINGLE_PROCESS mode enabled; processing PR inline")
            # Run synchronously in-process
            try:
                result = process_pull_request.run(pr_data)
                return JSONResponse(status_code=200, content={"status": "processed", **(result or {})})
            except Exception as e:
                logger.error(f"Inline processing failed: {e}")
                raise HTTPException(status_code=500, detail="Processing failed")
        else:
            # Queue the PR for analysis via Celery
            task = process_pull_request.delay(pr_data)
            logger.info(f"Queued PR analysis task: {task.id}")
            return JSONResponse(
                status_code=202,
                content={
                    "status": "queued",
                    "task_id": task.id,
                    "action": action,
                    "pr_number": pr_data.get("number")
                }
            )
    else:
        logger.info(f"Ignoring PR action: {action}")
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "action": action}
        )


async def _handle_issue_comment_event(payload: dict, installation_id: int | None, db: Session) -> JSONResponse:
    """Handle issue comment events (for bot commands)"""
    
    action = payload.get("action")
    comment = payload.get("comment", {})
    issue = payload.get("issue", {})
    repository = payload.get("repository", {})
    
    # Only process created comments
    if action != "created":
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "action": action}
        )
    
    comment_body = comment.get("body", "")
    
    # Check if this is a bot command
    if "@prcopilot" not in comment_body.lower():
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "reason": "not_a_bot_command"}
        )
    
    # Parse the command
    command = _parse_bot_command(comment_body)
    
    if not command:
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "reason": "invalid_command"}
        )
    
    # Handle the command
    if command["action"] == "triage":
        return await _handle_triage_command(payload, installation_id, db)
    elif command["action"] == "help":
        return await _handle_help_command(payload, db)
    else:
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "reason": "unknown_command"}
        )


def _parse_bot_command(comment_body: str) -> dict:
    """Parse bot command from comment body"""
    
    lines = comment_body.lower().split('\n')
    
    for line in lines:
        if '@prcopilot' in line:
            # Look for command patterns
            if '/triage' in line:
                return {"action": "triage"}
            elif '/help' in line:
                return {"action": "help"}
    
    return None


async def _handle_triage_command(payload: dict, installation_id: int | None, db: Session) -> JSONResponse:
    """Handle @PRCoPilot /triage command"""
    
    issue = payload.get("issue", {})
    repository = payload.get("repository", {})
    
    # Check if this is a PR (not an issue)
    if not issue.get("pull_request"):
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "reason": "not_a_pr"}
        )
    
    # Get PR data (simplified for MVP)
    pr_data = {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "body": issue.get("body"),
        "state": issue.get("state"),
        "user": {"login": issue.get("user", {}).get("login")},
        "head": {"repo": {"full_name": repository.get("full_name")}},
        "additions": 0,
        "deletions": 0,
        "changed_files": 0,
        "commits": 0,
        "id": issue.get("id"),
        "_installation_id": installation_id,
    }
    
    if SINGLE_PROCESS:
        logger.info("SINGLE_PROCESS mode enabled; processing /triage inline")
        try:
            result = process_pull_request.run(pr_data)
            return JSONResponse(status_code=200, content={"status": "processed", **(result or {})})
        except Exception as e:
            logger.error(f"Inline processing failed: {e}")
            raise HTTPException(status_code=500, detail="Processing failed")
    else:
        # Queue re-analysis
        task = process_pull_request.delay(pr_data)
        logger.info(f"Queued re-analysis task for PR #{pr_data['number']}: {task.id}")
        return JSONResponse(
            status_code=202,
            content={
                "status": "queued",
                "task_id": task.id,
                "action": "re_analyze",
                "pr_number": pr_data["number"]
            }
        )


async def _handle_help_command(payload: dict, db: Session) -> JSONResponse:
    """Handle @PRCoPilot /help command"""
    
    logger.info("Help command received")
    return JSONResponse(
        status_code=200,
        content={
            "status": "help_posted",
            "message": "Help information would be posted as comment"
        }
    )
