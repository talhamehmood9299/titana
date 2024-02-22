# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# import importlib.util
# import openai


# app = FastAPI()

# class TextGenerationRequest(BaseModel):
#     prompt: str

# # Allow CORS for all origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/plan_of_care")
# async def plan_of_care(request: TextGenerationRequest):
#     filename = request.prompt
#     task_string = "Task 2:"
#     try:
#         # Dynamically import the module
#         module = importlib.import_module(filename)

#         # Dynamically get the task function from the module
#         task_function = getattr(module, "task")

#         # Call the task function passing the task_string
#         result = task_function(task_string)

#         return {"result": result}
#     except ModuleNotFoundError:
#         raise HTTPException(status_code=404, detail="Module not found")
#     except AttributeError:
#         raise HTTPException(status_code=500, detail="Task function not found in the module")
    