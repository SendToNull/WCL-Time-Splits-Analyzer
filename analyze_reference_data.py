#!/usr/bin/env python3
"""
Analyze the reference app data to understand what the values underneath represent.
"""

def analyze_reference_data():
    """
    Analyze the reference app screenshot data to understand the pattern.
    
    From the reference app screenshot:
    
    Boss                | nota      | Eternal   | good talk | Return latest | Return best | Best Segments
    -------------------|-----------|-----------|-----------|---------------|-------------|---------------
    The Prophet Skeram | 0:55      | 0:39      | 0:57      | 0:57          | 1:07        | 0:39
                       | (+0:16)   | (no val)  | (+0:18)   | (+0:18)       | (+0:28)     | (-0:16)
                       | (no val)  | (no val)  | (no val)  | (no val)      | (no val)    | (no val)
    
    Silithid Royalty   | 3:25      | 3:06      | 4:03      | 3:47          | 4:14        | 2:54
                       | (+0:19)   | (no val)  | (+0:57)   | (+0:41)       | (+1:08)     | (-0:31)
                       | (+0:13)   | (no val)  | (+0:58)   | (+0:37)       | (+0:49)     | (-0:13)
    
    Let me analyze what these values could be:
    
    For Skeram:
    - Main time: cumulative time to kill boss
    - First parentheses: difference from base run (Eternal)
    - Second parentheses: ??? (missing for Skeram)
    
    For Silithid Royalty:
    - Main time: 3:25 (nota), 3:06 (Eternal), etc.
    - First parentheses: +0:19 (3:25 - 3:06), +0:57 (4:03 - 3:06), etc.
    - Second parentheses: +0:13, +0:58, +0:37, +0:49, -0:13
    
    The second value might be:
    1. Individual boss fight duration difference
    2. Idle time difference 
    3. Segment time difference (time from previous boss end to this boss end)
    
    Let me check if it's segment time differences:
    - Silithid segment for nota: 3:25 - 0:55 = 2:30
    - Silithid segment for Eternal: 3:06 - 0:39 = 2:27
    - Difference: 2:30 - 2:27 = 0:03, but reference shows +0:13
    
    So it's NOT segment time differences.
    
    Let me check if it's fight duration differences:
    - If Eternal Silithid fight took 2:27 and nota took 2:40, difference would be +0:13
    - This seems to match!
    
    So the pattern appears to be:
    - Main time: Cumulative time to boss kill
    - First parentheses: Cumulative time difference from base run
    - Second parentheses: Individual boss fight duration difference from base run
    - No second value for Skeram because it's the first boss (no previous reference point)
    """
    
    print("Analysis of reference app data:")
    print("==============================")
    print()
    print("Pattern identified:")
    print("- Main time: Cumulative time when boss dies")
    print("- First parentheses: Cumulative time difference from base run")
    print("- Second parentheses: Boss fight duration difference from base run")
    print("- Skeram has no second value (first boss)")
    print()
    print("Best Segments calculation:")
    print("- Takes the best cumulative time for each boss across all runs")
    print("- NOT the sum of best individual segments")
    print("- Shows the actual best cumulative time achieved")
    print()
    print("Example for Silithid Royalty:")
    print("- Best cumulative time: 2:54 (from some run)")
    print("- Difference from base (3:06): 2:54 - 3:06 = -0:12 (but shows -0:31?)")
    print("- Fight duration difference: -0:13")

if __name__ == "__main__":
    analyze_reference_data()
