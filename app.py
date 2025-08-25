import streamlit as st
import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

# 页面配置
st.set_page_config(
    page_title="代码生成助手",
    page_icon="💻",
    layout="wide"
)

# 应用标题
st.title("代码生成助手")
st.markdown("基于Google ADK的代码生成、审查和优化流水线")

# 侧边栏
with st.sidebar:
    st.header("关于")
    st.info("这是一个使用Google ADK开发的代码生成助手，可以根据您的需求生成、审查和优化Python代码。")
    
    # API密钥输入
    api_key = st.text_input("Moonshot API密钥", type="password")
    api_base = st.text_input("Moonshot API基础URL", value="https://api.moonshot.cn/v1")
    
    st.markdown("---")
    st.markdown("由Google ADK和Streamlit提供支持")

# 主要功能
def initialize_agent():
    """
    初始化代码生成流水线代理
    """
    # 设置API密钥
    os.environ["MOONSHOT_API_KEY"] = api_key
    os.environ["MOONSHOT_API_BASE"] = api_base
    
    # 初始化模型
    model = LiteLlm(
        model="openai/kimi-k2-0711-preview",
        api_key=api_key,
        api_base=api_base,
    )
    
    # 代码生成器代理
    code_writer_agent = Agent(
        name="CodeWriterAgent",
        model=model,
        instruction="""You are a Python Code Generator.
Based *only* on the user's request, write Python code that fulfills the requirement.
Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
        description="Writes initial Python code based on a specification.",
        output_key="generated_code"
    )
    
    # 代码审查代理
    code_reviewer_agent = Agent(
        name="CodeReviewerAgent",
        model=model,
        instruction="""You are an expert Python Code Reviewer. 
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
finally,Output should be transformed to Chinese.
""",
        description="Reviews code and provides feedback.",
        output_key="review_comments",
    )
    
    # 代码优化代理
    code_refactorer_agent = Agent(
        name="CodeRefactorerAgent",
        model=model,
        instruction="""You are a Python Code Refactoring AI.
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
""",
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

# 用户输入区域
user_request = st.text_area("请输入您的代码需求", height=150, 
                           placeholder="例如：创建一个简单的Flask API，包含用户注册和登录功能")

# 处理按钮
if st.button("生成代码", type="primary", disabled=not api_key):
    if not api_key:
        st.error("请提供Moonshot API密钥")
    elif not user_request:
        st.warning("请输入代码需求")
    else:
        try:
            with st.spinner("正在生成代码..."):
                # 初始化代理
                agent = initialize_agent()
                
                # 运行代理
                result = agent.run(user_request)
                
                # 显示结果
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("初始代码")
                    st.code(result["generated_code"].strip("```python").strip("```").strip(), language="python")
                
                with col2:
                    st.subheader("代码审查")
                    st.markdown(result["review_comments"])
                
                with col3:
                    st.subheader("优化后的代码")
                    st.code(result["refactored_code"].strip("```python").strip("```").strip(), language="python")
                
                # 下载按钮
                st.download_button(
                    label="下载优化后的代码",
                    data=result["refactored_code"].strip("```python").strip("```").strip(),
                    file_name="generated_code.py",
                    mime="text/plain",
                )
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
else:
    if not api_key:
        st.info("请在侧边栏输入您的Moonshot API密钥以继续")

# 使用说明
with st.expander("使用说明"):
    st.markdown("""
    ### 如何使用
    1. 在侧边栏输入您的Moonshot API密钥
    2. 在文本框中描述您需要的Python代码功能
    3. 点击"生成代码"按钮
    4. 查看生成的代码、审查意见和优化后的代码
    5. 使用下载按钮保存优化后的代码
    
    ### 提示
    - 尽量详细描述您的需求，包括功能、输入输出等
    - 如果生成的代码不符合预期，尝试重新描述您的需求
    """)