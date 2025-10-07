import os
import base64
from typing import Optional, Tuple

try:
    import google.generativeai as genai
except Exception:
    genai = None

import requests


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Optional flag to force mocks even if SDK present
        self.enable_mock = os.getenv("ENABLE_GEMINI_MOCK", "true").lower() in ("1", "true", "yes")
        if genai and self.api_key:
            try:
                # Some SDK versions use configure
                if hasattr(genai, 'configure'):
                    genai.configure(api_key=self.api_key)
            except Exception:
                pass

    def _extract_text(self, resp) -> str:
        # Try several common shapes of response
        try:
            if hasattr(resp, 'text'):
                return resp.text
            if isinstance(resp, dict):
                # common patterns
                for key in ('text', 'output', 'content', 'result'):
                    if key in resp and isinstance(resp[key], str):
                        return resp[key]
                # nested output
                out = resp.get('output') or resp.get('results')
                if isinstance(out, list) and out:
                    first = out[0]
                    if isinstance(first, dict):
                        return first.get('content') or first.get('text') or str(first)
            return str(resp)
        except Exception as e:
            return f"[ERROR extracting text] {e}"

    def generate_text(self, prompt: str) -> str:
        if not genai or not self.api_key:
            if self.enable_mock:
                return f"[MOCK TEXT] {prompt}"
            return "[Gemini not configured]"

        # Try multiple SDK call styles for robustness
        try:
            # genai.text.generate
            if hasattr(genai, 'text') and hasattr(genai.text, 'generate'):
                resp = genai.text.generate(model="models/text-bison-001", prompt=prompt)
                return self._extract_text(resp)

            # genai.generate_text
            if hasattr(genai, 'generate_text'):
                resp = genai.generate_text(model="text-bison-001", prompt=prompt)
                return self._extract_text(resp)

            # genai.generate
            if hasattr(genai, 'generate'):
                resp = genai.generate(model="text-bison-001", prompt=prompt)
                return self._extract_text(resp)

            return "[Gemini SDK present but no known text method]"
        except Exception as e:
            return f"[ERROR in Gemini] {e}"

    def _extract_image_bytes(self, resp) -> Optional[bytes]:
        # resp may contain bytes, base64 string, or URL
        try:
            # direct bytes
            if hasattr(resp, 'bytes'):
                return resp.bytes

            if isinstance(resp, (bytes, bytearray)):
                return bytes(resp)

            # dict-like
            if isinstance(resp, dict):
                # check common keys
                for k in ('b64_json', 'base64', 'image', 'data'):
                    v = resp.get(k)
                    if isinstance(v, str):
                        # base64
                        try:
                            return base64.b64decode(v)
                        except Exception:
                            pass
                # check nested outputs for urls
                for key in ('url', 'image_url', 'result'):
                    url = resp.get(key)
                    if isinstance(url, str) and url.startswith('http'):
                        r = requests.get(url)
                        if r.status_code == 200:
                            return r.content

            # object with url attribute
            url = getattr(resp, 'url', None) or getattr(resp, 'image_url', None)
            if isinstance(url, str) and url.startswith('http'):
                r = requests.get(url)
                if r.status_code == 200:
                    return r.content
        except Exception:
            pass
        return None

    def generate_image(self, prompt: str) -> bytes:
        # If Gemini SDK present and configured, try to generate image
        if genai and self.api_key and not self.enable_mock:
            try:
                # try common method names
                candidates = []
                if hasattr(genai, 'images') and hasattr(genai.images, 'generate'):
                    candidates.append(lambda: genai.images.generate(prompt=prompt))
                if hasattr(genai, 'image') and hasattr(genai.image, 'generate'):
                    candidates.append(lambda: genai.image.generate(prompt=prompt))
                if hasattr(genai, 'generate_image'):
                    candidates.append(lambda: genai.generate_image(prompt=prompt))

                for call in candidates:
                    try:
                        resp = call()
                        img = self._extract_image_bytes(resp)
                        if img:
                            return img
                    except Exception:
                        continue
            except Exception:
                pass

        # If we reach here, either SDK not present/usable or mocking enabled
        if self.enable_mock:
            # return a 1x1 PNG
            return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9c\x63\x60\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82"

        return b""

    def generate_video(self, prompt: str) -> bytes:
        # Placeholder stub for future integration
        return b""
