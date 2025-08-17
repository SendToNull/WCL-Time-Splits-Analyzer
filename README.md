# WCL Time Splits Analyzer

A web-based tool for analyzing and comparing raid performance from [Warcraft Logs](https://warcraftlogs.com/). This application fetches combat log data from both Classic and Fresh WarcraftLogs, calculates detailed time splits for each fight, measures idle time between encounters, and provides special metrics for raids like Naxxramas. It's designed to help raid teams identify areas for improvement and track their progress over time.

## ✨ Features

### **Core Analysis**
* **Detailed Fight Analysis**: View start times, end times, and durations for all boss and trash fights relative to the start of the raid
* **Accurate Timing**: Properly excludes "Unknown" fights from timing calculations for precise raid duration measurements
* **Idle Time Calculation**: Automatically calculates the downtime between each fight to identify pacing issues

### **Comparison & Visualization**
* **Dual Report Comparison**: Load two reports side-by-side to compare boss kill timings and see improvements at a glance
* **Enhanced Delta Display**: Time differences are clearly marked as faster (▼ green) or slower (▲ red) with bold highlighting
* **Naxxramas Wing Splits**: For Naxxramas logs, automatically calculates and displays clear time for each wing (Spider, Plague, Abomination, Military)

### **User Experience**
* **Flexible Input**: Accept both report IDs and full WarcraftLogs URLs - just paste either format
* **Multi-Platform Support**: Automatically detects and fetches from both classic.warcraftlogs.com and fresh.warcraftlogs.com
* **Trash Fight Toggle**: Easily show or hide trash fights to focus on the data that matters most
* **Responsive Design**: Clean, dark-mode UI that works on desktop and mobile devices
* **Better Error Handling**: Clear, specific error messages help troubleshoot issues

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

    Copy the example environment file and add your API key:
    ```bash
    cp .env.example .env
    ```
    
    Then edit `.env` and replace `your_api_key_here` with your actual API key:
    ```
    WCL_API_KEY="your_actual_api_key_here"
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

## 📖 Usage

### **Basic Analysis**
1. Navigate to the application URL in your web browser
2. Enter a report ID or paste a full WarcraftLogs URL in the "Report ID 1" field
   - **Report ID**: `xkTQz4GyjJ6XFbhw`
   - **Full URL**: `https://classic.warcraftlogs.com/reports/xkTQz4GyjJ6XFbhw`
   - **Fresh URL**: `https://fresh.warcraftlogs.com/reports/WqaDLpJjXzM9ymfK`
3. Click "Analyze" to process the report

### **Comparison Analysis**
1. Enter your primary report in "Report ID 1"
2. Enter a comparison report in "Report ID 2" (optional)
3. Click "Analyze" to see side-by-side comparison with delta times

### **Understanding the Results**
- **Green ▼ arrows**: Faster times compared to the second report
- **Red ▲ arrows**: Slower times compared to the second report
- **Idle Time**: Time spent between fights (useful for identifying pacing issues)
- **Wing Time**: For Naxxramas, shows time to clear each wing
- **Total Run Time**: Complete raid duration (excluding "Unknown" fights)

## 🔧 Supported Raids

The application automatically detects and supports:
- **Classic WoW**: Molten Core, Blackwing Lair, Temple of Ahn'Qiraj, Naxxramas
- **Season of Discovery**: Blackfathom Deeps, Gnomeregan, Blackwing Lair, Temple of Ahn'Qiraj, Naxxramas
- **Fresh Servers**: All supported Classic raids

## 🐛 Troubleshooting

### Common Issues
- **"Report not found"**: Verify the report ID is correct and the report is public
- **"Invalid API key"**: Check your WCL_API_KEY environment variable
- **"No fights found"**: The report may not contain supported raid content
- **Timeout errors**: Large reports may take longer to process

### Getting Help
If you encounter issues:
1. Check that your API key is valid and has proper permissions
2. Verify the report is public and contains raid data
3. Try with a different report to isolate the issue

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Warcraft Logs](https://warcraftlogs.com/) for providing the combat log data API
- The Classic WoW community for feedback and testing
