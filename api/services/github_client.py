"""
GitHub API Client - Handles all GitHub API interactions
"""

import os
import jwt
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from github import Github, GithubIntegration
import httpx

logger = logging.getLogger(__name__)


class GitHubClient:
    """Handles GitHub API interactions including authentication and webhook processing"""
    
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        
        if not all([self.app_id, self.private_key_path]):
            raise ValueError("GitHub App configuration missing")
        
        # Load private key
        with open(self.private_key_path, 'r') as key_file:
            self.private_key = key_file.read()
    
    def get_installation_token(self, installation_id: str) -> str:
        """Generate JWT token for GitHub App installation"""
        
        # Create JWT token
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Issued at time (1 minute ago)
            'exp': now + 600,  # Expires in 10 minutes
            'iss': self.app_id  # Issuer
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        
        # Get installation access token
        integration = GithubIntegration(self.app_id, self.private_key)
        auth = integration.get_access_token(installation_id)
        
        return auth.token
    
    def get_github_client(self, installation_id: str) -> Github:
        """Get authenticated GitHub client for an installation"""
        token = self.get_installation_token(installation_id)
        return Github(token)
    
    async def get_pr_context(self, repo_full_name: str, pr_number: int) -> Dict[str, Any]:
        """Get additional context for a PR from GitHub API"""
        
        # For MVP, we'll use a simplified approach
        # In production, you'd need to track installation IDs per repository
        
        try:
            # This is a simplified version - in production you'd need proper installation handling
            # For now, return basic context that can be extracted from webhook data
            return {
                "ci_status": "unknown",
                "review_count": 0,
                "author_contributions": 0,
                "days_since_created": 0,
                "has_conflicts": False
            }
        except Exception as e:
            logger.error(f"Error getting PR context: {str(e)}")
            return {}
    
    async def post_pr_comment(self, repo_full_name: str, pr_number: int, comment_body: str) -> bool:
        """Post a comment to a GitHub PR"""
        
        try:
            # This is a simplified version for MVP
            # In production, you'd need proper installation handling
            logger.info(f"Would post comment to {repo_full_name}#{pr_number}")
            logger.info(f"Comment: {comment_body[:200]}...")
            
            # For MVP, we'll just log the comment
            # In production, implement actual GitHub API call here
            return True
            
        except Exception as e:
            logger.error(f"Error posting PR comment: {str(e)}")
            return False
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        
        if not self.webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True
        
        try:
            import hmac
            import hashlib
            
            expected_signature = 'sha256=' + hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    def parse_webhook_payload(self, payload: dict) -> Dict[str, Any]:
        """Parse and validate GitHub webhook payload"""
        
        event_type = payload.get("action")
        pr_data = payload.get("pull_request", {})
        
        if not pr_data:
            raise ValueError("No pull_request data in webhook payload")
        
        return {
            "event_type": event_type,
            "pr_data": pr_data,
            "repository": payload.get("repository", {}),
            "installation": payload.get("installation", {})
        }
