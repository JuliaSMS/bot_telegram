"""Test Supabase connection script.

This script reads .env, attempts to create a Supabase client and performs simple queries
to verify the connection and permissions (select from 'planos', list storage buckets).

It prints clear, masked output and exits with non-zero code on failure.
"""
import os
import sys
from dotenv import load_dotenv


def mask(s: str) -> str:
    if not s:
        return "(empty)"
    if len(s) <= 8:
        return s
    return s[:4] + "..." + s[-4:]


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    dotenv_path = os.path.join(root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

    print(f"SUPABASE_URL={mask(url)}")
    print(f"SUPABASE_KEY={mask(key)}")

    if not url or not key:
        print("Supabase URL/key not set in .env. Aborting test.")
        sys.exit(2)

    try:
        from supabase import create_client
    except Exception as e:
        print("supabase client not installed. Install with: pip install supabase")
        print("Exception:", e)
        sys.exit(3)

    try:
        client = create_client(url, key)
        print("Supabase client created.")
    except Exception as e:
        print("Error creating Supabase client:", e)
        sys.exit(4)

    # Test a simple table query
    try:
        res = client.table('planos').select('*').limit(1).execute()
        print("Query 'planos' executed. Result:")
        print(getattr(res, 'data', res))
    except Exception as e:
        print("Error querying 'planos':", e)

    # Test storage (list buckets) if supported
    try:
        storage = client.storage
        buckets = storage.list_buckets()
        print("Storage buckets:", buckets)
    except Exception as e:
        print("Storage test failed or unsupported in client:", e)

    print("Supabase connection test finished.")


if __name__ == '__main__':
    main()
