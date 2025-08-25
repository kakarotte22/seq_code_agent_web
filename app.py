import streamlit as st
from create_agent import initialize_agent,generate_ids
import asyncio
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
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
    api_key = st.text_input("Moonshot API密钥",type="password")
    api_base = st.text_input("Moonshot API基础URL", value="https://api.moonshot.cn/v1")
    
    st.markdown("---")
    st.markdown("由Google ADK和Streamlit提供支持")

# 主要功能
root_agent = initialize_agent(api_key,api_base)
# session_service = InMemorySessionService()

APP_NAME = "code_generator_app"
USER_ID,SESSION_ID = generate_ids()

# session_service = InMemorySessionService()

# runner = Runner(
#     agent=root_agent,
#     app_name=APP_NAME,
#     session_service=session_service
# )

async def run_and_get(query: str,user_id=USER_ID,session_id=SESSION_ID):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent,app_name=APP_NAME,session_service=session_service)
    await runner.session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    content = types.Content(role="user",parts=[types.Part(text=query)])
    final_text = None
    async for event in runner.run_async(user_id=user_id,session_id=session_id,new_message=content):
        if event.is_final_response():
            final_text = event.content.parts[0].text
    return final_text



# 用户输入区域
user_request = st.text_area("请输入您的代码需求", height=150, 
                           placeholder="例如：写一个python冒泡排序函数")

# 处理按钮
if st.button("生成代码", type="primary", disabled=not api_key):
    if not api_key:
        st.error("请提供Moonshot API密钥")
    elif not user_request:
        st.warning("请输入代码需求")
    else:
        try:
            with st.spinner("正在生成代码..."):
                # 运行代理
                # 使用asyncio运行异步函数
                result = asyncio.run(run_and_get(user_request,user_id=USER_ID,session_id=SESSION_ID))
                # 显示结果
                col1 = st.columns(1)[0]
                
                with col1:
                    st.subheader("生成优化后的代码")
                    st.code(result.strip("```python").strip("```").strip(), language="python")
                
                # 下载按钮
                st.download_button(
                    label="下载优化后的代码",
                    data=result.strip("```python").strip("```").strip(),
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