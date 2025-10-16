"""
PR Classification Service - Core AI logic for analyzing and categorizing PRs
"""

import json
import logging
from typing import Dict, Any
import os

from openai import OpenAI

logger = logging.getLogger(__name__)


class PRClassifier:
    """Handles PR classification and priority scoring using OpenAI"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
    
    def classify_pr(self, pr_data: dict, pr_context: dict = None) -> Dict[str, Any]:
        """
        Analyze and classify a pull request
        
        Args:
            pr_data: GitHub PR webhook payload
            pr_context: Additional context from GitHub API
            
        Returns:
            Dictionary with classification results
        """
        
        # Prepare PR data for analysis
        analysis_data = self._prepare_pr_data(pr_data, pr_context)
        
        # Create the classification prompt
        prompt = self._create_classification_prompt(analysis_data)
        
        try:
            # Call OpenAI API (v1 SDK)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a PR triage expert with deep knowledge of software development workflows. Analyze pull requests and provide structured, actionable insights.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=1000,
            )
            
            content = response.choices[0].message.content or "{}"
            result = json.loads(content)
            
            # Validate and clean the result
            validated_result = self._validate_result(result)
            
            logger.info(f"Successfully classified PR: {validated_result['classification']}")
            return validated_result
            
        except Exception as e:
            logger.error(f"Error classifying PR: {str(e)}")
            # Return a fallback classification
            return self._get_fallback_classification(pr_data)
    
    def _prepare_pr_data(self, pr_data: dict, pr_context: dict = None) -> dict:
        """Prepare PR data for analysis"""
        
        # Extract basic PR information
        basic_info = {
            "title": pr_data.get("title", ""),
            "description": pr_data.get("body", "") or "",
            "author": pr_data.get("user", {}).get("login", ""),
            "state": pr_data.get("state", ""),
            "draft": pr_data.get("draft", False),
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "changed_files": pr_data.get("changed_files", 0),
            "commits": pr_data.get("commits", 0),
        }
        
        # Add context if available
        if pr_context:
            basic_info.update({
                "has_conflicts": pr_context.get("mergeable", True) is False,
                "ci_status": pr_context.get("ci_status", "unknown"),
                "review_count": pr_context.get("review_count", 0),
                "author_contributions": pr_context.get("author_contributions", 0),
                "days_since_created": pr_context.get("days_since_created", 0),
            })
        
        return basic_info
    
    def _create_classification_prompt(self, pr_data: dict) -> str:
        """Create the classification prompt for the LLM"""
        
        return f"""Analyze this GitHub pull request and classify it according to the categories below.

PR Details:
- Title: {pr_data['title']}
- Description: {pr_data.get('description', 'No description')}
- Author: {pr_data['author']} (Contributions: {pr_data.get('author_contributions', 'Unknown')})
- Changes: +{pr_data['additions']} additions, -{pr_data['deletions']} deletions
- Files changed: {pr_data['changed_files']}
- Commits: {pr_data['commits']}
- Draft: {pr_data.get('draft', False)}
- Has conflicts: {pr_data.get('has_conflicts', False)}
- CI Status: {pr_data.get('ci_status', 'Unknown')}
- Reviews: {pr_data.get('review_count', 0)}
- Days since created: {pr_data.get('days_since_created', 0)}

Classify this PR into ONE of these categories:

1. **Ready to Merge** - All checks pass, trusted contributor, no major issues
2. **Needs Architecture Discussion** - Large changes, breaking changes, or architectural decisions needed
3. **Needs Minor Fixes** - Small issues like formatting, tests, documentation, or minor bugs
4. **Needs Mentor Support** - First-time contributor or needs guidance
5. **Needs Maintainer Decision** - Policy questions, roadmap decisions, or maintainer input needed
6. **Blocked/Stale** - Has conflicts, failing CI, inactive for >14 days, or other blockers

Also assign a priority score (0-100) based on:
- Security/bug fixes: High priority (70-100)
- Feature additions: Medium priority (40-70)
- Documentation/typos: Low priority (0-40)
- Consider impact, urgency, and maintainer workload

Provide your analysis in this exact JSON format:
{
  "classification": "exact category name",
  "confidence": 0.85,
  "priority_score": 75,
  "reasoning": "Brief explanation of why this classification was chosen",
  "suggested_action": "Specific action the maintainer should take next"
}"""
    
    def _validate_result(self, result: dict) -> dict:
        """Validate and clean the classification result"""
        
        valid_classifications = [
            "Ready to Merge",
            "Needs Architecture Discussion", 
            "Needs Minor Fixes",
            "Needs Mentor Support",
            "Needs Maintainer Decision",
            "Blocked/Stale"
        ]
        
        # Ensure classification is valid
        if result.get("classification") not in valid_classifications:
            result["classification"] = "Needs Minor Fixes"  # Safe default
        
        # Ensure confidence is between 0 and 1
        confidence = result.get("confidence", 0.5)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.5
        result["confidence"] = max(0.0, min(1.0, confidence))
        
        # Ensure priority score is between 0 and 100
        priority = result.get("priority_score", 50)
        try:
            priority = int(priority)
        except Exception:
            priority = 50
        result["priority_score"] = max(0, min(100, priority))
        
        # Ensure required fields exist
        result["reasoning"] = result.get("reasoning", "Analysis completed")
        result["suggested_action"] = result.get("suggested_action", "Review and take appropriate action")
        
        return result
    
    def _get_fallback_classification(self, pr_data: dict) -> dict:
        """Provide a fallback classification when AI analysis fails"""
        
        # Simple heuristic-based fallback
        is_draft = pr_data.get("draft", False)
        has_conflicts = pr_data.get("mergeable", True) is False
        additions = pr_data.get("additions", 0)
        
        if is_draft:
            classification = "Needs Minor Fixes"
            priority = 20
        elif has_conflicts:
            classification = "Blocked/Stale"
            priority = 80
        elif additions > 500:
            classification = "Needs Architecture Discussion"
            priority = 60
        else:
            classification = "Ready to Merge"
            priority = 50
        
        return {
            "classification": classification,
            "confidence": 0.3,  # Low confidence for fallback
            "priority_score": priority,
            "reasoning": "Fallback classification due to analysis error",
            "suggested_action": "Manual review recommended"
        }
