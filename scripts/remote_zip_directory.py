"""Bounded HTTP Range reader for ZIP metadata. Never extracts archive members."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import zipfile
from urllib.request import Request, urlopen

from modality_inventory import aggregate


class DirectoryRanges:
    def __init__(self, url: str, max_bytes: int = 2 * 1024 * 1024):
        if not url.startswith("https://"): raise ValueError("HTTPS required")
        self.url, self.max_bytes, self.received, self.position = url, max_bytes, 0, 0
        self.spans: list[dict] = []
        self.cache: list[tuple[int, bytes]] = []
        self.context = ssl.create_default_context()
        try:
            import certifi
            self.context.load_verify_locations(certifi.where())
        except ImportError:
            pass
        start, end, total, data = self._range("bytes=-22")
        self.size = total
        self.cache.append((start, data))

    def _range(self, value: str):
        request = Request(self.url, headers={"Range": value, "Accept-Encoding": "identity",
                                             "User-Agent": "drone-data-collector/0.1 metadata-only"})
        with urlopen(request, timeout=25, context=self.context) as response:
            if response.status != 206:
                raise ValueError(f"Range request returned HTTP {response.status}; refused full body")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
            if not match: raise ValueError("missing/invalid Content-Range")
            start, end, total = map(int, match.groups())
            length = end - start + 1
            if length < 1 or start < 0 or end >= total or self.received + length > self.max_bytes:
                raise ValueError("ZIP metadata transfer limit exceeded")
            data = response.read(length + 1)
            if len(data) != length: raise ValueError("Range response length mismatch")
        self.received += len(data)
        self.spans.append({"start": start, "end": end, "bytes": len(data)})
        return start, end, total, data

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if self.position < 0: raise ValueError("negative offset")
        return self.position

    def tell(self): return self.position

    def seekable(self): return True

    def read(self, size=-1):
        if size < 0: size = self.size - self.position
        size = min(size, self.size - self.position)
        if size <= 0: return b""
        begin = self.position
        for start, data in self.cache:
            if start <= begin and begin + size <= start + len(data):
                self.position += size
                return data[begin - start:begin - start + size]
        if size > self.max_bytes - self.received:
            raise ValueError("refused payload-sized read")
        start, end, total, data = self._range(f"bytes={begin}-{begin + size - 1}")
        if (start, end, total) != (begin, begin + size - 1, self.size):
            raise ValueError("unexpected Range offsets or changed archive size")
        self.cache.append((start, data))
        self.position += size
        return data


def inspect_directory(url: str, dataset: str = "") -> dict:
    source = DirectoryRanges(url)
    try:
        with zipfile.ZipFile(source) as archive:
            files = [{"path": f.filename, "size": f.file_size} for f in archive.infolist() if not f.is_dir()]
    except zipfile.BadZipFile as exc:
        raise ValueError(f"not a readable ZIP directory: {exc}") from exc
    return {"url": url, "archive_bytes": source.size, "metadata_bytes_received": source.received,
            "ranges": source.spans, "inventory": aggregate(files, dataset),
            "inventory_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
            "limitations": ["ZIP directory only; payload integrity and semantics were not validated."]}
