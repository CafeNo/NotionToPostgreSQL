from datetime import datetime

# Convert Notion's due date string to a Python datetime object
def convert_due_date(due_date_str):
    return datetime.strptime(due_date_str, "%Y-%m-%d")
