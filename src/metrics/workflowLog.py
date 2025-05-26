from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict
import json
import os

@dataclass
class ClipLogEntry:
    clipNumber: int
    filePath: str
    platform: str
    uploadStatus: str
    smartDetailsEnabled: bool
    smartDetailsUsed: bool
    errors: list = field(default_factory=list)

@dataclass
class WorkflowLog:
    configName: str
    workflowStart: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    workflowEnd: str = ""
    clips: Dict[int, ClipLogEntry] = field(default_factory=dict)
    errorsDuringWorkflow: list = field(default_factory=list)

    def add_clip(self, entry: ClipLogEntry):
        self.clips[entry.clipNumber] = entry

    def update_clip(self, clipNumber: int, **kwargs):
        clip = self.clips.get(clipNumber)
        if not clip:
            raise ValueError(f"Clip {clipNumber} not found in log")
        for key, value in kwargs.items():
            setattr(clip, key, value)

    def set_end_time(self):
        self.workflowEnd = datetime.utcnow().isoformat() + "Z"

    def save_to_file(self, output_dir: str = "./logs"):
        os.makedirs(output_dir, exist_ok=True)
        filename = f"log_{self.configName}_{self.workflowStart[:10]}.json"
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(asdict(self), f, indent=4)
