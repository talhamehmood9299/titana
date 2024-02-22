from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

class TextGenerationRequest(BaseModel):
    provider: str
    prompt: str

def process_task(request: TextGenerationRequest, task: str):
    provider_module = request.provider
    post_date = request.prompt
    logger.info(f"Processing task '{task}' with provider '{provider_module}'")

    try:

        # Dynamically import the module
        module = importlib.import_module(provider_module)

        # Dynamically get the task function from the module
        task_function = getattr(module, "task")

        # Call the task function passing the task string
        response = task_function(task, post_date)

        return {"response": response}
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail="Module not found")
    except AttributeError:
        raise HTTPException(status_code=500, detail="Task function not found in the module")

@app.post("/history_of_illness")
async def history_of_illness(request: TextGenerationRequest):
    return process_task(request, "Task 1:")
    
@app.post("/plan_of_care")
async def plan_of_care(request: TextGenerationRequest):
    return process_task(request, "Task 2:")

@app.post("/cpt_code")
async def cpt_code(request: TextGenerationRequest):
    return process_task(request, "Task 3:")

@app.post("/physical_exam")
async def physical_exam(request: TextGenerationRequest):
    return process_task(request, "Task 4:")

@app.post("/review_of_system")
async def review_of_system(request: TextGenerationRequest):
    return process_task(request, "Task 5:")