#!/usr/bin/env python3
"""
Test script to verify the best segments calculation and display logic.
This creates mock data to test the frontend functionality without needing WCL API access.
"""

import json
from datetime import datetime

def create_mock_data():
    """Create mock data that simulates the structure returned by the WCL API processing."""
    
    # Mock data for base run (similar to the screenshot data)
    base_run = {
        "title": "aq40 pump",
        "zone": "Temple of Ahn'Qiraj",
        "date": "August 18, 2025",
        "total_duration": 1583000,  # 26:23 in milliseconds
        "fights": [
            {
                "name": "The Prophet Skeram",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 55000,  # 0:55
                "duration": 55000,
                "individual_segment_time": 55000,  # First boss, so segment time = end time
                "idle_time": None
            },
            {
                "name": "Silithid Royalty",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 205000,  # 3:25
                "duration": 150000,  # 2:30 fight duration
                "individual_segment_time": 150000,  # 3:25 - 0:55 = 2:30
                "idle_time": 18000  # Some idle time
            },
            {
                "name": "Battleguard Sartura",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 309000,  # 5:09
                "duration": 104000,
                "individual_segment_time": 104000,  # 5:09 - 3:25 = 1:44
                "idle_time": 12000
            },
            {
                "name": "Fankriss the Unyielding",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 432000,  # 7:12
                "duration": 123000,
                "individual_segment_time": 123000,  # 7:12 - 5:09 = 2:03
                "idle_time": 15000
            },
            {
                "name": "Viscidus",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 503000,  # 8:23
                "duration": 71000,
                "individual_segment_time": 71000,  # 8:23 - 7:12 = 1:11
                "idle_time": 8000
            },
            {
                "name": "Princess Huhuran",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 711000,  # 11:51
                "duration": 208000,
                "individual_segment_time": 208000,  # 11:51 - 8:23 = 3:28
                "idle_time": 25000
            },
            {
                "name": "Twin Emperors",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 901000,  # 15:01
                "duration": 190000,
                "individual_segment_time": 190000,  # 15:01 - 11:51 = 3:10
                "idle_time": 20000
            },
            {
                "name": "Ouro",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1332000,  # 22:12
                "duration": 431000,
                "individual_segment_time": 431000,  # 22:12 - 15:01 = 7:11
                "idle_time": 45000
            },
            {
                "name": "C'Thun",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1460000,  # 24:20
                "duration": 128000,
                "individual_segment_time": 128000,  # 24:20 - 22:12 = 2:08
                "idle_time": 15000
            }
        ],
        "timeline_data": []
    }
    
    # Mock data for comparison run 1 (run 2 in the table)
    run2 = {
        "title": "run 2",
        "zone": "Temple of Ahn'Qiraj",
        "date": "August 18, 2025",
        "total_duration": 1591000,  # 26:31 in milliseconds
        "fights": [
            {
                "name": "The Prophet Skeram",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 39000,  # 0:39 (better than base)
                "duration": 39000,
                "individual_segment_time": 39000,
                "idle_time": None
            },
            {
                "name": "Silithid Royalty",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 186000,  # 3:06 (better than base)
                "duration": 147000,
                "individual_segment_time": 147000,  # 3:06 - 0:39 = 2:27
                "idle_time": 15000
            },
            {
                "name": "Battleguard Sartura",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 308000,  # 5:08 (slightly better)
                "duration": 122000,
                "individual_segment_time": 122000,  # 5:08 - 3:06 = 2:02
                "idle_time": 18000
            },
            {
                "name": "Fankriss the Unyielding",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 413000,  # 6:53 (better than base)
                "duration": 105000,
                "individual_segment_time": 105000,  # 6:53 - 5:08 = 1:45
                "idle_time": 12000
            },
            {
                "name": "Viscidus",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 503000,  # 8:23 (same as base)
                "duration": 90000,
                "individual_segment_time": 90000,  # 8:23 - 6:53 = 1:30
                "idle_time": 10000
            },
            {
                "name": "Princess Huhuran",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 701000,  # 11:41 (better than base)
                "duration": 198000,
                "individual_segment_time": 198000,  # 11:41 - 8:23 = 3:18
                "idle_time": 22000
            },
            {
                "name": "Twin Emperors",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 884000,  # 14:44 (better than base)
                "duration": 183000,
                "individual_segment_time": 183000,  # 14:44 - 11:41 = 3:03
                "idle_time": 18000
            },
            {
                "name": "Ouro",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1329000,  # 22:09 (slightly better)
                "duration": 445000,
                "individual_segment_time": 445000,  # 22:09 - 14:44 = 7:25
                "idle_time": 50000
            },
            {
                "name": "C'Thun",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1460000,  # 24:20 (same as base)
                "duration": 131000,
                "individual_segment_time": 131000,  # 24:20 - 22:09 = 2:11
                "idle_time": 12000
            }
        ],
        "timeline_data": []
    }
    
    # Mock data for comparison run 2 (GT AQ 14/08)
    run3 = {
        "title": "GT AQ 14/08",
        "zone": "Temple of Ahn'Qiraj",
        "date": "August 14, 2025",
        "total_duration": 1872000,  # 31:12 in milliseconds
        "fights": [
            {
                "name": "The Prophet Skeram",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 57000,  # 0:57 (worse than base)
                "duration": 57000,
                "individual_segment_time": 57000,
                "idle_time": None
            },
            {
                "name": "Silithid Royalty",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 243000,  # 4:03 (worse than base)
                "duration": 186000,
                "individual_segment_time": 186000,  # 4:03 - 0:57 = 3:06
                "idle_time": 22000
            },
            {
                "name": "Battleguard Sartura",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 348000,  # 5:48 (worse than base)
                "duration": 105000,
                "individual_segment_time": 105000,  # 5:48 - 4:03 = 1:45
                "idle_time": 15000
            },
            {
                "name": "Fankriss the Unyielding",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 475000,  # 7:55 (worse than base)
                "duration": 127000,
                "individual_segment_time": 127000,  # 7:55 - 5:48 = 2:07
                "idle_time": 18000
            },
            {
                "name": "Viscidus",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 566000,  # 9:26 (worse than base)
                "duration": 91000,
                "individual_segment_time": 91000,  # 9:26 - 7:55 = 1:31
                "idle_time": 12000
            },
            {
                "name": "Princess Huhuran",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 790000,  # 13:10 (worse than base)
                "duration": 224000,
                "individual_segment_time": 224000,  # 13:10 - 9:26 = 3:44
                "idle_time": 28000
            },
            {
                "name": "Twin Emperors",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1063000,  # 17:43 (worse than base)
                "duration": 273000,
                "individual_segment_time": 273000,  # 17:43 - 13:10 = 4:33
                "idle_time": 35000
            },
            {
                "name": "Ouro",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1550000,  # 25:50 (worse than base)
                "duration": 487000,
                "individual_segment_time": 487000,  # 25:50 - 17:43 = 8:07
                "idle_time": 60000
            },
            {
                "name": "C'Thun",
                "is_boss": True,
                "is_kill": True,
                "start_time_rel": 0,
                "end_time_rel": 1704000,  # 28:24 (worse than base)
                "duration": 154000,
                "individual_segment_time": 154000,  # 28:24 - 25:50 = 2:34
                "idle_time": 18000
            }
        ],
        "timeline_data": []
    }
    
    return {
        "results": [base_run, run2, run3]
    }

def save_mock_data():
    """Save mock data to a JSON file for testing."""
    mock_data = create_mock_data()
    
    with open('mock_data.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print("Mock data saved to mock_data.json")
    print("\nExpected Best Segments calculation:")
    print("- The Prophet Skeram: 0:39 (from run 2)")
    print("- Silithid Royalty: 2:27 (from run 2) -> cumulative: 3:06")
    print("- Battleguard Sartura: 1:44 (from base run) -> cumulative: 4:50")
    print("- Fankriss the Unyielding: 1:45 (from run 2) -> cumulative: 6:35")
    print("- Viscidus: 1:11 (from base run) -> cumulative: 7:46")
    print("- Princess Huhuran: 3:18 (from run 2) -> cumulative: 11:04")
    print("- Twin Emperors: 3:03 (from run 2) -> cumulative: 14:07")
    print("- Ouro: 7:11 (from base run) -> cumulative: 21:18")
    print("- C'Thun: 2:08 (from base run) -> cumulative: 23:26")
    print("\nTheoretical best total time: 23:26")

if __name__ == "__main__":
    save_mock_data()
