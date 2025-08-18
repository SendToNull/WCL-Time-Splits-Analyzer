#!/usr/bin/env python3
"""
Test script to verify the Best Segments display logic matches the reference app.
This tests both the calculation and display behavior.
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

def test_display_logic():
    """Test that the display logic matches the reference app behavior."""
    
    print("Testing Best Segments Display Logic")
    print("=" * 50)
    
    # Mock data based on the reference app screenshot
    mock_results = [
        {
            "title": "aq40 pump",
            "total_duration": 1603000,  # 26:43
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 55000, "start_time_rel": 55000},    # 0:55, cumulative 0:55
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 150000, "start_time_rel": 205000},   # 2:30, cumulative 3:25
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 104000, "start_time_rel": 309000}, # 1:44, cumulative 5:09
            ]
        },
        {
            "title": "run 2", 
            "total_duration": 1591000,  # 26:31
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 39000, "start_time_rel": 39000},    # 0:39 (BEST), cumulative 0:39
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 147000, "start_time_rel": 186000},   # 2:27, cumulative 3:06
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 122000, "start_time_rel": 308000}, # 2:02, cumulative 5:08
            ]
        },
        {
            "title": "GT AQ 14/08",
            "total_duration": 1852000,  # 30:52
            "fights": [
                {"name": "The Prophet Skeram", "is_boss": True, "individual_segment_time": 57000, "start_time_rel": 57000},    # 0:57, cumulative 0:57
                {"name": "Silithid Royalty", "is_boss": True, "individual_segment_time": 126000, "start_time_rel": 183000},   # 2:06 (BEST), cumulative 4:03
                {"name": "Battleguard Sartura", "is_boss": True, "individual_segment_time": 105000, "start_time_rel": 288000}, # 1:45, cumulative 4:48
            ]
        }
    ]
    
    # Get all unique boss names
    all_bosses = set()
    for result in mock_results:
        for fight in result["fights"]:
            if fight["is_boss"]:
                all_bosses.add(fight["name"])
    
    # Calculate best segments using the fixed logic
    best_segments = {}
    best_segments_cumulative = {}
    theoretical_best_time = 0
    
    for boss_name in all_bosses:
        best_segment_time = None
        best_cumulative_time = None
        best_run_index = -1
        
        for result_index, result in enumerate(mock_results):
            fight = next((f for f in result["fights"] if f["name"] == boss_name and f["is_boss"]), None)
            if fight and fight["individual_segment_time"] is not None:
                if best_segment_time is None or fight["individual_segment_time"] < best_segment_time:
                    best_segment_time = fight["individual_segment_time"]
                    best_cumulative_time = fight["start_time_rel"]  # Store cumulative for display
                    best_run_index = result_index
        
        if best_segment_time is not None:
            best_segments[boss_name] = best_segment_time  # For total calculation
            best_segments_cumulative[boss_name] = best_cumulative_time  # For individual display
            theoretical_best_time += best_segment_time  # Sum of best individual segments
    
    print("Individual Boss Best Segments (Display Values - Cumulative Times):")
    print("-" * 60)
    for boss_name in sorted(all_bosses):
        if boss_name in best_segments_cumulative:
            cumulative_time = best_segments_cumulative[boss_name]
            individual_time = best_segments[boss_name]
            print(f"{boss_name:25} | Display: {format_timestamp(cumulative_time, True):>8} | Individual: {format_timestamp(individual_time, True):>8}")
    
    print(f"\nTotal Run Time Best Segments (Sum of Individual Segments):")
    print(f"Theoretical Best: {format_timestamp(theoretical_best_time, True)}")
    
    # Expected values based on the reference app
    expected_display_values = {
        "The Prophet Skeram": 39000,    # 0:39 from run 2
        "Silithid Royalty": 183000,     # 3:03 from GT AQ 14/08 (cumulative time where best individual segment occurs)
        "Battleguard Sartura": 309000,  # 5:09 from aq40 pump (cumulative time where best individual segment occurs)
    }
    
    expected_individual_segments = {
        "The Prophet Skeram": 39000,    # 0:39 from run 2
        "Silithid Royalty": 126000,     # 2:06 from GT AQ 14/08
        "Battleguard Sartura": 104000,  # 1:44 from aq40 pump
    }
    
    expected_total = sum(expected_individual_segments.values())  # Sum of individual segments
    
    print(f"\nVerification:")
    print(f"Expected total: {format_timestamp(expected_total, True)}")
    print(f"Calculated total: {format_timestamp(theoretical_best_time, True)}")
    
    # Verify the logic
    all_correct = True
    
    # Check individual segment calculations (for total)
    for boss_name, expected_time in expected_individual_segments.items():
        if best_segments.get(boss_name) != expected_time:
            print(f"ERROR: {boss_name} individual segment expected {format_timestamp(expected_time, True)}, got {format_timestamp(best_segments.get(boss_name, 0), True)}")
            all_correct = False
    
    # Check display values (cumulative times)
    for boss_name, expected_display in expected_display_values.items():
        if best_segments_cumulative.get(boss_name) != expected_display:
            print(f"ERROR: {boss_name} display value expected {format_timestamp(expected_display, True)}, got {format_timestamp(best_segments_cumulative.get(boss_name, 0), True)}")
            all_correct = False
    
    if theoretical_best_time != expected_total:
        print(f"ERROR: Total time mismatch. Expected {format_timestamp(expected_total, True)}, got {format_timestamp(theoretical_best_time, True)}")
        all_correct = False
    
    if all_correct:
        print("\n✅ SUCCESS: Display logic matches reference app!")
        print("- Individual boss rows show cumulative times from the run with best individual segment")
        print("- Total row shows sum of all best individual segments")
        print("- This matches the behavior shown in the reference screenshot")
    else:
        print("\n❌ FAILURE: Display logic has issues.")
    
    return all_correct

if __name__ == "__main__":
    test_display_logic()
