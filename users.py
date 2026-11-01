import os

import psycopg2
import psycopg2.extras


def get_all_users(dsn=None):
    """Return all rows from the users table as a list of dicts."""
    dsn = dsn or os.environ["DATABASE_URL"]
    with psycopg2.connect(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Static query, no external input. If filters are added later,
            # pass values via %s placeholders, never string formatting.
            cur.execute("SELECT * FROM users")
            return cur.fetchall()


if __name__ == "__main__":
    for user in get_all_users():
        print(user)
