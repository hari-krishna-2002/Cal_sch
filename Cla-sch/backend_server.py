# backend_server.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from task_extractor_core import extract_tasks
from calendar_helper import create_event, init_calendar_config
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

class EventInput(BaseModel):
    task_text: str
    due_date: str
    description: str = ""

@app.post("/init_calendar")
async def init_calendar(file: UploadFile = File(...), calendar_id: str = Form(...)):
    try:
        content = await file.read()
        json_data = content.decode('utf-8')
        init_calendar_config(json_data=json_data, calendar_id=calendar_id)
        return {"status": "Calendar Initialized"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/extract_tasks")
async def extract_tasks_api(data: TextInput):
    try:
        tasks = extract_tasks(data.text)
        return tasks
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/create_event")
async def create_event_api(data: EventInput):
    try:
        result = create_event(
            task_text=data.task_text,
            due_date=data.due_date,
            description=data.description
        )
        if result:
            return {"status": "success", "link": result.get("htmlLink", "")}
        else:
            return JSONResponse(status_code=500, content={"error": "Failed to create event"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
