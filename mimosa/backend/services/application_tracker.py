from datetime import datetime, timedelta
from typing import List, Dict
import json
import os

class ApplicationTrackerService:
    def __init__(self):
        self.data_path = "./data/applications.json"
        self.applications = self._load_applications()

    def _load_applications(self) -> List[Dict]:
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_applications(self):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, ensure_ascii=False, indent=2)

    def create_application(self, user_id: str, resume_id: int, job_id: int, notes: str = None) -> Dict:
        application = {
            'id': len(self.applications) + 1,
            'user_id': user_id,
            'resume_id': resume_id,
            'job_id': job_id,
            'status': 'applied',
            'applied_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'notes': notes or '',
            'interview_schedule': None
        }
        self.applications.append(application)
        self._save_applications()
        return application

    def get_user_applications(self, user_id: str) -> List[Dict]:
        return [app for app in self.applications if app['user_id'] == user_id]

    def update_application_status(self, application_id: int, status: str):
        for app in self.applications:
            if app['id'] == application_id:
                app['status'] = status
                app['last_updated'] = datetime.utcnow().isoformat()
                self._save_applications()
                return True
        return False

    def add_interview_schedule(self, application_id: int, date: str, time: str, location: str):
        for app in self.applications:
            if app['id'] == application_id:
                app['interview_schedule'] = {
                    'date': date,
                    'time': time,
                    'location': location
                }
                app['last_updated'] = datetime.utcnow().isoformat()
                self._save_applications()
                return True
        return False

    def get_pending_followups(self, days_threshold: int = 3) -> List[Dict]:
        pending = []
        threshold_date = (datetime.utcnow() - timedelta(days=days_threshold)).isoformat()
        
        for app in self.applications:
            if app['status'] == 'applied' and app['applied_at'] < threshold_date:
                pending.append(app)
        
        return pending

    def delete_application(self, application_id: int) -> bool:
        for i, app in enumerate(self.applications):
            if app['id'] == application_id:
                del self.applications[i]
                self._save_applications()
                return True
        return False

    def get_application_stats(self, user_id: str) -> Dict:
        user_apps = self.get_user_applications(user_id)
        stats = {
            'total_applied': len(user_apps),
            'status_distribution': {
                'applied': 0,
                'interview': 0,
                'offer': 0,
                'rejected': 0
            },
            'recent_applications': []
        }
        
        for app in user_apps:
            status = app['status']
            if status in stats['status_distribution']:
                stats['status_distribution'][status] += 1
        
        user_apps.sort(key=lambda x: x['applied_at'], reverse=True)
        stats['recent_applications'] = user_apps[:5]
        
        return stats