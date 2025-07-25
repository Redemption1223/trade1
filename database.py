import streamlit as st
import requests
import json
from typing import List, Dict, Optional

class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client with credentials from Streamlit secrets"""
        try:
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["key"]
            self.service_key = st.secrets["supabase"].get("service_key", self.key)
            
            self.headers = {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            self.admin_headers = {
                "apikey": self.service_key,
                "Authorization": f"Bearer {self.service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
        except KeyError as e:
            st.error(f"Missing Supabase configuration: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, use_admin: bool = False) -> requests.Response:
        """Make HTTP request to Supabase API"""
        url = f"{self.url}/rest/v1/{endpoint}"
        headers = self.admin_headers if use_admin else self.headers
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            st.error(f"Database request failed: {e}")
            raise
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks from the database"""
        try:
            response = self._make_request("GET", "tasks?order=created_at.desc")
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch tasks: {e}")
            return []
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID"""
        try:
            response = self._make_request("GET", f"tasks?id=eq.{task_id}")
            tasks = response.json()
            return tasks[0] if tasks else None
        except Exception as e:
            st.error(f"Failed to fetch task {task_id}: {e}")
            return None
    
    def create_task(self, title: str, description: str = "") -> Dict:
        """Create a new task"""
        data = {
            "title": title,
            "description": description,
            "completed": False
        }
        
        try:
            response = self._make_request("POST", "tasks", data)
            created_task = response.json()
            return created_task[0] if isinstance(created_task, list) else created_task
        except Exception as e:
            st.error(f"Failed to create task: {e}")
            raise
    
    def update_task(self, task_id: int, title: str, description: str = "", completed: bool = False) -> Dict:
        """Update an existing task"""
        data = {
            "title": title,
            "description": description,
            "completed": completed
        }
        
        try:
            response = self._make_request("PATCH", f"tasks?id=eq.{task_id}", data)
            updated_task = response.json()
            return updated_task[0] if isinstance(updated_task, list) else updated_task
        except Exception as e:
            st.error(f"Failed to update task {task_id}: {e}")
            raise
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            self._make_request("DELETE", f"tasks?id=eq.{task_id}")
            return True
        except Exception as e:
            st.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def get_task_stats(self) -> Dict:
        """Get task statistics"""
        try:
            tasks = self.get_all_tasks()
            total = len(tasks)
            completed = len([task for task in tasks if task.get('completed', False)])
            pending = total - completed
            
            return {
                "total": total,
                "completed": completed,
                "pending": pending,
                "completion_rate": (completed / total * 100) if total > 0 else 0
            }
        except Exception as e:
            st.error(f"Failed to get task statistics: {e}")
            return {"total": 0, "completed": 0, "pending": 0, "completion_rate": 0}
    
    def search_tasks(self, query: str) -> List[Dict]:
        """Search tasks by title or description"""
        try:
            # Using ilike for case-insensitive search
            endpoint = f"tasks?or=(title.ilike.*{query}*,description.ilike.*{query}*)&order=created_at.desc"
            response = self._make_request("GET", endpoint)
            return response.json()
        except Exception as e:
            st.error(f"Failed to search tasks: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            response = self._make_request("GET", "tasks?limit=1")
            return True
        except Exception as e:
            st.error(f"Database connection test failed: {e}")
            return False

# Utility functions for Streamlit
@st.cache_data(ttl=30)  # Cache for 30 seconds
def cached_get_tasks():
    """Cached version of get_all_tasks for better performance"""
    db = SupabaseClient()
    return db.get_all_tasks()

@st.cache_data(ttl=60)  # Cache for 1 minute
def cached_get_stats():
    """Cached version of get_task_stats for better performance"""
    db = SupabaseClient()
    return db.get_task_stats()
