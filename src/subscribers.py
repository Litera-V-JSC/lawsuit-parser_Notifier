import json
from typing import Any, Dict

from src.config import Config


def load_subscribers() -> Dict[str, Any]:
    path = Config.SUBSCRIBERS_FILE
    if not path.exists():
        path = Config.SUBSCRIBERS_DEFAULT

    if not path.exists():
        raise FileNotFoundError(
            f"No subscribers file found at {Config.SUBSCRIBERS_FILE} "
            f"or {Config.SUBSCRIBERS_DEFAULT}"
        )

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return {
        'smtp': data.get('smtp', {}),
        'subscribers': data.get('subscribers', []),
        'source': str(path),
    }
