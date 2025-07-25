import streamlit as st
import json
import requests
from urllib.parse import parse_qs
from database import SupabaseClient
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Task Manager API",
    page_icon="📋",
    layout="wide"
)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    return SupabaseClient()

db = init_supabase()

# CORS headers for API responses
def set_cors_headers():
    st.markdown("""
    <script>
    // Set CORS headers
    if (window.parent) {
        window.parent.postMessage({type: 'cors', headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }}, '*');
    }
    </script>
    """, unsafe_allow_html=True)

# Get query parameters
query_params = st.experimental_get_query_params()

# API endpoint handling
if 'api' in query_params:
    set_cors_headers()
    api_endpoint = query_params['api'][0]
    
    # Get all tasks
    if api_endpoint == 'tasks':
        try:
            tasks = db.get_all_tasks()
            response = {
                "status": "success",
                "data": tasks
            }
            st.json(response)
            st.stop()
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            st.stop()
    
    # Get specific task
    elif api_endpoint == 'task':
        try:
            task_id = query_params.get('id', [None])[0]
            if task_id:
                task = db.get_task(int(task_id))
                response = {
                    "status": "success",
                    "data": task
                }
                st.json(response)
            else:
                st.json({"status": "error", "message": "Task ID required"})
            st.stop()
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            st.stop()
    
    # Create task
    elif api_endpoint == 'create_task':
        try:
            # For GET requests with parameters
            title = query_params.get('title', [None])[0]
            description = query_params.get('description', [''])[0]
            
            if title:
                task = db.create_task(title, description)
                response = {
                    "status": "success",
                    "data": task,
                    "message": "Task created successfully"
                }
                st.json(response)
            else:
                st.json({"status": "error", "message": "Title is required"})
            st.stop()
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            st.stop()
    
    # Update task
    elif api_endpoint == 'update_task':
        try:
            task_id = query_params.get('id', [None])[0]
            title = query_params.get('title', [None])[0]
            description = query_params.get('description', [''])[0]
            completed = query_params.get('completed', ['false'])[0].lower() == 'true'
            
            if task_id and title:
                task = db.update_task(int(task_id), title, description, completed)
                response = {
                    "status": "success",
                    "data": task,
                    "message": "Task updated successfully"
                }
                st.json(response)
            else:
                st.json({"status": "error", "message": "Task ID and title are required"})
            st.stop()
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            st.stop()
    
    # Delete task
    elif api_endpoint == 'delete_task':
        try:
            task_id = query_params.get('id', [None])[0]
            if task_id:
                success = db.delete_task(int(task_id))
                if success:
                    response = {
                        "status": "success",
                        "message": "Task deleted successfully"
                    }
                else:
                    response = {
                        "status": "error",
                        "message": "Failed to delete task"
                    }
                st.json(response)
            else:
                st.json({"status": "error", "message": "Task ID required"})
            st.stop()
        except Exception as e:
            st.json({"status": "error", "message": str(e)})
            st.stop()
    
    # Health check
    elif api_endpoint == 'health':
        st.json({
            "status": "success",
            "message": "API is running",
            "timestamp": pd.Timestamp.now().isoformat()
        })
        st.stop()

# Regular Streamlit Web App Interface
else:
    st.title("📋 Task Manager")
    st.markdown("---")
    
    # Sidebar for API info
    with st.sidebar:
        st.header("API Endpoints")
        st.markdown("""
        **Available endpoints:**
        - `?api=tasks` - Get all tasks
        - `?api=task&id=1` - Get specific task
        - `?api=create_task&title=...&description=...` - Create task
        - `?api=update_task&id=1&title=...&description=...&completed=true` - Update task
        - `?api=delete_task&id=1` - Delete task
        - `?api=health` - Health check
        """)
        
        st.markdown("---")
        
        # App URL for frontend
        st.subheader("Frontend Integration")
        app_url = st.text_input("Your Streamlit App URL:", 
                                placeholder="https://your-app.streamlit.app")
        if app_url:
            st.code(f"""
// JavaScript example
const API_BASE = '{app_url}';
fetch(`${{API_BASE}}/?api=tasks`)
  .then(response => response.json())
  .then(data => console.log(data));
            """)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create New Task")
        with st.form("create_task"):
            title = st.text_input("Title*")
            description = st.text_area("Description")
            
            if st.form_submit_button("Create Task"):
                if title:
                    try:
                        task = db.create_task(title, description)
                        st.success(f"Task created: {task['title']}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Title is required")
    
    with col2:
        st.subheader("Task Statistics")
        try:
            tasks = db.get_all_tasks()
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get('completed', False)])
            pending_tasks = total_tasks - completed_tasks
            
            st.metric("Total Tasks", total_tasks)
            st.metric("Completed", completed_tasks)
            st.metric("Pending", pending_tasks)
            
            if total_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
    
    # Display tasks
    st.subheader("All Tasks")
    
    try:
        tasks = db.get_all_tasks()
        
        if tasks:
            for task in tasks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        status = "✅" if task.get('completed', False) else "⏳"
                        st.write(f"{status} **{task['title']}**")
                        if task.get('description'):
                            st.write(f"_{task['description']}_")
                    
                    with col2:
                        created = pd.to_datetime(task['created_at'])
                        st.write(f"Created: {created.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col3:
                        if st.button("Toggle", key=f"toggle_{task['id']}"):
                            try:
                                new_status = not task.get('completed', False)
                                db.update_task(
                                    task['id'], 
                                    task['title'], 
                                    task.get('description', ''), 
                                    new_status
                                )
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{task['id']}"):
                            try:
                                db.delete_task(task['id'])
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    st.markdown("---")
        else:
            st.info("No tasks found. Create your first task!")
            
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        st.info("Make sure your Supabase connection is configured correctly.")

    # Footer
    st.markdown("---")
    st.markdown("""
    **How to use this as an API:**
    1. Deploy this app to Streamlit Cloud
    2. Use the app URL as your API base
    3. Add query parameters for different operations
    4. Your HTML frontend can make requests to these endpoints
    """)
