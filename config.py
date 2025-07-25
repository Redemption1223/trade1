import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY') 
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # App configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    APP_NAME = "Task Manager API"
    APP_VERSION = "1.0.0"
    
    # API configuration
    API_VERSION = "v1"
    MAX_TASKS_PER_REQUEST = 100
    
    # CORS configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "https://your-frontend-domain.com",
        "*"  # Remove this in production
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")
        
        return True

# Database table schemas for reference
TASKS_SCHEMA = """
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on created_at for better performance
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Create an index on completed status
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Enable Row Level Security (RLS)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (adjust as needed)
CREATE POLICY "Allow all operations on tasks" ON tasks
FOR ALL USING (true);
"""

# Sample data for testing
SAMPLE_DATA = [
    {
        "title": "Setup Supabase Database",
        "description": "Create tables and configure RLS policies",
        "completed": True
    },
    {
        "title": "Build Streamlit Backend", 
        "description": "Create API endpoints for task management",
        "completed": True
    },
    {
        "title": "Create HTML Frontend",
        "description": "Build responsive UI that calls the Streamlit API",
        "completed": False
    },
    {
        "title": "Deploy to Production",
        "description": "Deploy backend to Streamlit Cloud and frontend to hosting service",
        "completed": False
    },
    {
        "title": "Add User Authentication",
        "description": "Implement user login and authorization",
        "completed": False
    }
]
