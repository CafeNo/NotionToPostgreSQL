import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Get table name from environment variables
TABLE_NAME = os.getenv('TABLE_NAME')

# Establish a connection to PostgreSQL
def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

# Fetch tasks from PostgreSQL database
def fetch_db_tasks():
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT notion_id, task_name, status, due_date, updated_at FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    
    db_tasks = []
    for row in rows:
        db_tasks.append({
            'notion_id': row[0],
            'task_name': row[1],
            'status': row[2],
            'due_date': row[3],
            'updated_at': row[4]
        })
    
    cursor.close()
    conn.close()
    return db_tasks

# Insert or update tasks into PostgreSQL
def insert_data_to_db(tasks):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    insert_query = f"""
    INSERT INTO {TABLE_NAME} (task_name, status, due_date, notion_id, updated_at)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (notion_id)
    DO UPDATE SET
        task_name = EXCLUDED.task_name,
        status = EXCLUDED.status,
        due_date = EXCLUDED.due_date,
        updated_at = EXCLUDED.updated_at;
    """
    
    for task in tasks:
        cursor.execute(insert_query, task)

    conn.commit()
    cursor.close()
    conn.close()

# Delete task from PostgreSQL based on notion_id
def delete_task_from_db(notion_id):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    delete_query = f"DELETE FROM {TABLE_NAME} WHERE notion_id = %s"
    
    cursor.execute(delete_query, (notion_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
