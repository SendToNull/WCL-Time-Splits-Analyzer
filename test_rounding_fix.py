#!/usr/bin/env python3
"""
Test script to verify the rounding fix works correctly.
"""

import math

def format_timestamp_gas(ms, include_hours=True):
    """Google Apps Script exact logic."""
    if not isinstance(ms, (int, float)):
        return "---"

    sign = "-" if ms < 0 else ""
    delta = abs(ms) / 1000
    
    days = math.floor(delta / 86400)
    delta -= days * 86400
    hours = math.floor(delta / 3600) % 24
    delta -= hours * 3600
    minutes = math.floor(delta / 60) % 60
    delta -= minutes * 60
    seconds = math.floor(delta % 60)

    seconds_string = f"{seconds:02d}"
    minutes_string = f"{minutes:02d}"

    if include_hours:
        return f"{sign}{hours}:{minutes_string}:{seconds_string}"
    else:
        return f"{sign}{minutes_string}:{seconds_string}"

def format_delta(delta_ms):
    """Format delta time with proper sign."""
    if delta_ms is None:
        return ""
    
    formatted = format_timestamp_gas(abs(delta_ms), False)
    if delta_ms > 0:
        return f"+{formatted}"
    elif delta_ms < 0:
        return f"-{formatted}"
    else:
        return formatted

def test_old_method(base_time, comp_time):
    """Test the old (incorrect) rounding method."""
    base_rounded = round(base_time / 1000) * 1000
    comp_rounded = round(comp_time / 1000) * 1000
    delta = base_rounded - comp_rounded
    return delta

def test_new_method(base_time, comp_time):
    """Test the new (correct) rounding method."""
    raw_delta = base_time - comp_time
    delta = round(raw_delta / 1000) * 1000
    return delta

print("=== Testing Rounding Fix ===")
print("Testing the Princess Huhuran scenario and other edge cases")
print()

test_cases = [
    (750000, 730000, "Exact 20 second difference"),
    (750500, 730600, "Princess Huhuran case - should show +00:20"),
    (750400, 730500, "Another millisecond case"),
    (750499, 730500, "Edge case - 19.999s"),
    (750500, 730501, "Another edge case - 19.999s"),
    (750001, 730001, "Minimal millisecond difference"),
    (750999, 730001, "Large millisecond difference"),
]

for base_time, comp_time, description in test_cases:
    old_delta = test_old_method(base_time, comp_time)
    new_delta = test_new_method(base_time, comp_time)
    
    print(f"{description}:")
    print(f"  Base time: {base_time} ms ({format_timestamp_gas(base_time, True)})")
    print(f"  Comp time: {comp_time} ms ({format_timestamp_gas(comp_time, True)})")
    print(f"  Raw delta: {base_time - comp_time} ms")
    print(f"  Old method: {old_delta} ms -> {format_delta(old_delta)}")
    print(f"  New method: {new_delta} ms -> {format_delta(new_delta)}")
    
    if old_delta != new_delta:
        print(f"  *** FIXED: Changed from {format_delta(old_delta)} to {format_delta(new_delta)} ***")
    else:
        print(f"  No change needed")
    print()

print("=== Summary ===")
print("The fix changes the rounding logic from:")
print("1. OLD: Round each time individually, then calculate delta")
print("2. NEW: Calculate raw delta first, then round the delta")
print()
print("This ensures that small millisecond differences don't get")
print("compounded by the rounding process, giving more accurate results.")
