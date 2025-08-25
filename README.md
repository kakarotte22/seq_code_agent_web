# 代码生成助手

基于Google ADK的代码生成、审查和优化流水线，使用Streamlit构建的Web应用。

## 功能

- 根据用户需求生成Python代码
- 自动审查生成的代码并提供改进建议
- 根据审查意见优化代码
- 下载优化后的代码

## 本地运行

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`streamlit run app.py`

## 环境变量

应用需要以下环境变量：

- `MOONSHOT_API_KEY`: Moonshot API密钥
- `MOONSHOT_API_BASE`: Moonshot API基础URL (默认: https://api.moonshot.cn/v1)

## 部署

此应用可以部署到Streamlit社区云，详见部署指南。