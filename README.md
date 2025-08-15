# WCL Time Splits Analyzer



A web-based tool for analyzing and comparing raid performance from [Warcraft Logs](https://classic.warcraftlogs.com/). This application fetches combat log data, calculates detailed time splits for each fight, measures idle time between encounters, and provides special metrics for raids like Naxxramas. It's designed to help raid teams identify areas for improvement and track their progress over time.

## ✨ Features

* **Detailed Fight Analysis**: View start times, end times, and durations for all boss and trash fights relative to the start of the raid.
* **Idle Time Calculation**: Automatically calculates the downtime between each fight to identify pacing issues.
* **Dual Report Comparison**: Load two reports side-by-side to compare boss kill timings and see your improvements at a glance. Time differences (deltas) are clearly marked as faster (▼) or slower (▲).
* **Naxxramas Wing Splits**: For Naxxramas logs, the tool automatically calculates and displays the clear time for each wing (Spider, Plague, Abomination, Military).
* **Trash Fight Toggle**: Easily show or hide trash fights to focus on the data that matters most to you.
* **Responsive Design**: A clean, dark-mode UI that works on both desktop and mobile devices.

## 🛠️ Tech Stack

* **Backend**: Python with Flask
* **API Client**: Requests
* **Frontend**: HTML5, CSS3, vanilla JavaScript (with Fetch API)
* **WSGI Server**: Gunicorn
* **Containerization**: Docker

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* Docker (optional, for containerized deployment)
* A Warcraft Logs (WCL) v1 API Key

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/wcl-analyzer.git](https://github.com/your-username/wcl-analyzer.git)
    cd wcl-analyzer
    ```

2.  **Set Up Environment Variables**
    You need a WCL v1 Public API key. You can get one from your [WCL profile settings](https://www.warcraftlogs.com/profile).

    Create a file named `.env` in the root of the project directory and add your API key:
    ```
    WCL_API_KEY="your_api_key_here"
    ```
    The application will load this variable automatically.

### Running the Application

You can run the application locally using Python or with Docker.

#### Method 1: Running Locally

1.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Flask application:**
    ```bash
    flask run
    # Or 'python app.py' (on port `8080`)
    ```
    The application will be available at `http://127.0.0.1:5000`.

#### Method 2: Running with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t wcl-analyzer .
    ```

2.  **Run the Docker container:**
    Make sure your `.env` file is created as described above.
    ```bash
    docker run --rm -p 8080:8080 --env-file .env wcl-analyzer
    ```
    The application will be available at `http://localhost:8080`.

##  kullanım

1.  Navigate to the application URL in your web browser.
2.  Find the Report ID you want to analyze from Warcraft Logs. The ID is the string of characters in the URL, e.g., `aBcDeFgHiJkL1234` from `https://classic.warcraftlogs.com/reports/aBcDeFgHiJkL1234`.
3.  Enter the ID into the "Report ID 1" field.
4.  Optionally, enter a second report ID to compare against.
5.  Click "Analyze". The processed data will be displayed in one or two cards below the form.