# Notion Task Sync to PostgreSQL

This project syncs tasks from a Notion database to a PostgreSQL database. It fetches tasks from Notion, compares them with the existing database records, and inserts, updates, or deletes records as necessary.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Functions Overview](#functions-overview)
- [License](#license)

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/your-username/notion-task-sync.git
   cd notion-task-sync
   ```

2. Create a virtual environment and activate it:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory and provide the following credentials:

```
# Notion API
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id

# PostgreSQL Database
POSTGRES_HOST=your_postgres_host
POSTGRES_DATABASE=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
TABLE_NAME=your_table_name
```

## Usage

Run the script to sync tasks from Notion to PostgreSQL:

```sh
python main.py
```

## Project Structure
```
notion-task-sync/
│── main.py           # Main script for syncing tasks
│── notion_api.py     # Handles Notion API interactions
│── postgres_db.py    # Manages PostgreSQL database operations
│── utils.py          # Utility functions
│── .env.example      # Example environment configuration
│── requirements.txt  # Required Python dependencies
│── README.md         # Project documentation
```

## Functions Overview

### `main.py`
- Fetches tasks from Notion API.
- Fetches tasks from PostgreSQL.
- Compares data and determines which tasks need insertion, updates, or deletion.
- Updates the PostgreSQL database accordingly.

### `notion_api.py`
- `fetch_notion_data()`: Fetches tasks from the Notion database using the Notion API.
- `sync_notion_to_db(notion_tasks, db_tasks)`: Synchronizes Notion tasks with PostgreSQL.

### `postgres_db.py`
- `get_postgres_connection()`: Establishes a connection to PostgreSQL.
- `fetch_db_tasks()`: Retrieves tasks from PostgreSQL.
- `insert_data_to_db(tasks)`: Inserts or updates tasks in PostgreSQL.
- `delete_task_from_db(notion_id)`: Deletes a task from PostgreSQL based on Notion ID.

### `utils.py`
- `convert_due_date(due_date_str)`: Converts Notion's due date format to a Python datetime object.

## License
This project is licensed under the MIT License.

