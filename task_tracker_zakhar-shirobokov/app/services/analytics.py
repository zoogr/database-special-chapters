from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any
from app.models.task import Task, TaskStatus
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_statistics(self) -> Dict[str, Any]:
        total_tasks = self.db.query(Task).count()
        
        status_counts = dict(
            self.db.query(Task.status, func.count(Task.id))
            .group_by(Task.status)
            .all()
        )
        
        assignee_stats = (
            self.db.query(Task.assignee_id, func.count(Task.id))
            .filter(Task.assignee_id.isnot(None))
            .group_by(Task.assignee_id)
            .all()
        )
        
        recent_tasks = (
            self.db.query(Task)
            .filter(Task.created_at >= datetime.now() - timedelta(days=7))
            .count()
        )
        
        return {
            "total_tasks": total_tasks,
            "by_status": {status.value: count for status, count in status_counts.items()},
            "by_assignee": {str(assignee_id): count for assignee_id, count in assignee_stats},
            "recent_week": recent_tasks,
            "completion_rate": (status_counts.get(TaskStatus.DONE, 0) / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def create_status_chart(self) -> str:
        stats = self.get_statistics()
        
        df = pd.DataFrame({
            'status': list(stats['by_status'].keys()),
            'count': list(stats['by_status'].values())
        })
        
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df, x='status', y='count', palette='viridis')
        plt.title('Tasks by Status')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = '/tmp/status_chart.png'
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    
    def get_dataframe(self) -> pd.DataFrame:
        tasks = self.db.query(Task).all()
        
        data = [{
            'id': task.id,
            'title': task.title,
            'status': task.status.value,
            'assignee_id': task.assignee_id,
            'created_at': task.created_at,
            'due_date': task.due_date
        } for task in tasks]
        
        return pd.DataFrame(data)