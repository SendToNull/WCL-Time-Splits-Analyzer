# -*- coding: utf-8 -*-
"""
WCL Time Splits Analyzer - Production Version

A Flask web application for analyzing and comparing Warcraft Logs (WCL) combat reports.
Provides detailed timing analysis with multiple run comparisons and timeline visualization.
"""

import os
import requests
import json
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from config import get_config

# Initialize the Flask App with correct template path
app = Flask(__name__, template_folder='../templates')

# Load configuration
config_obj = get_config()
app.config.from_object(config_obj)

# Validate production configuration if needed
if app.config.get('FLASK_ENV') == 'production':
    config_obj.validate()

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def format_timestamp(ms, include_hours=True):
    """
    Format timestamp using exact Google Apps Script logic.
    
    This matches the original getStringForTimeStamp function exactly,
    using Math.floor() for all calculations to ensure consistent results.
    """
    if not isinstance(ms, (int, float)):
        return "---"

    # Handle negative durations for delta calculations
    sign = "-" if ms < 0 else ""
    
    # Convert to seconds using the exact original logic
    delta = abs(ms) / 1000
    
    # Original Google Apps Script logic:
    # var days = Math.floor(delta / 86400);
    # delta -= days * 86400;
    # var hours = Math.floor(delta / 3600) % 24;
    # delta -= hours * 3600;
    # var minutes = Math.floor(delta / 60) % 60;
    # delta -= minutes * 60;
    # var seconds = Math.floor(delta % 60);
    
    days = math.floor(delta / 86400)
    delta -= days * 86400
    hours = math.floor(delta / 3600) % 24
    delta -= hours * 3600
    minutes = math.floor(delta / 60) % 60
    delta -= minutes * 60
    seconds = math.floor(delta % 60)

    # Format with leading zeros
    seconds_string = f"{seconds:02d}"
    minutes_string = f"{minutes:02d}"

    if include_hours:
        return f"{sign}{hours}:{minutes_string}:{seconds_string}"
    else:
        return f"{sign}{minutes_string}:{seconds_string}"


def get_wcl_data(report_id, api_key):
    """Fetch fight data from WCL v1 API with multiple endpoint support."""
    if not report_id or not report_id.strip():
        return {"error": "Report ID cannot be empty"}
    
    report_id = report_id.strip()
    
    # Extract report ID from URL if needed
    if "warcraftlogs.com/reports/" in report_id:
        try:
            report_id = report_id.split("reports/")[1].split("#")[0].split("?")[0]
        except IndexError:
            return {"error": "Invalid report URL format"}
    
    # Validate report ID format
    if not report_id.replace('-', '').replace('_', '').isalnum():
        return {"error": f"Invalid report ID format: {report_id}"}
    
    # Try multiple endpoints
    endpoints = [
        ("classic", f"https://classic.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}"),
        ("fresh", f"https://fresh.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}")
    ]
    
    last_error = None
    for endpoint_name, url in endpoints:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("error") and data.get("fights"):
                print(f"Successfully fetched report {report_id} from {endpoint_name}.warcraftlogs.com")
                return data
            elif data.get("error"):
                last_error = data["error"]
                
        except requests.exceptions.Timeout:
            last_error = f"Request timeout for {endpoint_name}.warcraftlogs.com"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                last_error = f"Report not found on {endpoint_name}.warcraftlogs.com"
            elif e.response.status_code == 401:
                last_error = "Invalid API key or insufficient permissions"
            else:
                last_error = f"HTTP {e.response.status_code} error from {endpoint_name}.warcraftlogs.com"
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            last_error = f"Network/parsing error from {endpoint_name}.warcraftlogs.com: {str(e)}"
    
    return {"error": last_error or f"Report {report_id} not found on any WarcraftLogs endpoint"}


