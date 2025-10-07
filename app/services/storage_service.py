import os
from typing import Optional
import io

try:
    from supabase import create_client
except Exception:
    create_client = None


class StorageService:
    def __init__(self, db_service):
        # db_service is expected to be DBService instance
        self.db = db_service

    def _ensure_client(self):
        # ensure db.client exists, otherwise try to create one from env
        client = getattr(self.db, 'client', None)
        if client:
            return client
        # attempt to create client if supabase.create_client available
        try:
            from supabase import create_client as _create
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            if url and key:
                client = _create(url, key)
                self.db.client = client
                return client
        except Exception:
            pass
        return None

    def upload_bytes(self, bucket: str, path: str, data: bytes) -> Optional[str]:
        """Upload bytes to Supabase Storage and return public URL if possible; otherwise save locally and return file path."""
        # If Supabase client is available, try to upload
        client = self._ensure_client()
        if client:
            try:
                storage = client.storage
                # Try uploading bytes directly using a file-like object
                try:
                    file_obj = io.BytesIO(data)
                    # supabase-py upload may accept file-like objects
                    res = storage.from_(bucket).upload(path, file_obj)
                except Exception:
                    # Fallback: write to temp file then upload
                    os.makedirs('.temp_storage', exist_ok=True)
                    tmp_path = os.path.join('.temp_storage', os.path.basename(path))
                    with open(tmp_path, 'wb') as f:
                        f.write(data)
                    res = storage.from_(bucket).upload(path, tmp_path)

                # Attempt to create public URL
                try:
                    url = storage.from_(bucket).get_public_url(path)
                    return url
                except Exception:
                    # Some supabase clients return object with 'public_url' or direct link
                    try:
                        if isinstance(res, dict):
                            return res.get('publicURL') or res.get('public_url') or res.get('public')
                    except Exception:
                        return None
            except Exception as e:
                print(f"[StorageService] upload error: {e}")
                # fallback to local file
                pass

        # fallback: save locally under .temp_storage
        os.makedirs('.temp_storage', exist_ok=True)
        local_path = os.path.join('.temp_storage', path.replace('/', '_'))
        with open(local_path, 'wb') as f:
            f.write(data)
        return local_path
