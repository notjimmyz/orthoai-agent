"""Launcher module - initiates and coordinates the medical evaluation process."""

import multiprocessing
import json
from src.green_agent.agent import start_green_agent
from src.white_agent.agent import start_white_agent
from src.my_util import my_a2a


async def launch_evaluation():
    """Launch the complete evaluation workflow"""
    # Start green agent
    print("Launching medical green agent...")
    green_address = ("localhost", 9001)
    green_url = f"http://{green_address[0]}:{green_address[1]}"
    p_green = multiprocessing.Process(
        target=start_green_agent, args=("medical_green_agent", *green_address)
    )
    p_green.start()
    assert await my_a2a.wait_agent_ready(green_url), "Green agent not ready in time"
    print("Green agent is ready.")
    
    # Start white agent
    print("Launching medical white agent...")
    white_address = ("localhost", 9002)
    white_url = f"http://{white_address[0]}:{white_address[1]}"
    p_white = multiprocessing.Process(
        target=start_white_agent, args=("medical_white_agent", *white_address)
    )
    p_white.start()
    assert await my_a2a.wait_agent_ready(white_url), "White agent not ready in time"
    print("White agent is ready.")
    
    # Send the task description to green agent
    print("Sending evaluation task to green agent...")
    task_text = f"""
Your task is to evaluate the medical agent located at:
<white_agent_url>
{white_url}/
</white_agent_url>
You should test it with the following medical task:
<task_description>
Retrieve the blood pressure reading for patient MRN S1234567
</task_description>
<max_steps>
30
</max_steps>
    """
    print("Task description:")
    print(task_text)
    print("Sending...")
    response = await my_a2a.send_message(green_url, task_text)
    print("Response from green agent:")
    print(response)
    
    print("Evaluation complete. Terminating agents...")
    p_green.terminate()
    p_green.join()
    p_white.terminate()
    p_white.join()
    print("Agents terminated.")

