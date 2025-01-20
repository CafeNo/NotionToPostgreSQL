from dotenv import load_dotenv
from notion_api import fetch_notion_data
from postgres_db import fetch_db_tasks, insert_data_to_db, delete_task_from_db
from utils import convert_due_date
from datetime import datetime, timezone

load_dotenv()

# Fetch data from Notion
notion_data = fetch_notion_data()

# Fetch tasks from PostgreSQL
db_tasks = fetch_db_tasks()

# Initialize a list to store tasks to insert or update
tasks_to_insert = []
tasks_to_delete = []

# Create a set of notion_ids from Notion data for comparison
notion_ids_in_notion = set(task['id'] for task in notion_data)

# Iterate over each task from Notion
for result in notion_data:
    task_name = result['properties']['task_name']['title'][0]['text']['content']
    
    # Retrieve task status and convert it to a standardized format
    status_property = result['properties'].get('status', {}).get('status', {})
    status = status_property.get('name', 'Not Started')

    if status == 'In progress':
        status = 'In Progress'
    elif status == 'Not started':
        status = 'Not Started'
    elif status == 'Done':
        status = 'Done'

    # Retrieve and convert due date if present
    due_date = result['properties'].get('due_date', {}).get('date', {}).get('start', None)
    if due_date:
        due_date = convert_due_date(due_date)

    # Extract Notion ID and last updated time
    notion_id = result['id']
    updated_at_str = result['last_edited_time']
    updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))  # Convert to offset-aware datetime

    # Check if the task exists in the PostgreSQL database
    task_exists = False
    for db_task in db_tasks:
        if notion_id == db_task['notion_id']:
            task_exists = True

            # Convert the 'updated_at' field to an offset-aware datetime for comparison
            db_updated_at = db_task['updated_at'].replace(tzinfo=timezone.utc)

            # If the task in Notion is more recent, or the status has changed, mark it for insertion/updating
            if updated_at > db_updated_at or status != db_task['status']:
                tasks_to_insert.append((task_name, status, due_date, notion_id, updated_at))
            break

    # If task does not exist in the database, add it to tasks to be inserted
    if not task_exists:
        tasks_to_insert.append((task_name, status, due_date, notion_id, updated_at))

# Identify tasks that have been deleted in Notion by comparing notion_id
notion_ids_in_db = {db_task['notion_id'] for db_task in db_tasks}
deleted_notion_ids = notion_ids_in_db - notion_ids_in_notion

# Add deleted tasks to the delete list
for notion_id in deleted_notion_ids:
    tasks_to_delete.append(notion_id)

# Insert or update tasks in PostgreSQL
if tasks_to_insert:
    insert_data_to_db(tasks_to_insert)
    print(f"INSERTED or UPDATED {len(tasks_to_insert)} tasks into PostgreSQL.")

# Delete tasks from PostgreSQL
if tasks_to_delete:
    for notion_id in tasks_to_delete:
        delete_task_from_db(notion_id)
    print(f"DELETED {len(tasks_to_delete)} tasks from PostgreSQL.")

# Check if there are any tasks left in the PostgreSQL database
if not tasks_to_insert and not tasks_to_delete:
    print("NO new tasks to INSERT / UPDATE / DELETE.")
