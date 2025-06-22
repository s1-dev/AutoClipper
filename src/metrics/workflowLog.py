from dataclasses import dataclass
from utils.fileUtils import FileUtils
from utils.constants import Metrics
from enum import Enum
from postClipHandling.clipSavingConfig import ExternalPlatform

class UploadStatus(Enum):
    FAILED = "failed"
    UPLOADED = "uploaded"

class LocalClipState(Enum):
    SAVED = "saved"
    DELETED = "deleted"

@dataclass
class ClipData:
    clipNumber: int
    localClipState: LocalClipState 
    savedPath: str
    platform: ExternalPlatform
    uploadStatus: UploadStatus 

    def toDict(self):
        return {
            "clipNumber": self.clipNumber,
            "localClipState": self.localClipState.value if self.localClipState else None,
            "savedPath": self.savedPath if self.savedPath else "",
            "platform": self.platform.value if self.platform else None,
            "uploadStatus": self.uploadStatus.value if self.uploadStatus else None
        }

class WorkflowLog:
    def __init__(self, outputFolder: str):
        self.clips = {}
        self.outputFolder = outputFolder

    def addEntry(self, clipData: ClipData):
        if clipData.clipNumber in self.clips:
            raise Exception("There is already a clip data entry with this clip number.")
        self.clips[clipData.clipNumber] = clipData

    def getEntry(self, clipNumber: int) -> ClipData:
        return self.clips[clipNumber]
    
    def updateEntry(self, clipNumber: int, newData: ClipData):
        self.clips[clipNumber] = newData

    def outputToFile(self):
        outputPath = FileUtils.joinFileToPath(self.outputFolder, Metrics.CLIP_DATA_FILE_NAME)

        serialized = {
            clip_number: clip_data.toDict()
            for clip_number, clip_data in self.clips.items()
        }

        FileUtils.createDir(self.outputFolder, exist_ok=True)
        FileUtils.dictToJson(dictData=serialized, outputPath=outputPath, indent=2)

        print(f"Workflow log written to {outputPath}")

# @dataclass
# class WorkflowLog:
#     configName: str
#     workflowStart: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
#     workflowEnd: str = ""
#     clips: Dict[int, ClipData] = field(default_factory=dict)
#     errorsDuringWorkflow: list = field(default_factory=list)

#     def add_clip(self, entry: ClipData):
#         self.clips[entry.clipNumber] = entry

#     def update_clip(self, clipNumber: int, **kwargs):
#         clip = self.clips.get(clipNumber)
#         if not clip:
#             raise ValueError(f"Clip {clipNumber} not found in log")
#         for key, value in kwargs.items():
#             setattr(clip, key, value)

#     def set_end_time(self):
#         self.workflowEnd = datetime.utcnow().isoformat() + "Z"

#     def save_to_file(self, output_dir: str = "./logs"):
#         os.makedirs(output_dir, exist_ok=True)
#         filename = f"log_{self.configName}_{self.workflowStart[:10]}.json"
#         with open(os.path.join(output_dir, filename), "w") as f:
#             json.dump(asdict(self), f, indent=4)