def find_raid_zone_times(report_data):
    """Identify primary raid zone and calculate start/end times."""
    if not report_data or "fights" not in report_data or not report_data["fights"]:
        return None, None, None, "Log data is missing or contains no fights."

    # Group fights by recognized zone
    zone_fights = {}
    for fight in report_data["fights"]:
        zone_id = fight.get("zoneID")
        if zone_id in app.config['ZONE_ID_MAP']:
            zone_name = app.config['ZONE_ID_MAP'][zone_id]
            if zone_name not in zone_fights:
                zone_fights[zone_name] = []
            zone_fights[zone_name].append(fight)

    # Determine primary zone
    if zone_fights:
        primary_zone_name = max(zone_fights, key=lambda z: len(zone_fights[z]))
        all_fights_in_zone = sorted(zone_fights[primary_zone_name], key=lambda f: f["start_time"])
    else:
        # Fallback to top-level zone
        top_level_zone_id = report_data.get("zone")
        if top_level_zone_id in app.config['ZONE_ID_MAP']:
            primary_zone_name = app.config['ZONE_ID_MAP'][top_level_zone_id]
            all_fights_in_zone = sorted(report_data["fights"], key=lambda f: f["start_time"])
        else:
            return None, None, None, "No fights found in a recognized raid zone."

    # Filter for valid fights (>4 seconds, with enemy encounters)
    valid_fights = []
    for fight in all_fights_in_zone:
        if (fight.get("name") != "Unknown" and 
            fight.get("end_time", 0) - fight.get("start_time", 0) > 4000):
            
            # Check for enemy encounters
            has_enemies = False
            if "enemies" in report_data:
                for enemy in report_data["enemies"]:
                    if enemy.get("type") in ["NPC", "Boss"]:
                        for enemy_fight in enemy.get("fights", []):
                            if enemy_fight.get("id") == fight.get("id"):
                                has_enemies = True
                                break
                        if has_enemies:
                            break
            else:
                # Fallback for missing enemies data
                has_enemies = (fight.get("boss", 0) > 0 or 
                             fight.get("end_time", 0) - fight.get("start_time", 0) > 10000)
            
            if has_enemies:
                valid_fights.append(fight)
    
    if not valid_fights:
        return None, None, None, "No valid fights found in the recognized zone."

    # Calculate raid boundaries
    raid_start_time = valid_fights[0]["start_time"]
    raid_end_time = valid_fights[-1]["end_time"]

    # Use completeRaids data if available for official timing
    if "completeRaids" in report_data and report_data["completeRaids"]:
        for complete_raid in report_data["completeRaids"]:
            if complete_raid.get("start_time") == raid_start_time:
                official_end_time = complete_raid.get("end_time")
                if official_end_time and official_end_time != raid_end_time:
                    raid_end_time = official_end_time

    return primary_zone_name, raid_start_time, raid_end_time, None


def process_fights(report_data):
    """Process raw WCL fight data using exact Google Apps Script logic."""
    if not report_data or report_data.get("error"):
        return report_data

    zone_name, raid_start_time, raid_end_time, error = find_raid_zone_times(report_data)
    if error:
        return {"error": error}

    # Use the exact zone start time as zoneStart (matching Google Apps Script)
    zone_start = raid_start_time
    zone_end = raid_end_time
    
    processed = {
        "title": report_data.get("title"),
        "zone": zone_name,
        "date": datetime.fromtimestamp(report_data.get("start") / 1000).strftime("%B %d, %Y"),
        "total_duration": zone_end - zone_start,
        "fights": [],
        "timeline_data": []
    }

    # Filter valid fights using Google Apps Script logic
    valid_fights = []
    for fight in report_data["fights"]:
        # Match the Google Apps Script condition:
        # ((fight.start_time <= zoneStart && fight.end_time >= zoneStart) || 
        #  (fight.start_time <= zoneEnd && fight.end_time >= zoneEnd) || 
        #  (fight.start_time >= zoneStart && fight.end_time <= zoneEnd)) && 
        # (fight.end_time - fight.start_time > 4000)
        if (((fight["start_time"] <= zone_start and fight["end_time"] >= zone_start) or
             (fight["start_time"] <= zone_end and fight["end_time"] >= zone_end) or
             (fight["start_time"] >= zone_start and fight["end_time"] <= zone_end)) and
            (fight.get("end_time", 0) - fight.get("start_time", 0) > 4000)):
            
            # Verify enemy encounters (matching Google Apps Script logic)
            has_valid_enemies = False
            if "enemies" in report_data:
                for enemy in report_data["enemies"]:
                    if enemy.get("type") in ["NPC", "Boss"]:
                        for enemy_fight in enemy.get("fights", []):
                            if enemy_fight.get("id") == fight.get("id"):
                                has_valid_enemies = True
                                break
                        if has_valid_enemies:
                            break
            
            if has_valid_enemies:
                # Adjust fight end time if it exceeds zone end (matching Google Apps Script)
                if fight["end_time"] > zone_end:
                    fight["end_time"] = zone_end
                valid_fights.append(fight)

    if not valid_fights:
        return {"error": f"Found '{zone_name}', but no processable fights were found."}

    # Process fights using exact Google Apps Script timing logic
    is_naxx = zone_name == "Naxxramas"
    wing_clear_times = {"Abomination": 0, "Plague": 0, "Spider": 0, "Military": 0}
    previous_fight_end = -1  # Matches Google Apps Script variable name
    previous_boss_end = 0  # Track previous boss end time for individual segment calculation

    for fight in sorted(valid_fights, key=lambda f: f["start_time"]):
        is_boss = fight.get("boss", 0) > 0 and fight.get("name") != "Trash"
        
        # Calculate times using exact Google Apps Script formulas:
        # start_time_rel = fight.start_time - zoneStart
        # end_time_rel = fight.end_time - zoneStart  
        # duration = fight.end_time - fight.start_time
        start_time_rel = fight["start_time"] - zone_start
        end_time_rel = fight["end_time"] - zone_start
        duration = fight["end_time"] - fight["start_time"]
        
        # Calculate individual segment time for bosses (time from previous boss end to this boss end)
        # This matches the reference app's "Eternal" column behavior
        individual_segment_time = None
        if is_boss:
            individual_segment_time = end_time_rel - previous_boss_end
            previous_boss_end = end_time_rel
        
        # Calculate idle time using Google Apps Script logic:
        # if (previousFightEnd == -1) "---" else fight.start_time - previousFightEnd - zoneStart
        if previous_fight_end == -1:
            idle_time = None  # Will display as "---"
        else:
            idle_time = fight["start_time"] - previous_fight_end - zone_start
        
        wing_time = None

        # Naxxramas wing time calculation (matching Google Apps Script)
        if is_naxx and is_boss and fight.get("kill"):
            boss_id = fight.get("boss")
            for wing, wing_boss_ids in app.config['NAXX_CONFIG']["wing_bosses"].items():
                if boss_id in wing_boss_ids:
                    last_end_boss_time = max(wing_clear_times.values())
                    wing_time = end_time_rel - last_end_boss_time
                    wing_clear_times[wing] = end_time_rel
                    break

        processed["fights"].append({
            "name": fight["name"] if is_boss else f"{fight['name']} (Trash)",
            "is_boss": is_boss,
            "is_kill": fight.get("kill", False),
            "start_time_rel": start_time_rel,
            "end_time_rel": end_time_rel,
            "duration": duration,
            "individual_segment_time": individual_segment_time,  # New field for individual segment times
            "idle_time": idle_time,
            "wing_time": wing_time,
        })
        
        # Add to timeline data
        processed["timeline_data"].append({
            "name": fight["name"],
            "start": start_time_rel,
            "end": end_time_rel,
            "is_boss": is_boss,
            "is_kill": fight.get("kill", False)
        })
        
        # Update previousFightEnd using Google Apps Script logic:
        # previousFightEnd = fight.end_time - zoneStart
        previous_fight_end = fight["end_time"]

    return processed


