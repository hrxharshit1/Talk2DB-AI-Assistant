# Project Submission: Talk2DB (AI Data Assistant)

## 1. Project Overview

**Problem Statement:**
In many organizations, accessing data from databases requires knowledge of SQL (Structured Query Language). Non-technical stakeholders (managers, marketing teams, etc.) often depend on technical staff to write queries for simple data retrieval, creating bottlenecks and delaying decision-making.

**Objective:**
To build an intelligent "Text-to-SQL" web assistant that empowers users to query a MySQL database using natural language (plain English), automatically generating and executing the correct SQL code.

**Scope:**
The application connects to a live MySQL database, fetches the schema, uses a Large Language Model (LLM) to translate user questions into SQL, executes the query safely, and provides a summarized, human-readable answer back to the user.

---

## 2. Your Role & Responsibilities

**Role:** Python Developer & AI Integrator

**Responsibilities:**
*   **Backend Development:** Designed and implemented the Flask application architecture to handle HTTP requests and manage application state.
*   **AI Integration:** Integrated the Google Gemini API (`google-genai`) to handle natural language processing and SQL generation.
*   **Database Connectivity:** specific logic to securely connect to arbitrary MySQL databases and dynamically retrieve schema information for the AI context.
*   **Frontend Implementation:** created a responsive web interface for users to input credentials and chat with the database.
*   **Debugging & Optimization:** resolved critical environment configuration issues and optimized API calls for reliability.

---

## 3. Technical Stack Used

*   **Languages:** Python (v3.12), SQL, HTML5, CSS3, JavaScript.
*   **Framework:** Flask (Python Web Framework).
*   **AI/ML:** Google Gemini API (Model: `gemini-2.0-flash`).
*   **Database:** MySQL (connected via `mysql-connector-python`).
*   **Tools:** VS Code, Virtual Environments (`venv`), Pip.

---

## 4. Challenges Faced & Solutions

**Challenge 1: Model Deprecation/Availability (404 Error)**
*   **Problem:** During development, the hardcoded AI model (`gemini-1.5-flash`) became unavailable, causing `404 Not Found` errors in the application.
*   **Solution:** I implemented a debugging script to programmatically list all available models associated with the API key. I identified the newer `gemini-2.0-flash` model and refactored the code to use a Configuration File (`config.json`), allowing model swaps without changing source code.

**Challenge 2: Environment Configuration Conflicts**
*   **Problem:** The application would run via a batch script but fail in the VS Code IDE due to path conflicts between the global Python installation and the project's virtual environment (`venv`).
*   **Solution:** I configured VS Code workspaces settings (`.vscode/settings.json` and `launch.json`) to strictly enforce the use of the local virtual environment, ensuring consistency across all development tools.

---

## 5. Learning Outcomes

*   **Resilient API Integration:** Learned to build robust applications that can adapt to changing third-party APIs (like AI models) by avoiding hardcoded dependencies.
*   **Environment Management:** Gained a deep understanding of Python virtual environments and how to properly configure IDEs to respect project-specific dependencies.
*   **Prompt Engineering:** Improved skills in crafting context-aware prompts (injecting database schemas) to get accurate SQL outputs from LLMs.
*   **Maintainable Code:** Understood the value of separating configuration from logic (using `config.json`) to make the application deployment-ready and easier to maintain.
