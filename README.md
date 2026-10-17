# AutoClipper
Tool to automate clipping 

(Note: Sort of abandoned this project, so making public. Was a fun run) 

### Questions
- Keep in Python or move to JVM (Kotlin or Java)? We're setting it up in OOP.... Java may be better
- Going to have different approaches for clip detection 
- Template matching (is logo present, if so dont clip, if not clip)
- Train model to detect commercial 

### Broad TODO: 
- Need to make a list of all the dependencies used for this project. There are a lot (install script?)
- Need to provide framework/guide for custom selenium scripts? 
- Overhaul of configuration setup and listing 
- Probably need unit tests lol
- Create a UI version
- Have a thread in the run workflow that is a server and can accept commands

### Immediate TODO: 
- We need to handle OBS errors gracefully. Most notbably OBS errors when stopping/starting recording:
Traceback (most recent call last):
  line 53, in send
    raise OBSSDKRequestError(
    ...<3 lines>...
    )
obsws_python.error.OBSSDKRequestError: Request StopRecord returned code 501.

I think we could wrap the OBS client requests with try catch and retry 'n' times before crashing

- Implement a workflow fatal error and crash handling. When one component of workflow breaks, we finish uploading, if needed, and close all threads/processes
- Implement post recording commands. Or post detection/undetection commands
- Is there a way to upload the video and have it marked if it's for kids or not? 
- Refactor logging and generate a log file after every workflow. Dir holding log that displays overview of workflow and all logs generated during?
- Create a tiktok uploader and have tiktok as an external platform
- Once we get multiple platforms supported, multi-platform uploading per clip? 
- We need to fix bug where files aren't being deleted properly in runWorkflow

- Generating a title and description should be quite feasible: 
1. Post recording, transcribe audio (OpenAI Whisper, Google Speech-to-Text)
2. Feed transcript to LLG like GPT and have prompt for title and description
  - We can also ask for tags and to make all of the generated text SEO optimized 
3. Apply generates lines to video and upload


### Potential architecture
Client (Web UI or CLI)
    ↓
Backend (FastAPI / Node / Django)
    ↓
Workers (Docker)
   - YOLO detection
   - Whisper transcription
   - FFmpeg clipping/resizing
    ↓
Storage (S3, GCS, or local + CDN)
    ↓
Uploader Modules (YT, IG, TikTok APIs)
    ↓
Logs / Post Workflow Summary