def calculate_deltas(data1, data2):
    """Calculate delta times between two reports for matching boss fights."""
    if not data1 or not data2 or data1.get("error") or data2.get("error"):
        return
    
    # Create lookup map for data2 boss fights
    data2_boss_lookup = {}
    for fight in data2.get("fights", []):
        if fight["is_boss"]:
            base_name = fight["name"].replace(" (Trash)", "")
            data2_boss_lookup[base_name] = fight
    
    # Calculate deltas for matching boss fights in data1
    for fight in data1.get("fights", []):
        if fight["is_boss"]:
            base_name = fight["name"].replace(" (Trash)", "")
            if base_name in data2_boss_lookup:
                data2_fight = data2_boss_lookup[base_name]
                fight["delta"] = fight["end_time_rel"] - data2_fight["end_time_rel"]


# ==============================================================================
# FLASK ROUTES
# ==============================================================================

@app.route("/")
def index():
    """Render the main homepage."""
    return render_template("index.html")




@app.template_filter('format_timestamp')
def format_timestamp_filter(ms, include_hours=True):
    """Template filter for formatting timestamps."""
    return format_timestamp(ms, include_hours)


@app.route("/api/analyze", methods=["POST"])
def analyze_reports():
    """API endpoint to analyze WCL reports."""
    api_key = app.config.get('WCL_API_KEY')
    if not api_key:
        return jsonify({"error": "Server configuration error: WCL_API_KEY not set."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    reports = data.get("reports", [])
    if not reports:
        return jsonify({"error": "No reports provided"}), 400

    results = []
    for report_id in reports:
        if report_id and report_id.strip():
            raw_data = get_wcl_data(report_id.strip(), api_key)
            processed_data = process_fights(raw_data)
            results.append(processed_data)
        else:
            results.append(None)

    # Calculate deltas between runs if multiple reports
    if len(results) >= 2 and results[0] and results[1]:
        calculate_deltas(results[0], results[1])

    return jsonify({"results": results})


@app.route("/health")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Production-ready configuration
    port = int(os.environ.get("PORT", 8080))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
