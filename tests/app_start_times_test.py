# -*- coding: utf-8 -*-
"""
WCL Time Splits Analyzer - Test Version with Start Times for Best Segments

This is a test version that uses start_time_rel instead of end_time_rel
for best segments calculation to match the reference app behavior.
"""

import os
import requests
import json
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Initialize the Flask App
app = Flask(__name__)

# ==============================================================================
# CONFIGURATION DATA
# ==============================================================================

# Zone ID mapping for different WoW versions
ZONE_ID_MAP = {
    # Classic IDs
    1000: "Molten Core",
    1002: "Blackwing Lair",
    1005: "Temple of Ahn'Qiraj",
    1006: "Naxxramas",
    # Season of Discovery / Fresh IDs
    1017: "Blackfathom Deeps",
    1032: "Gnomeregan",
    1034: "Blackwing Lair",
    1035: "Temple of Ahn'Qiraj",
    1036: "Naxxramas",
    # Era IDs
    531: "Temple of Ahn'Qiraj",
    533: "Naxxramas",
}

# Naxxramas wing configuration for wing clear times
NAXX_CONFIG = {
    "wing_bosses": {
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
        if zone_id in ZONE_ID_MAP:
            zone_name = ZONE_ID_MAP[zone_id]
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
        if top_level_zone_id in ZONE_ID_MAP:
            primary_zone_name = ZONE_ID_MAP[top_level_zone_id]
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
                official_end_time = complete_raid.get
