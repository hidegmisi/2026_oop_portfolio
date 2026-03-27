from __future__ import annotations

import os
import re
from dataclasses import dataclass

_THUMB_PREFIX_RE = re.compile(r"^Website%20DB/", re.IGNORECASE)


@dataclass(frozen=True)
class ThumbnailPathResolver:
    base_dir: str = "assets/project_thumbs"
    default_ext: str = ".png"

    def resolve(self, *, raw_thumbnail: str, slug: str) -> str | None:
        if not slug:
            return None

        ext = self.default_ext
        raw_value = (raw_thumbnail or "").strip()
        if raw_value:
            clean = _THUMB_PREFIX_RE.sub("", raw_value)
            filename = os.path.basename(clean)
            _, parsed_ext = os.path.splitext(filename)
            if parsed_ext:
                ext = parsed_ext

        return os.path.join(self.base_dir, f"{slug}{ext}").replace("\\", "/")
