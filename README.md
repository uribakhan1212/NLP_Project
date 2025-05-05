# NLP_Project

# 📈 Trend-Based Story Generator Microservice

This project is a containerized microservice that fetches trending topics (from Google) and generates themed story scripts (e.g., comedy, tragedy, sarcasm) using a large language model i.e., Mistral 7B running locally.

It exposes a **gRPC API** for backend interaction and a **Streamlit-based frontend** for demo and user input.

---

## 🚀 Features

- 🔌 **gRPC API** with `/GenerateStory` endpoint
- 🧠 Story generation using a local LLM (Mistral 7B)
- 📥 Fetches real-time trending data by region
- ⚙️ Handles concurrent requests using `asyncio.Queue`
- 🧪 Fully testable via Postman or Python testcases
- 🌐 Frontend built using **Streamlit**
- 🐳 Docker-ready, with deployment scripts
- 💥 Detached frontend/backend architecture

---

## 🧩 Architecture Overview

```text
[Streamlit UI] ───> [gRPC Client] ───> [gRPC Server]
                                      |-> Async Queue
                                      |-> LLM-based Story Generator
                                      |-> Trend Data Fetcher
