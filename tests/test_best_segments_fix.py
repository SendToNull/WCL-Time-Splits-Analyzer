#!/usr/bin/env python3
"""
Test script to verify the Best Segments calculation fix.
This simulates the data structure and tests the logic without needing WCL API access.
"""

def format_timestamp(ms, include_hours=True):
    """Format timestamp using exact Google Apps Script logic."""
    if not isinstance(ms, (int, float)):
        return "---"

    # Handle negative durations for delta calculations
    sign = "-" if ms < 0 else ""
    
    # Convert to seconds using the exact original logic
    delta = abs(ms) / 1000
    
    import math
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

def test_best_segments_calculation():
    """Test the Best Segments calculation with mock data."""
    
    # Mock data simulating three runs with different individual segment times
    # Including both individual_segment_time and start_time_rel (cumulative) for proper testing
    mock_results = [
        {
            "title": "Base Run",
            "total_duration": 1800000,  # 30 minutes
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 120000, "start_time_rel": 120000},  # 2:00, cumulative 2:00
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 180000, "start_time_rel": 300000},   # 3:00, cumulative 5:00
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 150000, "start_time_rel": 450000}, # 2:30, cumulative 7:30
                {"name": "Twin Emperors", "is_boss": True, "individual_segment_time": 300000, "start_time_rel": 750000},      # 5:00, cumulative 12:30
                {"name": "C'Thun", "is_boss": True, "individual_segment_time": 240000, "start_time_rel": 990000},             # 4:00, cumulative 16:30
            ]
        },
        {
            "title": "Run 2",
            "total_duration": 1740000,  # 29 minutes
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 110000, "start_time_rel": 110000},  # 1:50 (BEST), cumulative 1:50
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 190000, "start_time_rel": 300000},   # 3:10, cumulative 5:00
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 140000, "start_time_rel": 440000}, # 2:20 (BEST), cumulative 7:20
                {"name": "Twin Emperors", "is_boss": True, "individual_segment_time": 320000, "start_time_rel": 760000},      # 5:20, cumulative 12:40
                {"name": "C'Thun", "is_boss": True, "individual_segment_time": 250000, "start_time_rel": 1010000},             # 4:10, cumulative 16:50
            ]
        },
        {
            "title": "Run 3", 
            "total_duration": 1680000,  # 28 minutes
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 115000, "start_time_rel": 115000},  # 1:55, cumulative 1:55
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 170000, "start_time_rel": 285000},   # 2:50 (BEST), cumulative 4:45
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 145000, "start_time_rel": 430000}, # 2:25, cumulative 7:10
                {"name": "Twin Emperors", "is_boss": True, "individual_segment_time": 280000, "start_time_rel": 710000},      # 4:40 (BEST), cumulative 11:50
                {"name": "C'Thun", "is_boss": True, "individual_segment_time": 220000, "start_time_rel": 930000},             # 3:40 (BEST), cumulative 15:30
            ]
        }
    ]
    
    # Get all unique boss names
    all_bosses = set()
    for result in mock_results:
        for fight in result["fights"]:
            if fight["is_boss"]:
                all_bosses.add(fight["name"])
    
    # Calculate best segments (this is the fixed logic)
    best_segments = {}
    theoretical_best_time = 0
    
    for boss_name in all_bosses:
        best_segment_time = None
        best_run_index = -1
        
        for result_index, result in enumerate(mock_results):
            fight = next((f for f in result["fights"] if f["name"] == boss_name and f["is_boss"]), None)
            if fight and fight["individual_segment_time"] is not None:
                if best_segment_time is None or fight["individual_segment_time"] < best_segment_time:
                    best_segment_time = fight["individual_segment_time"]
                    best_run_index = result_index
        
        if best_segment_time is not None:
            best_segments[boss_name] = best_segment_time
            theoretical_best_time += best_segment_time  # Sum of all best individual segments
            print(f"Best {boss_name} segment: {format_timestamp(best_segment_time, True)} from run {best_run_index + 1}")
    
    print(f"\nTheoretical best total time: {format_timestamp(theoretical_best_time, True)}")
    
    # Verify the calculation
    expected_best_times = {
        "The Prophet Skeram": 110000,  # 1:50 from Run 2
        "Silithid Royalty": 170000,    # 2:50 from Run 3  
        "Battleguard Sartura": 140000, # 2:20 from Run 2
        "Twin Emperors": 280000,       # 4:40 from Run 3
        "C'Thun": 220000,              # 3:40 from Run 3
    }
    
    expected_total = sum(expected_best_times.values())  # Should be 920000ms = 15:20
    
    print(f"\nExpected total: {format_timestamp(expected_total, True)}")
    print(f"Calculated total: {format_timestamp(theoretical_best_time, True)}")
    
    # Verify each boss has the correct best time
    all_correct = True
    for boss_name, expected_time in expected_best_times.items():
        if best_segments.get(boss_name) != expected_time:
            print(f"ERROR: {boss_name} expected {format_timestamp(expected_time, True)}, got {format_timestamp(best_segments.get(boss_name, 0), True)}")
            all_correct = False
    
    if theoretical_best_time != expected_total:
        print(f"ERROR: Total time mismatch. Expected {format_timestamp(expected_total, True)}, got {format_timestamp(theoretical_best_time, True)}")
        all_correct = False
    
    if all_correct:
        print("\n✅ SUCCESS: Best Segments calculation is working correctly!")
        print("The fix properly calculates the sum of individual best segment times.")
    else:
        print("\n❌ FAILURE: Best Segments calculation has issues.")
    
    return all_correct

if __name__ == "__main__":
    print("Testing Best Segments Calculation Fix")
    print("=" * 50)
    test_best_segments_calculation()
