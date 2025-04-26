from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from config import api_key
from typing import Union, List


# Configure your Gemini API key
model = GeminiModel(
'gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key)
)

class SubTasks(BaseModel):
    sub_tasks: List[str] = Field("The Tasks That Is Needed To Be Done")

class Code(BaseModel):
    code: str = Field("The Code To Be executed")

class Thoughts(BaseModel):
    thoughts:List[str] = Field("The Thoughts On The Task Progress")
    results:str = Field("The Final Output")
first_planner_agent = Agent(
    model=model,
    result_type=SubTasks,
    system_prompt=(
    """You are an AI assistant that, given a high-level task, will break it down into smaller subtasks. Each subtask should be simple enough to be executed sequentially by the automation tool Playwright without using loops. Each step should be actionable and straightforward like enter input, click the button, etc. ensuring the automation progresses sequentially as it communicates continuously with an external processor for updates."""
    ),)

thoughts_examples = """
Thoughts:
- The current screenshot shows the issues page of the GitHub repository 'lavague-ai/LaVague'.
- The objective is to go to the first issue.
- Previous instructions have been unsuccessful. A new approach should be used.
- The '#225' seems not to be clickable and it might be relevant to devise an instruction that does not include it.

Thoughts:
- The current page shows the model page for 'meta-llama/Meta-Llama-3-8B' on Hugging Face.
- Hugging Face, is a hub for AI models and datasets, where users can explore and interact with a variety of AI models.
- I am therefore on the right page to find information about the release date of 'Meta-Llama-3-8B'.
- However, only information visible right now is about legal and licensing information.
- Therefore the best next step is to use the 'SCAN' command to take screenshots of the whole page to find the release date before taking further action.

Thoughts:
- The whole page has been scanned and current screenshot show the documentation page for the getting started of Gemini API.
- I am therefore on the right page to find the code to get started with the Gemini API.
- The next step is to provide the code to get started with the Gemini API.
- Therefore I need to use the Python Engine to generate the code to extract the code to get started with the Gemini API from this page.
"""

thought_agent = Agent(
    model=model,
    result_type=Thoughts,
    system_prompt=(
    """You are given the page content and the tasks that has to be performed and the list of playwright commands already executed. Think carefully, Analyze the tasks and Give a list of thoughts. Each thought should be concise and clear.
    Output the results of the task If task is complete.
    examples
    {thoughts_examples}"""
    ),)

next_planner_agent = Agent(
    model=model,
    result_type=SubTasks,
    system_prompt=(
        'You are an assistant tasked with determining whether all sub-tasks required for a given high-level task have been completed based on the Playwright automation tool. Using the provided list of sub-tasks, the list of executed commands, and the current page source, decide if further actions are required or if the task is complete.'
        'Based on this information, provide a revised list of subtasks, ensuring each can be executed by Playwright sequentially without loops. Adjust the tasks as needed based on the changes observed in the page content.'
    ),)

code_agent = Agent(
    model=model,
    result_type=Code,
    system_prompt=(
    """You are an assistant tasked with generating executable code snippets for Playwright and Python. Output Playwright commands to perform web operations or Python commands to store web content in a list named `local_storage_list`. 
    Avoid using the `await` keyword."""
    ),)
