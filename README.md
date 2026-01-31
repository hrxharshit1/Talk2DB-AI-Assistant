# Talk2DB-AI-Assistant

An intelligent data assistant that lets users query MySQL databases using plain English. Built with Flask and Google Gemini AI to auto-generate and execute SQL safely.

## 🚀 Features

*   **Natural Language to SQL:** Convert plain English questions into complex SQL queries.
*   **Automatic execution:** Securely executes the generated SQL against your connected database.
*   **Smart Summarization:** Explains the query results in friendly, human-readable text.
*   **Dynamic Configuration:** Easily switch between different AI models (e.g., Gemini 1.5, Gemini 2.0) via a config file.
*   **Modern UI:** Clean and responsive interface.

## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **AI:** Google Gemini API (`google-genai`)
*   **Database:** MySQL (`mysql-connector-python`)
*   **Frontend:** HTML, CSS, JavaScript

## ⚙️ Setup & Installation

1.  **Clone the repository** (or download code).
2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuration:**
    *   The project uses a `config.json` file for settings.
    *   Ensure `config.json` exists in the root directory with your API key and preferred model:
    ```json
    {
        "GOOGLE_API_KEY": "YOUR_API_KEY_HERE",
        "GEMINI_MODEL_NAME": "gemini-2.0-flash"
    }
    ```

## 🏃‍♂️ How to Run

**Option 1: Using the Batch Script (Recommended for Windows)**
Simply double-click `run_app.bat` or run it from the terminal:
```bash
.\run_app.bat
```

**Option 2: Using VS Code**
1.  Open the project in VS Code.
2.  Go to the "Run and Debug" tab.
3.  Select **"Python: Flask (venv)"**.
4.  Click the green Play button.

## 📝 Usage

1.  Open your browser to `http://127.0.0.1:5000`.
2.  Enter your MySQL database credentials (Host, User, Password, Database).
3.  Click **Connect**.
4.  Once connected, type a question like:
    *   *"Show me all employees in the IT department"*
    *   *"What is the total revenue for last month?"*
5.  The AI will generate the SQL, run it, and show you the answer!
