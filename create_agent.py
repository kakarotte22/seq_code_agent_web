import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types 
import uuid
from datetime import datetime
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

def generate_ids():
    """
    生成UID和server_id
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_uuid = str(uuid.uuid4())
    return f"{random_uuid}",f"{timestamp}-{random_uuid}"

def initialize_agent(api_key,api_base):
    """
    初始化代码生成流水线代理
    """
    # 设置API密钥
    # os.environ["MOONSHOT_API_KEY"] = api_key
    # os.environ["MOONSHOT_API_BASE"] = api_base
    
    # 初始化模型
    model = LiteLlm(
        model="openai/kimi-k2-0711-preview",
        api_key=api_key,
        api_base=api_base,
    )
    
    # 代码生成器代理
    code_writer_agent_prompt = """
    You are a Python Code Generator.
    Based *only* on the user's request, write Python code that fulfills the requirement.
    Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.
    """
    code_writer_agent = Agent(
        name="CodeWriterAgent",
        model=model,
        instruction=code_writer_agent_prompt,
        description="Writes initial Python code based on a specification.",
        output_key="generated_code"
    )
    
    # 代码审查代理
    code_reviewer_agent_prompt = """
    You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

    **Review Criteria:**
    1.  **Correctness:** Does the code work as intended? Are there logic errors?
    2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
    3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
    4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
    5.  **Best Practices:** Does the code follow common Python best practices?

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
    If the code is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues" statement.
    finally,Output should be transformed to Chinese."""
    code_reviewer_agent = Agent(
        name="CodeReviewerAgent",
        model=model,
        instruction=code_reviewer_agent_prompt,
        description="Reviews code and provides feedback.",
        output_key="review_comments",
    )
    
    # 代码优化代理
    code_refactorer_agent_promt = """
    You are a Python Code Refactoring AI.
    Your goal is to improve the given Python code based on the provided review comments.

    **Original Code:**
    ```python
    {generated_code}
    ```

    **Review Comments:**
    {review_comments}

    **Task:**
    Carefully apply the suggestions from the review comments to refactor the original code.
    If the review comments state "No major issues found," return the original code unchanged.
    Ensure the final code is complete, functional, and includes necessary imports and docstrings.

    **Output:**
    Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.
    """
    code_refactorer_agent = Agent(
        name="CodeRefactorerAgent",
        model=model,
        instruction=code_refactorer_agent_promt,
        description="Refactors code based on review comments.",
        output_key="refactored_code",
    )
    
    # 创建流水线代理
    code_pipeline_agent = SequentialAgent(
        name="CodePipelineAgent",
        sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
        description="Executes a sequence of code writing, reviewing, and refactoring.",
    )
    
    return code_pipeline_agent

