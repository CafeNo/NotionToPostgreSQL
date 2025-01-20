import requests
import os
import time
from postgres_db import insert_data_to_db, delete_task_from_db

# Fetch data from Notion API and handle pagination
def fetch_notion_data():
    NOTION_TOKEN = os.getenv('NOTION_TOKEN') 
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2021-05-13"
    }

    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    notion_data = []
    next_cursor = None
    
    while True:
        params = {}
        if next_cursor:
            params['start_cursor'] = next_cursor
        
        response = requests.post(url, headers=headers, json=params)
        data = response.json()

        # Handle pagination if there is a next_cursor
        notion_data.extend(data['results'])
        next_cursor = data.get('next_cursor', None)
        
        if not next_cursor:
            break
        
        time.sleep(1)
    
    # Filter out deleted tasks from the results
    notion_data = [task for task in notion_data if not task.get('archived', False)]
    
    return notion_data

# Sync tasks from Notion to PostgreSQL
def sync_notion_to_db(notion_tasks, db_tasks):
    for notion_task in notion_tasks:
        task_name = notion_task['properties']['task_name']['title'][0]['text']['content']
        status_property = notion_task['properties'].get('status', {}).get('status', {})
        status = status_property.get('name', 'Not Started')
        due_date = notion_task['properties'].get('due_date', {}).get('date', {}).get('start', None)
        notion_id = notion_task['id']
        updated_at = notion_task['last_edited_time']  # Moved from properties

        # Check if the task already exists in PostgreSQL
        task_exists = False
        for db_task in db_tasks:
            if notion_id == db_task['notion_id']:
                task_exists = True
                # If the task is more recent, update it in PostgreSQL
                if updated_at > db_task['updated_at']:
                    insert_data_to_db([(task_name, status, due_date, notion_id, updated_at)])
                break
        
        # If task doesn't exist, insert it into PostgreSQL
        if not task_exists:
            insert_data_to_db([(task_name, status, due_date, notion_id, updated_at)])

    # Delete tasks from PostgreSQL that are no longer in Notion
    notion_ids_in_notion = {task['id'] for task in notion_tasks}
    notion_ids_in_db = {db_task['notion_id'] for db_task in db_tasks}
    deleted_notion_ids = notion_ids_in_db - notion_ids_in_notion
    
    for notion_id in deleted_notion_ids:
        delete_task_from_db(notion_id)
