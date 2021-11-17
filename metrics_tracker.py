from enum import Enum
from typing import Any, Dict
import json

class DataType(Enum):
    DISTRIBUTION = "distribution"
    SEQUENTIAL = "sequential"
    MAP = "map"


class Metrics:

    def __init__(self) -> None:
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def new_data(self, name: str, type: DataType, **kwargs):
        entry = {
            "type": type.value,
            "data": [],
            **kwargs
        }
        self.metrics[name] = entry

    def add(self, name: str, data: Any):
        self.metrics[name]["data"].append(data)

    def save(self, path: str = "metrics.json"):
        with open(path, "w") as fd:
            json.dump(self.metrics, fd)

    def auto_bins(self, name: str):
        mini = min(self.metrics[name]["data"])
        maxi = max(self.metrics[name]["data"])
        self.metrics[name]["bins"] = list(range(mini, maxi + 2))
