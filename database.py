import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuestionDatabase:
    def __init__(self, db_path: Optional[str] = None):
        # Use environment variable if available, otherwise default
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'pride_questions.db')
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create questions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        response_time_ms INTEGER,
                        tools_called TEXT,
                        response_length INTEGER,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        metadata TEXT
                    )
                """)
                
                # Create analytics table for aggregated data
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        total_questions INTEGER DEFAULT 0,
                        successful_questions INTEGER DEFAULT 0,
                        avg_response_time_ms REAL DEFAULT 0,
                        most_common_questions TEXT,
                        unique_users INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_timestamp ON questions(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)")
                
                conn.commit()
                logger.info(f"✅ Database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def store_question(self, question: str, user_id: Optional[str] = None, 
                      session_id: Optional[str] = None, response_time_ms: Optional[int] = None,
                      tools_called: Optional[List[str]] = None, response_length: Optional[int] = None,
                      success: bool = True, error_message: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a question and its metadata in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO questions (
                        question, user_id, session_id, response_time_ms, 
                        tools_called, response_length, success, error_message, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    question,
                    user_id,
                    session_id,
                    response_time_ms,
                    json.dumps(tools_called) if tools_called else None,
                    response_length,
                    success,
                    error_message,
                    json.dumps(metadata) if metadata else None
                ))
                
                question_id = cursor.lastrowid
                conn.commit()
                logger.info(f"✅ Question stored with ID: {question_id}")
                return question_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store question: {e}")
            raise
    
    def get_questions(self, limit: int = 100, offset: int = 0, 
                     user_id: Optional[str] = None, 
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve questions with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM questions WHERE 1=1"
                params = []
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if start_date:
                    query += " AND DATE(timestamp) >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(timestamp) <= ?"
                    params.append(end_date)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve questions: {e}")
            return []
    
    def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics data for the specified number of days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get daily analytics
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as total_questions,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_questions,
                        AVG(response_time_ms) as avg_response_time,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM questions 
                    WHERE timestamp >= DATE('now', '-{} days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """.format(days))
                
                daily_stats = [dict(row) for row in cursor.fetchall()]
                
                # Get overall stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_questions,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_questions,
                        AVG(response_time_ms) as avg_response_time,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM questions 
                    WHERE timestamp >= DATE('now', '-{} days')
                """.format(days))
                
                overall_stats = dict(cursor.fetchone())
                
                # Get most common questions
                cursor.execute("""
                    SELECT question, COUNT(*) as count
                    FROM questions 
                    WHERE timestamp >= DATE('now', '-{} days')
                    GROUP BY question
                    ORDER BY count DESC
                    LIMIT 10
                """.format(days))
                
                common_questions = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "daily_stats": daily_stats,
                    "overall_stats": overall_stats,
                    "common_questions": common_questions,
                    "period_days": days
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get analytics: {e}")
            return {}
    
    def update_analytics(self):
        """Update the analytics table with aggregated data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get today's date
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Check if analytics for today already exists
                cursor.execute("SELECT id FROM analytics WHERE date = ?", (today,))
                existing = cursor.fetchone()
                
                # Calculate today's stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_questions,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_questions,
                        AVG(response_time_ms) as avg_response_time,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM questions 
                    WHERE DATE(timestamp) = ?
                """, (today,))
                
                stats = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute("""
                        UPDATE analytics 
                        SET total_questions = ?, successful_questions = ?, 
                            avg_response_time_ms = ?, unique_users = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE date = ?
                    """, (stats[0], stats[1], stats[2], stats[3], today))
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO analytics (
                            date, total_questions, successful_questions, 
                            avg_response_time_ms, unique_users
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (today, stats[0], stats[1], stats[2], stats[3]))
                
                conn.commit()
                logger.info(f"✅ Analytics updated for {today}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update analytics: {e}")

# Global database instance
db = QuestionDatabase() 