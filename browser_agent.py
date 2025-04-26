from playwright.sync_api import sync_playwright
from sub_agents import next_planner_agent,first_planner_agent,code_agent,thought_agent
import nest_asyncio
nest_asyncio.apply()


playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()


task = "Search for tensorflow in the site."
website = "https://pypi.org/project/google/"

task_list = []
commands = []

next_command = f"page.goto('{website}')"
exec(next_command)
commands.append(next_command)
page_content = page.content()


def update_task(task,task_list,commands,page_content):
    prompt = f"""
    Original Task:
        {task}
        Sub-Tasks List:
        {task_list}
        Executed Commands:
        {commands}
        Current Page Content:
        {page_content}
        """
    thoughts = thought_agent.run_sync(prompt)
    thoughts_result = thoughts.data
    print("Thoughts:\n" + "\n".join(thoughts_result.thoughts) + "\n")
    print("Results: \n" + thoughts_result.results)
    result = next_planner_agent.run_sync(prompt + "\n Thoughts:" + "\n".join(thoughts_result.thoughts))

    return result.data 

def create_first_tasks(task):
    prompt = f"""
    Write the task list for this task: {task}"""
    result = next_planner_agent.run_sync(prompt)
    return result.data 

def create_playwright_cmd(tasks, commands, page_content):
    playwright_command_prompt = f"""
    Task List:
    {tasks}
    Executed Command Till Now:
    {commands}
    Current Page Content:
    {page_content}
    Based on this context, output the necessary code to complete the next step in the task list. Ensure the code is suitable for sequential execution and directly interacts with `local_storage_list` for storing data as needed.
    Just output the code, nothing else. Also output will be just one-line code that needs to be executed next.
    If the previous code is an error. Try to write a different code.
    for eg: 
    Instead of page.fill("input[name='q']", "Indian PM"). Use page.locator('textarea[name="q"]').fill("Indian PM")
    """
    result = code_agent.run_sync(playwright_command_prompt)

    return result.data

plan = create_first_tasks(task)
task_list = plan.sub_tasks
print("Tasks" + "\n".join(task_list) + "\n")
while len(task_list):
    next_command = create_playwright_cmd(task_list, commands, page_content)
    try:
        print("Code\n" + next_command.code + "\n")
        exec(next_command.code)
        page_content = page.content()
        commands.append(next_command.code)
    except Exception as e:
        print(f"There is an error in the previous commmand. {e} Will Try Again. ")
        page_content = e
    plan = update_task(task,task_list,commands,page_content)
    task_list = plan.sub_tasks
    print("Next tasks \n" + "\n".join(task_list) + "\n")


