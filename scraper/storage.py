"""
Armazenamento incremental em JSONL (JSON Lines).
Cada linha é um post completo serializado como JSON, garantindo que dados
não sejam perdidos em caso de interrupção do script.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonlStorage:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._seen_ids: set[str] = set()
        self._load_seen_ids()

    def _load_seen_ids(self) -> None:
        """Lê o arquivo existente e popula o conjunto de IDs já coletados."""
        if not self.filepath.exists():
            return
        with self.filepath.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    post_id = record.get("post", {}).get("id")
                    if post_id:
                        self._seen_ids.add(post_id)
                except json.JSONDecodeError:
                    pass
        logger.info("Retomando coleta. %d posts já no disco.", len(self._seen_ids))

    def is_seen(self, post_id: str) -> bool:
        return post_id in self._seen_ids

    def save(self, record: dict) -> None:
        """Salva um único registro (post + comentários) no arquivo JSONL."""
        post_id = record.get("post", {}).get("id")
        with self.filepath.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        if post_id:
            self._seen_ids.add(post_id)
        logger.debug("Salvo post_id=%s", post_id)
