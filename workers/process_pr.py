"""
Background task for processing pull requests
"""

from celery import current_task
from workers.celery_app import celery_app
from api.services.classifier import PRClassifier
from api.services.github_client import GitHubClient
from api.database import SessionLocal, PullRequest, Repository
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_pull_request(self, pr_data: dict):
    """
    Process a pull request: analyze, classify, and post results
    
    Args:
        pr_data: GitHub PR webhook payload
    """
    try:
        # Extract PR information
        pr_number = pr_data["number"]
        repo_full_name = pr_data["head"]["repo"]["full_name"]
        pr_id = pr_data["id"]
        
        logger.info(f"Processing PR #{pr_number} in {repo_full_name}")
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Check if we've already analyzed this PR
            existing_pr = db.query(PullRequest).filter(
                PullRequest.github_pr_id == pr_id
            ).first()
            
            if existing_pr:
                logger.info(f"PR {pr_id} already analyzed, skipping")
                return {"status": "skipped", "reason": "already_analyzed"}
            
            # Initialize services
            classifier = PRClassifier()
            github_client = GitHubClient()
            
            # Get additional PR context from GitHub API
            pr_context = github_client.get_pr_context(repo_full_name, pr_number)
            
            # Classify the PR
            analysis_result = classifier.classify_pr(pr_data, pr_context)
            
            # Save to database
            pr_record = PullRequest(
                github_pr_id=pr_id,
                repository_full_name=repo_full_name,
                pr_number=pr_number,
                title=pr_data["title"],
                description=pr_data["body"] or "",
                author=pr_data["user"]["login"],
                state=pr_data["state"],
                classification=analysis_result["classification"],
                confidence=analysis_result["confidence"],
                priority_score=analysis_result["priority_score"],
                reasoning=analysis_result["reasoning"],
                suggested_action=analysis_result["suggested_action"]
            )
            
            db.add(pr_record)
            db.commit()
            
            # Post comment to GitHub PR
            comment_body = _format_analysis_comment(analysis_result)
            github_client.post_pr_comment(repo_full_name, pr_number, comment_body)
            
            logger.info(f"Successfully processed PR #{pr_number}")
            
            return {
                "status": "success",
                "pr_number": pr_number,
                "classification": analysis_result["classification"],
                "priority_score": analysis_result["priority_score"]
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing PR: {str(e)}")
        # Re-raise for Celery to handle retry logic
        raise self.retry(exc=e, countdown=60, max_retries=3)


def _format_analysis_comment(analysis_result: dict) -> str:
    """Format analysis results into a GitHub comment"""
    
    classification_emoji = {
        "Ready to Merge": "✅",
        "Needs Architecture Discussion": "🏗️",
        "Needs Minor Fixes": "🔧",
        "Needs Mentor Support": "👥",
        "Needs Maintainer Decision": "🤔",
        "Blocked/Stale": "⏸️"
    }
    
    emoji = classification_emoji.get(analysis_result["classification"], "🤖")
    
    comment = f"""## {emoji} PR Copilot Analysis

**Classification:** {analysis_result['classification']}
**Priority Score:** {analysis_result['priority_score']}/100
**Confidence:** {analysis_result['confidence']:.1%}

### Reasoning
{analysis_result['reasoning']}

### Suggested Action
{analysis_result['suggested_action']}

---
*Powered by [PR Copilot](https://github.com/your-org/pr-copilot) - AI-Powered PR Management*

Use `@PRCoPilot /triage` to re-analyze this PR.
"""
    
    return comment
