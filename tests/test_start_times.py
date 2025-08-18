#!/usr/bin/env python3
"""
Test script to experiment with using start times instead of end times
for boss calculations to see if it matches the reference app better.
"""

import json
import math
from datetime import datetime

def format_timestamp(ms, include_hours=True):
    """Format timestamp using exact Google Apps Script logic."""
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

def test_timing_approaches():
    """Test different timing approaches with sample data."""
    
    # Sample fight data from the debug output we saw
    sample_fights = [
        {"name": "The Prophet Skeram", "start_time_rel": 39399, "end_time_rel": 77412, "duration": 38013},
        {"name": "Silithid Royalty", "start_time_rel": 186569, "end_time_rel": 223950, "duration": 37381},
        {"name": "Battleguard Sartura", "start_time_rel": 308044, "end_time_rel": 341691, "duration": 33647},
        {"name": "Fankriss the Unyielding", "start_time_rel": 413020, "end_time_rel": 445044, "duration": 32024},
        {"name": "Viscidus", "start_time_rel": 503933, "end_time_rel": 579531, "duration": 75598},
        {"name": "Princess Huhuran", "start_time_rel": 701822, "end_time_rel": 730526, "duration": 28704},
        {"name": "Twin Emperors", "start_time_rel": 884239, "end_time_rel": 1000476, "duration": 116237},
        {"name": "Ouro", "start_time_rel": 1329030, "end_time_rel": 1379264, "duration": 50234},
        {"name": "C'Thun", "start_time_rel": 1460234, "end_time_rel": 1591538, "duration": 131304},
    ]
    
    # Expected values from reference app (Eternal column)
    expected_values = {
        "The Prophet Skeram": "0:39",
        "Silithid Royalty": "3:06", 
        "Battleguard Sartura": "5:08",
        "Fankriss the Unyielding": "6:53",
        "Viscidus": "8:23",
        "Princess Huhuran": "11:41",
        "Twin Emperors": "14:44",
        "Ouro": "22:09",
        "C'Thun": "24:20"
    }
    
    print("=== TIMING APPROACH COMPARISON ===\n")
    
    print("Boss Name                | Current (End Time) | Start Time Approach | Expected (Reference) | Duration")
    print("-" * 95)
    
    for fight in sample_fights:
        boss_name = fight["name"]
        
        # Current approach: end_time_rel (cumulative time from raid start to boss kill)
        current_time = format_timestamp(fight["end_time_rel"], True)
        
        # Start time approach: start_time_rel (cumulative time from raid start to boss pull)
        start_time = format_timestamp(fight["start_time_rel"], True)
        
        # Duration approach: just the fight duration
        duration_time = format_timestamp(fight["duration"], True)
        
        # Expected from reference
        expected = expected_values.get(boss_name, "N/A")
        
        print(f"{boss_name:<24} | {current_time:<18} | {start_time:<19} | {expected:<20} | {duration_time}")
    
    print("\n=== ANALYSIS ===")
    print("Current Approach (End Time): Shows cumulative time from raid start to boss kill")
    print("Start Time Approach: Shows cumulative time from raid start to boss pull")
    print("Expected (Reference): Shows individual best segment times (not cumulative)")
    print("\nNone of these approaches match the reference because the reference shows")
    print("'best segments' - the best individual performance for each boss across multiple runs.")
    
    print("\n=== CONVERSION TO MATCH REFERENCE ===")
    print("To match the reference, we need to calculate individual segment times:")
    print("Boss Name                | Individual Segment Time | Expected (Reference)")
    print("-" * 70)
    
    previous_end = 0
    for i, fight in enumerate(sample_fights):
        boss_name = fight["name"]
        
        # Calculate individual segment time (time from previous boss end to this boss end)
        if i == 0:
            # First boss: time from raid start to boss end
            segment_time = fight["end_time_rel"]
        else:
            # Subsequent bosses: time from previous boss end to this boss end
            segment_time = fight["end_time_rel"] - previous_end
        
        segment_formatted = format_timestamp(segment_time, False)  # No hours for shorter format
        expected = expected_values.get(boss_name, "N/A")
        
        print(f"{boss_name:<24} | {segment_formatted:<23} | {expected}")
        
        previous_end = fight["end_time_rel"]
    
    print("\n=== CONCLUSION ===")
    print("The reference app shows 'best individual segment times', not cumulative times.")
    print("To match it, we need to:")
    print("1. Calculate individual segment times for each boss")
    print("2. Compare across multiple runs to find the best segment for each boss")
    print("3. Display those best segments as the 'Eternal' column")

if __name__ == "__main__":
    test_timing_approaches()
