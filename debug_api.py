import os
import requests
import json
from datetime import datetime

# Get API key from environment
api_key = os.getenv("WCL_API_KEY")
if not api_key:
    print("WCL_API_KEY environment variable not set")
    exit(1)

report_id = "xkTQz4GyjJ6XFbhw"  # Classic report

# Test both endpoints
endpoints = [
    ("classic", f"https://classic.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}"),
    ("fresh", f"https://fresh.warcraftlogs.com:443/v1/report/fights/{report_id}?translate=true&api_key={api_key}")
]

for name, url in endpoints:
    print(f"\n=== Testing {name}.warcraftlogs.com ===")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            print(f"API Error: {data['error']}")
            continue
            
        if not data.get("fights"):
            print("No fights data")
            continue
            
        print(f"Success! Found {len(data['fights'])} fights")
        print(f"Report title: {data.get('title', 'N/A')}")
        print(f"Report start timestamp: {data.get('start', 'N/A')}")
        print(f"Report zone: {data.get('zone', 'N/A')}")
        
        # Show first few fights to understand structure
        print("First 5 fights:")
        for i, fight in enumerate(data["fights"][:5]):
            print(f"  Fight {i+1}: {fight.get('name', 'N/A')} - Zone: {fight.get('zoneID', 'N/A')} ({fight.get('zoneName', 'N/A')})")
            print(f"    Start: {fight.get('start_time', 'N/A')}ms, End: {fight.get('end_time', 'N/A')}ms")
        
        # Calculate total duration using all fights
        all_fights = sorted(data["fights"], key=lambda f: f["start_time"])
        if all_fights:
            first_fight = all_fights[0]
            last_fight = all_fights[-1]
            
            print(f"\nFirst fight: {first_fight['name']} at {first_fight['start_time']}ms")
            print(f"Last fight: {last_fight['name']} at {last_fight['end_time']}ms")
            
            total_duration_ms = last_fight["end_time"] - first_fight["start_time"]
            total_duration_seconds = total_duration_ms / 1000
            minutes = int(total_duration_seconds // 60)
            seconds = int(total_duration_seconds % 60)
            
            print(f"Total duration (including Unknown): {minutes}:{seconds:02d} ({total_duration_ms}ms)")
            
            # Try excluding "Unknown" fights
            real_fights = [f for f in all_fights if f.get("name") != "Unknown"]
            if real_fights:
                first_real = real_fights[0]
                last_real = real_fights[-1]
                
                print(f"\nExcluding 'Unknown' fights:")
                print(f"First real fight: {first_real['name']} at {first_real['start_time']}ms")
                print(f"Last real fight: {last_real['name']} at {last_real['end_time']}ms")
                
                real_duration_ms = last_real["end_time"] - first_real["start_time"]
                real_duration_seconds = real_duration_ms / 1000
                real_minutes = int(real_duration_seconds // 60)
                real_seconds = int(real_duration_seconds % 60)
                
                print(f"Total duration (excluding Unknown): {real_minutes}:{real_seconds:02d} ({real_duration_ms}ms)")
            
    except Exception as e:
        print(f"Error: {e}")
