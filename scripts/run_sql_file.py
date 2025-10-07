"""Execute SQL file against DATABASE_URL using psycopg2.

Reads DATABASE_URL from .env (or environment) and runs the SQL statements in sql/create_tables.sql.
Be careful: this will modify the database.
"""
import os
import sys
from dotenv import load_dotenv


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    dotenv_path = os.path.join(root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        load_dotenv()

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('DATABASE_URL not set in .env. Aborting.')
        sys.exit(2)

    sql_path = os.path.join(root, 'sql', 'create_tables.sql')
    if not os.path.exists(sql_path):
        print('SQL file not found:', sql_path)
        sys.exit(3)

    try:
        import psycopg2
        from psycopg2 import sql
    except Exception as e:
        print('psycopg2 not installed. Install with: pip install psycopg2-binary')
        print('Exception:', e)
        sys.exit(4)

    def sanitize_database_url(url: str) -> str:
        # Try a robust regex-based sanitizer: split at the last '@' and encode username/password
        try:
            import re
            from urllib.parse import quote
            m = re.match(r"(?P<prefix>^[^:]+://)(?P<userinfo>.+)@(?P<host>.+)$", url)
            if not m:
                return url
            prefix = m.group('prefix')
            userinfo = m.group('userinfo')
            host = m.group('host')
            # userinfo may contain ':' separating user and pass
            if ':' in userinfo:
                user, pwd = userinfo.split(':', 1)
            else:
                user, pwd = userinfo, ''
            # remove surrounding brackets and whitespace
            user = user.strip().strip('[]')
            pwd = pwd.strip().strip('[]')
            # percent-encode
            user_q = quote(user, safe='')
            pwd_q = quote(pwd, safe='')
            new = f"{prefix}{user_q}:{pwd_q}@{host}"
            return new
        except Exception:
            return url

    try:
        conn = psycopg2.connect(database_url)
    except Exception as e:
        # Try to sanitize common percent-encoding errors
        msg = str(e)
        print('Initial connection error:', msg)
        try:
            safe_url = sanitize_database_url(database_url)
            if safe_url != database_url:
                print('Retrying with sanitized DATABASE_URL')
                try:
                    conn = psycopg2.connect(safe_url)
                except Exception:
                    # Try a direct simple fix: find userinfo between '://' and '@'
                    try:
                        from urllib.parse import quote
                        s = database_url
                        if '://' in s and '@' in s:
                            prefix, rest = s.split('://', 1)
                            # split at last '@' to allow @ inside password
                            userinfo, hostpart = rest.rsplit('@', 1)
                            # userinfo might be like user:pass; remove surrounding brackets in password
                            if ':' in userinfo:
                                user, pwd = userinfo.split(':', 1)
                                pwd = pwd.strip('[]')
                                user_q = quote(user, safe='')
                                pwd_q = quote(pwd, safe='')
                                new = prefix + '://' + user_q + ':' + pwd_q + '@' + hostpart
                                print('Retrying with directly-encoded DATABASE_URL')
                                conn = psycopg2.connect(new)
                            else:
                                raise
                        else:
                            raise
                    except Exception as e2:
                        print('Direct encoding retry failed:', e2)
                        raise
            else:
                raise
        except Exception as e2:
            print('Error connecting to DATABASE_URL after sanitizing:', e2)
            sys.exit(5)

    try:
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_text = f.read()
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_text)
        print('SQL executed successfully.')
    except Exception as e:
        print('Error executing SQL:', e)
        sys.exit(6)
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
