# -*- coding: utf-8 -*-
"""
This module implements a Flask web application for analyzing and comparing
Warcraft Logs (WCL) combat reports. It provides an API to fetch log data,
process it to calculate fight timings, idle periods, and special metrics like
Naxxramas wing clear times, and then sends this data to a frontend for display.
"""

import os
import requests
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import math

# Initialize the Flask App
app = Flask(__name__)

# ==============================================================================
# CONFIGURATION DATA
# ==============================================================================

# A mapping of WCL zone IDs to their recognized raid names. This helps
# normalize data from different game versions (Classic, Era, SoD).
ZONE_ID_MAP = {
    # Classic IDs
    1000: "Molten Core",
    1002: "Blackwing Lair",
    1005: "Temple of Ahn'Qiraj",
    1006: "Naxxramas",
    # Season of Discovery / Fresh IDs
    1017: "Blackfathom Deeps",
    1032: "Gnomeregan",
    1034: "Blackwing Lair",  # SoD version
    1035: "Temple of Ahn'Qiraj",  # SoD version
    1036: "Naxxramas",  # SoD version
    # Era IDs
    531: "Temple of Ahn'Qiraj",
    533: "Naxxramas",
}

# Configuration specific to the Naxxramas raid zone for calculating wing clear times.
NAXX_CONFIG = {
    "wing_bosses": {
        # Using sets to hold multiple possible WCL NPC IDs for each end-of-wing boss.
        # This accounts for different game versions or potential ID changes.
        "Spider": {15952, 51116},  # Maexxna
        "Plague": {15954, 51117},  # Loatheb
        "Abomination": {16028, 51118},  # Thaddius
        "Military": {16061, 51113},  # The Four Horsemen
    }
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def format_timestamp(ms, include_hours=True):
    """Formats a duration in milliseconds into a human-readable string (H:MM:SS or MM:SS).

    Args:
        ms (int or float): The duration in milliseconds.
        include_hours (bool): If True, format as H:MM:SS. Otherwise, MM:SS.

    Returns:
        str: The formatted time string, or "---" if the input is invalid.
    """
    if not isinstance(ms, (int, float)):
        return "---"

    # Handle negative durations for delta calculations
    sign = "-" if ms < 0 else ""
    total_seconds = round(abs(ms) / 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if include_hours:
        # :02d ensures minutes and seconds are two digits, e.g., 05 instead of 5.
        return f"{sign}{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{sign}{minutes:02d}:{seconds:02d}"


def get_wcl_data(report_id, api_key):
    """Fetches fight data for a given report ID from the WCL v1 API.

    Args:
        report_id (str): The unique identifier for the WCL report.
        api_key (str): The user's WCL API key.

    Returns:
        dict: The JSON response from the API as a dictionary, or an error dictionary.
    """
    if not report_id or not report_id.strip():
        return {"error": "Report ID cannot be empty"}
    
    report_id = report_id.strip()
    
    # Validate report ID format (alphanumeric, typically 16 characters)
    if not report_id.replace('-', '').replace('_', '').isalnum():
        return {"error": f"Invalid report ID format: {report_id}"}
    
    # Try classic.warcraftlogs.com first, then fall back to fresh.warcraftlogs.com
    # This order prioritizes the original/classic endpoint which has been around longer
    endpoints = [
        ("classic", f"https://classic.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}"),
        ("fresh", f"https://fresh.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}")
    ]
    
    last_error = None
    for endpoint_name, url in endpoints:
        try:
            response = requests.get(url, timeout=30)  # Add timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            
            # Check if we got valid data (not an error response)
            if not data.get("error") and data.get("fights"):
                print(f"Successfully fetched report {report_id} from {endpoint_name}.warcraftlogs.com")
                return data
            elif data.get("error"):
                last_error = data["error"]
                print(f"API error from {endpoint_name}.warcraftlogs.com: {last_error}")
            else:
                print(f"No fights data from {endpoint_name}.warcraftlogs.com")
                
        except requests.exceptions.Timeout:
            last_error = f"Request timeout for {endpoint_name}.warcraftlogs.com"
            print(last_error)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                last_error = f"Report not found on {endpoint_name}.warcraftlogs.com"
            elif e.response.status_code == 401:
                last_error = "Invalid API key or insufficient permissions"
            else:
                last_error = f"HTTP {e.response.status_code} error from {endpoint_name}.warcraftlogs.com"
            print(last_error)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            last_error = f"Network/parsing error from {endpoint_name}.warcraftlogs.com: {str(e)}"
            print(last_error)
    
    # Return the most specific error message
    if last_error:
        return {"error": last_error}
    else:
        return {"error": f"Report {report_id} not found on any WarcraftLogs endpoint"}


def find_raid_zone_times(report_data):
    """Identifies the primary raid zone and its start/end times from the report data.

    This function determines the main raid instance by finding which recognized
    zone has the most recorded fights.

    Args:
        report_data (dict): The raw JSON data from the WCL API.

    Returns:
        tuple: A tuple containing (primary_zone_name, raid_start_time, raid_end_time, error_message).
               On failure, the first three elements are None and the error_message is set.
    """
    if not report_data or "fights" not in report_data or not report_data["fights"]:
        return None, None, None, "Log data is missing or contains no fights."

    zone_fights = {}
    unrecognized_zones = set()

    # Group fights by their recognized zone name
    for fight in report_data["fights"]:
        zone_id, zone_name = fight.get("zoneID"), fight.get("zoneName")
        if zone_id in ZONE_ID_MAP:
            recognized_name = ZONE_ID_MAP[zone_id]
            if recognized_name not in zone_fights:
                zone_fights[recognized_name] = []
            zone_fights[recognized_name].append(fight)
        elif zone_name:
            unrecognized_zones.add(f"{zone_name} (ID: {zone_id})")

    # Determine the primary zone based on which has the most fights
    if zone_fights:
        primary_zone_name = max(zone_fights, key=lambda z: len(zone_fights[z]))
        all_fights_in_zone = sorted(
            zone_fights[primary_zone_name], key=lambda f: f["start_time"]
        )
    else:
        # Fallback for logs where individual fights don't have zone IDs
        top_level_zone_id = report_data.get("zone")
        if top_level_zone_id in ZONE_ID_MAP:
            primary_zone_name = ZONE_ID_MAP[top_level_zone_id]
            all_fights_in_zone = sorted(
                report_data["fights"], key=lambda f: f["start_time"]
            )
        else:
            # Handle cases where no recognized raid zone is found
            error_msg = "No fights found in a recognized raid zone."
            if unrecognized_zones:
                error_msg += (
                    f" Unsupported zones found: {', '.join(unrecognized_zones)}."
                )
            return None, None, None, error_msg

    if not all_fights_in_zone:
        return None, None, None, "Could not find any fights in the recognized zone."

    # Exclude "Unknown" fights from raid timing calculation
    real_fights_in_zone = [f for f in all_fights_in_zone if f.get("name") != "Unknown"]
    
    if not real_fights_in_zone:
        return None, None, None, "No valid fights found in the recognized zone (only 'Unknown' fights)."

    # The raid's effective start time is the beginning of the first real fight
    raid_start_time = real_fights_in_zone[0]["start_time"]
    # The raid's effective end time is the conclusion of the last real fight
    raid_end_time = real_fights_in_zone[-1]["end_time"]

    return primary_zone_name, raid_start_time, raid_end_time, None


def process_fights(report_data):
    """Processes raw WCL fight data into a structured format for the frontend.

    This function calculates relative timings, idle times between fights, and
    special metrics like Naxxramas wing clear times.

    Args:
        report_data (dict): The raw JSON data from the WCL API.

    Returns:
        dict: A dictionary containing structured report information and a list of
              processed fights, or an error dictionary if processing fails.
    """
    if not report_data or report_data.get("error"):
        return report_data  # Pass through any existing errors

    zone_name, raid_start_time, raid_end_time, error = find_raid_zone_times(report_data)
    if error:
        return {"error": error}

    processed = {
        "title": report_data.get("title"),
        "zone": zone_name,
        "date": datetime.fromtimestamp(report_data.get("start") / 1000).strftime(
            "%B %d, %Y"
        ),
        "total_duration": raid_end_time - raid_start_time,
        "fights": [],
    }

    last_fight_end_s = 0
    is_naxx = zone_name == "Naxxramas"
    # Store the cumulative time at which each Naxx wing was cleared
    wing_clear_times = {"Abomination": 0, "Plague": 0, "Spider": 0, "Military": 0}

    # Filter for fights that occurred within the primary raid instance timeline
    # Exclude "Unknown" fights from processing but also from raid timing calculation
    relevant_fights = [
        f
        for f in report_data["fights"]
        if raid_start_time <= f["start_time"] <= raid_end_time
        and f.get("name") != "Unknown"
    ]
    if not relevant_fights:
        return {
            "error": f"Found '{zone_name}', but no processable fights were found within its timeline."
        }

    # Process fights chronologically
    for fight in sorted(relevant_fights, key=lambda f: f["start_time"]):
        # Calculate times relative to the raid start, converting from ms to seconds
        start_s = round((fight["start_time"] - raid_start_time) / 1000)
        end_s = round((fight["end_time"] - raid_start_time) / 1000)

        is_boss = fight.get("boss", 0) > 0 and fight.get("name") != "Trash"
        wing_time = None

        # Naxxramas-specific logic for wing time calculation
        if is_naxx and is_boss and fight.get("kill"):
            boss_id = fight.get("boss")
            for wing, wing_boss_ids in NAXX_CONFIG["wing_bosses"].items():
                if boss_id in wing_boss_ids:
                    # Time of this wing clear is the duration from the previous wing's clear
                    last_end_boss_time = max(wing_clear_times.values())
                    current_kill_time = fight["end_time"] - raid_start_time
                    wing_time = current_kill_time - last_end_boss_time
                    wing_clear_times[wing] = current_kill_time
                    break

        processed["fights"].append(
            {
                "name": fight["name"] if is_boss else f"{fight['name']} (Trash)",
                "is_boss": is_boss,
                "is_kill": fight.get("kill", False),
                "start_time_rel": start_s * 1000,  # Convert back to ms for frontend
                "end_time_rel": end_s * 1000,
                "duration": (end_s - start_s) * 1000,
                "idle_time": (start_s - last_fight_end_s if last_fight_end_s > 0 else 0)
                * 1000,
                "wing_time": wing_time,
            }
        )
        last_fight_end_s = end_s

    return processed


# ==============================================================================
# FLASK ROUTES
# ==============================================================================
@app.route("/")
def index():
    """Renders the main homepage."""
    return render_template("index.html")


@app.route("/report", methods=["POST"])
def report():
    """API endpoint to fetch and process WCL report data."""
    api_key = os.getenv("WCL_API_KEY")
    if not api_key:
        return (
            jsonify({"error": "Server configuration error: WCL_API_KEY not set."}),
            500,
        )

    report_id1 = request.form.get("report_id1")
    report_id2 = request.form.get("report_id2")

    # Process the first report if its ID is provided
    processed_data1 = (
        process_fights(get_wcl_data(report_id1, api_key)) if report_id1 else None
    )

    # Process the second report if its ID is provided
    processed_data2 = (
        process_fights(get_wcl_data(report_id2, api_key)) if report_id2 else None
    )

    return jsonify({"data1": processed_data1, "data2": processed_data2})


# Main entry point for the application
if __name__ == "__main__":
    # The application runs in debug mode for development.
    # It binds to 0.0.0.0 to be accessible from outside a container.
    # The PORT is read from environment variables, defaulting to 8080.
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
