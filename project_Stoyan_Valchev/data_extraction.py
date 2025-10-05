import psycopg2
import os
from dotenv import load_dotenv
import time
import subprocess
import sys

load_dotenv()

TEXT_FILE = "../projects_data.md"
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
}

TABLE_NAME = "projects"

# The following functions are AI generated!!!!!!!!

def clean_line(line):
    line = line.strip().strip('|')
    return [col.strip() for col in line.split('|')]

def import_projects():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Ensure unique constraint on project_name
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = '{TABLE_NAME}_project_name_key'
                ) THEN
                    ALTER TABLE {TABLE_NAME}
                    ADD CONSTRAINT {TABLE_NAME}_project_name_key UNIQUE (project_name);
                END IF;
            END$$;
        """)

        with open(TEXT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('|---'):
                continue
            if line.lower().startswith('| project') or line.lower().startswith('project'):
                continue

            columns = clean_line(line)
            if len(columns) != 4:
                print(f"Skipping malformed line: {line}")
                continue

            project_name, responsible_person, industry, overview = columns

            # Upsert (insert or update if exists)
            cursor.execute(f"""
                INSERT INTO {TABLE_NAME} (project_name, responsible_person, industry, overview)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (project_name)
                DO UPDATE SET
                    responsible_person = EXCLUDED.responsible_person,
                    industry = EXCLUDED.industry,
                    overview = EXCLUDED.overview;
            """, (project_name, responsible_person, industry, overview))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Import complete.")

    except Exception as e:
        print("Error:", e)


def run_periodically(interval=5):
    print(f"Starting periodic check every {interval} seconds...")
    last_modified = None

    while True:
        try:

            current_modified = os.path.getmtime(TEXT_FILE)

            if last_modified is None or current_modified != last_modified:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Detected change in '{TEXT_FILE}'. Importing data...")
                import_projects()

                # Run embeddings on the data
                result = subprocess.run([sys.executable, 'embeddings.py'], capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Error:", result.stderr)

                last_modified = current_modified
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cycle complete.\n")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No changes detected.")

        except FileNotFoundError:
            print(f"Warning: '{TEXT_FILE}' not found.")
        except Exception as e:
            print("Error during check:", e)

        time.sleep(interval)

if __name__ == "__main__":
    run_periodically(120)
