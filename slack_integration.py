import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from database import db

logger = logging.getLogger(__name__)

class SlackIntegration:
    def __init__(self, webhook_url: Optional[str] = None, channel: str = "#general"):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.channel = channel
        self.enabled = bool(self.webhook_url)
        
        if self.enabled:
            logger.info("✅ Slack integration enabled")
        else:
            logger.warning("⚠️ Slack integration disabled - no webhook URL provided")
    
    async def send_message(self, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Send a message to Slack."""
        if not self.enabled:
            logger.warning("Slack integration disabled, skipping message")
            return False
        
        try:
            payload = {
                "channel": self.channel,
                "text": text
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                logger.info("✅ Slack message sent successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to send Slack message: {e}")
            return False
    
    async def send_question_notification(self, question: str, user_id: Optional[str] = None, 
                                       response_time_ms: Optional[int] = None, 
                                       success: bool = True) -> bool:
        """Send a notification about a new question."""
        if not self.enabled:
            return False
        
        # Create a simple message for question notifications
        status_emoji = "✅" if success else "❌"
        user_info = f" (User: {user_id})" if user_id else ""
        time_info = f" ({response_time_ms}ms)" if response_time_ms else ""
        
        text = f"{status_emoji} New PRIDE Question{user_info}{time_info}\n> {question}"
        
        return await self.send_message(text)
    
    async def send_daily_analytics(self, days: int = 1) -> bool:
        """Send daily analytics report to Slack."""
        if not self.enabled:
            return False
        
        try:
            # Get analytics data
            analytics = db.get_analytics(days)
            
            if not analytics or not analytics.get("overall_stats"):
                logger.warning("No analytics data available")
                return False
            
            stats = analytics["overall_stats"]
            
            # Create analytics message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 PRIDE MCP Server Analytics - Last {days} day(s)"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Questions:*\n{stats.get('total_questions', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Success Rate:*\n{self._calculate_success_rate(stats):.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Avg Response Time:*\n{stats.get('avg_response_time', 0):.0f}ms"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Unique Users:*\n{stats.get('unique_users', 0)}"
                        }
                    ]
                }
            ]
            
            # Add most common questions if available
            if analytics.get("common_questions"):
                questions_text = "\n".join([
                    f"• {q['question'][:50]}{'...' if len(q['question']) > 50 else ''} ({q['count']} times)"
                    for q in analytics["common_questions"][:5]
                ])
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Top Questions:*\n{questions_text}"
                    }
                })
            
            # Add timestamp
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            })
            
            return await self.send_message("Daily Analytics Report", blocks)
            
        except Exception as e:
            logger.error(f"❌ Failed to send daily analytics: {e}")
            return False
    
    async def send_error_notification(self, error_message: str, context: Optional[str] = None) -> bool:
        """Send error notification to Slack."""
        if not self.enabled:
            return False
        
        text = f"🚨 PRIDE MCP Server Error\n\n*Error:* {error_message}"
        if context:
            text += f"\n*Context:* {context}"
        
        return await self.send_message(text)
    
    async def send_system_status(self, status: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Send system status update to Slack."""
        if not self.enabled:
            return False
        
        emoji_map = {
            "online": "🟢",
            "offline": "🔴",
            "warning": "🟡",
            "maintenance": "🔧"
        }
        
        emoji = emoji_map.get(status.lower(), "ℹ️")
        text = f"{emoji} PRIDE MCP Server Status: {status.upper()}"
        
        if details:
            details_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
            text += f"\n\n*Details:*\n{details_text}"
        
        return await self.send_message(text)
    
    def _calculate_success_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate success rate from stats."""
        total = stats.get('total_questions', 0)
        successful = stats.get('successful_questions', 0)
        
        if total == 0:
            return 0.0
        
        return (successful / total) * 100

# Global Slack instance
slack = SlackIntegration() 