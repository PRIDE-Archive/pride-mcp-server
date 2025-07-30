from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from database import db
from slack_integration import slack

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter(prefix="/api", tags=["analytics"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PRIDE MCP Server"
    }

@api_router.get("/questions")
async def get_questions(
    limit: int = Query(100, ge=1, le=1000, description="Number of questions to return"),
    offset: int = Query(0, ge=0, description="Number of questions to skip"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get questions from the database."""
    try:
        questions = db.get_questions(
            limit=limit,
            offset=offset,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "questions": questions,
            "total": len(questions),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve questions")

@api_router.get("/analytics")
async def get_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """Get analytics data."""
    try:
        analytics = db.get_analytics(days=days)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No analytics data available")
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@api_router.get("/analytics/daily")
async def get_daily_analytics(
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)")
):
    """Get analytics for a specific day."""
    try:
        if date:
            # Get data for specific date
            questions = db.get_questions(
                limit=1000,
                start_date=date,
                end_date=date
            )
            
            if not questions:
                raise HTTPException(status_code=404, detail=f"No data found for {date}")
            
            # Calculate stats for the day
            total_questions = len(questions)
            successful_questions = sum(1 for q in questions if q.get('success', True))
            response_times = [q.get('response_time_ms', 0) for q in questions if q.get('response_time_ms')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            unique_users = len(set(q.get('user_id') for q in questions if q.get('user_id')))
            
            return {
                "date": date,
                "total_questions": total_questions,
                "successful_questions": successful_questions,
                "success_rate": (successful_questions / total_questions * 100) if total_questions > 0 else 0,
                "avg_response_time_ms": avg_response_time,
                "unique_users": unique_users,
                "questions": questions
            }
        else:
            # Get today's data
            today = datetime.now().strftime('%Y-%m-%d')
            return await get_daily_analytics(date=today)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve daily analytics")

@api_router.post("/questions")
async def store_question(
    question: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    tools_called: Optional[List[str]] = None,
    response_length: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Store a question in the database."""
    try:
        question_id = db.store_question(
            question=question,
            user_id=user_id,
            session_id=session_id,
            response_time_ms=response_time_ms,
            tools_called=tools_called,
            response_length=response_length,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
        
        # Send Slack notification if enabled
        await slack.send_question_notification(
            question=question,
            user_id=user_id,
            response_time_ms=response_time_ms,
            success=success
        )
        
        return {
            "id": question_id,
            "status": "stored",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to store question: {e}")
        raise HTTPException(status_code=500, detail="Failed to store question")

@api_router.get("/stats")
async def get_stats():
    """Get current system statistics."""
    try:
        # Get today's stats
        today = datetime.now().strftime('%Y-%m-%d')
        today_questions = db.get_questions(
            limit=1000,
            start_date=today,
            end_date=today
        )
        
        # Get this week's stats
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        week_questions = db.get_questions(
            limit=1000,
            start_date=week_ago
        )
        
        # Calculate stats
        today_total = len(today_questions)
        today_successful = sum(1 for q in today_questions if q.get('success', True))
        week_total = len(week_questions)
        week_successful = sum(1 for q in week_questions if q.get('success', True))
        
        # Get response times
        today_response_times = [q.get('response_time_ms', 0) for q in today_questions if q.get('response_time_ms')]
        week_response_times = [q.get('response_time_ms', 0) for q in week_questions if q.get('response_time_ms')]
        
        return {
            "today": {
                "total_questions": today_total,
                "successful_questions": today_successful,
                "success_rate": (today_successful / today_total * 100) if today_total > 0 else 0,
                "avg_response_time_ms": sum(today_response_times) / len(today_response_times) if today_response_times else 0,
                "unique_users": len(set(q.get('user_id') for q in today_questions if q.get('user_id')))
            },
            "this_week": {
                "total_questions": week_total,
                "successful_questions": week_successful,
                "success_rate": (week_successful / week_total * 100) if week_total > 0 else 0,
                "avg_response_time_ms": sum(week_response_times) / len(week_response_times) if week_response_times else 0,
                "unique_users": len(set(q.get('user_id') for q in week_questions if q.get('user_id')))
            },
            "system": {
                "database_status": "connected",
                "slack_integration": slack.enabled,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@api_router.post("/slack/test")
async def test_slack_integration():
    """Test Slack integration."""
    try:
        success = await slack.send_message("🧪 Test message from PRIDE MCP Server")
        
        if success:
            return {"status": "success", "message": "Slack message sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send Slack message")
    except Exception as e:
        logger.error(f"Slack test failed: {e}")
        raise HTTPException(status_code=500, detail="Slack integration test failed")

@api_router.post("/slack/analytics")
async def send_analytics_to_slack(
    days: int = Query(1, ge=1, le=30, description="Number of days to include in report")
):
    """Send analytics report to Slack."""
    try:
        success = await slack.send_daily_analytics(days=days)
        
        if success:
            return {"status": "success", "message": "Analytics report sent to Slack"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send analytics to Slack")
    except Exception as e:
        logger.error(f"Failed to send analytics to Slack: {e}")
        raise HTTPException(status_code=500, detail="Failed to send analytics report")

@api_router.get("/export/questions")
async def export_questions(
    format: str = Query("json", description="Export format (json, csv)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Export questions data."""
    try:
        questions = db.get_questions(
            limit=10000,  # Large limit for export
            start_date=start_date,
            end_date=end_date
        )
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'id', 'question', 'user_id', 'session_id', 'timestamp', 
                'response_time_ms', 'tools_called', 'response_length', 
                'success', 'error_message'
            ])
            
            writer.writeheader()
            for question in questions:
                # Clean up the data for CSV
                clean_question = {
                    'id': question.get('id'),
                    'question': question.get('question', ''),
                    'user_id': question.get('user_id', ''),
                    'session_id': question.get('session_id', ''),
                    'timestamp': question.get('timestamp', ''),
                    'response_time_ms': question.get('response_time_ms', ''),
                    'tools_called': question.get('tools_called', ''),
                    'response_length': question.get('response_length', ''),
                    'success': question.get('success', ''),
                    'error_message': question.get('error_message', '')
                }
                writer.writerow(clean_question)
            
            return JSONResponse(
                content={"csv_data": output.getvalue()},
                headers={"Content-Disposition": "attachment; filename=questions_export.csv"}
            )
        else:
            return {
                "questions": questions,
                "total": len(questions),
                "export_date": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to export questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to export questions") 