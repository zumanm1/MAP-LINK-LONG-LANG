#!/usr/bin/env python3
"""
Crash and Stability Bug Tests
Focus on inputs that might cause crashes or hangs
"""

from map_converter import extract_coordinates_from_url
import sys

def test_crash_scenarios():
    """Test inputs that might crash the program"""

    print("\n💥 Testing Crash Scenarios\n")
    print("=" * 80)

    test_cases = [
        # Extreme inputs
        ("", "Empty string"),
        (None, "None value"),
        (123, "Integer"),
        (12.34, "Float"),
        ([], "Empty list"),
        ({}, "Empty dict"),
        (True, "Boolean True"),
        (False, "Boolean False"),

        # Very long strings
        ("a" * 10000, "10K char string"),
        ("https://www.google.com/maps/@" + "1" * 1000 + "," + "2" * 1000, "Very long URL"),

        # Special strings
        ("\x00\x00\x00", "Null bytes"),
        ("🗺️📍🌍", "Only emojis"),
        ("https://www.google.com/maps/@🗺️,📍", "Emojis in URL"),

        # Malformed decimals
        ("https://www.google.com/maps/@-26.,28.", "Incomplete decimals"),
        ("https://www.google.com/maps/@.108,.052", "Leading decimals only"),
        ("https://www.google.com/maps/@-26.108.204,28.052.706", "Multiple decimals"),

        # Scientific notation
        ("https://www.google.com/maps/@-2.6e1,2.8e1", "Scientific notation"),
        ("https://www.google.com/maps/@-26.108204e10,28.0527061e10", "Scientific with exponents"),

        # Extreme coordinate values
        ("https://www.google.com/maps/@-999999.999999,999999.999999", "Extreme values"),
        ("https://www.google.com/maps/@1e100,1e100", "1e100 values"),

        # Unicode and special chars
        ("https://www.google.com/maps/@-26·108204,28·0527061", "Middle dot instead of period"),
        ("https://www.google.com/maps/@−26.108204,28.0527061", "Minus sign (Unicode) instead of hyphen"),
        ("https://www.google.com/maps/@-26․108204,28․0527061", "One dot leader (Unicode)"),
    ]

    crashes = []
    passed = 0
    failed = 0

    for test_input, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  Input type: {type(test_input)}")
        if isinstance(test_input, str) and len(test_input) > 100:
            print(f"  Input (truncated): {repr(test_input[:100])}...")
        else:
            print(f"  Input: {repr(test_input)}")

        try:
            lng, lat = extract_coordinates_from_url(test_input)
            print(f"  Result: lng={lng}, lat={lat}")
            print(f"  ✅ PASS - No crash")
            passed += 1
        except Exception as e:
            print(f"  ❌ CRASH: {type(e).__name__}: {str(e)}")
            crashes.append(f"CRASH BUG: {description} - {type(e).__name__}: {str(e)}")
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"\n📊 Results: {passed} survived, {failed} crashed")

    return crashes


def test_regex_catastrophic_backtracking():
    """Test for catastrophic backtracking in regex patterns"""

    print("\n\n⚡ Testing Regex Catastrophic Backtracking\n")
    print("=" * 80)

    test_cases = [
        # Patterns that might cause catastrophic backtracking
        ("https://www.google.com/maps/@" + "1,2," * 100, "Many comma pairs"),
        ("https://www.google.com/maps/@" + "." * 1000 + "," + "." * 1000, "Many dots"),
        ("https://www.google.com/maps/@-26" + ".1" * 100 + ",28" + ".5" * 100, "Many decimal pairs"),
        ("https://www.google.com/maps/@" + "123.456," * 50, "Repeated coordinate patterns"),
    ]

    bugs_found = []

    print(f"\nNote: Testing for slow regex patterns (timeout = 5 seconds)...\n")

    for url, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL length: {len(url)}")

        try:
            import time
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Regex took too long")

            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 second timeout

            start_time = time.time()
            lng, lat = extract_coordinates_from_url(url)
            elapsed = time.time() - start_time

            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)

            print(f"  Result: lng={lng}, lat={lat}")
            print(f"  Time: {elapsed:.3f}s")

            if elapsed > 1.0:
                print(f"  ⚠️  WARNING - Slow processing")
                bugs_found.append(f"PERFORMANCE BUG: Slow regex for '{description}' ({elapsed:.3f}s)")
            else:
                print(f"  ✅ PASS - Fast processing")

        except TimeoutError:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            print(f"  ❌ TIMEOUT - Took longer than 5 seconds")
            bugs_found.append(f"CRITICAL BUG: Regex timeout for '{description}'")
        except Exception as e:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            print(f"  ❌ ERROR: {str(e)}")
            bugs_found.append(f"BUG: Exception in '{description}': {str(e)}")

    print(f"\n{'=' * 80}")

    # Note: Performance bugs are excluded per requirements
    return [b for b in bugs_found if "PERFORMANCE BUG" not in b]


def test_memory_issues():
    """Test for potential memory issues"""

    print("\n\n💾 Testing Memory Issues\n")
    print("=" * 80)

    # Test with many URLs to see if there's memory accumulation
    test_url = "https://www.google.com/maps/@-26.108204,28.0527061,17z"

    print(f"\nProcessing same URL 1000 times to check for memory leaks...")

    bugs_found = []

    try:
        import time
        start_time = time.time()

        for i in range(1000):
            lng, lat = extract_coordinates_from_url(test_url)
            if i % 100 == 0:
                print(f"  Processed {i} iterations...")

        elapsed = time.time() - start_time

        print(f"\n  Total time: {elapsed:.2f}s")
        print(f"  Average per call: {elapsed/1000*1000:.3f}ms")

        if elapsed/1000 > 0.1:  # More than 100ms per call average
            print(f"  ⚠️  WARNING - Slow average processing time")

        print(f"  ✅ PASS - Completed without crash")

    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        bugs_found.append(f"MEMORY BUG: Failed during repeated processing: {str(e)}")

    print(f"\n{'=' * 80}")

    return bugs_found


if __name__ == "__main__":
    print("\n" + "💥 " * 30)
    print("\n  CRASH AND STABILITY TEST SUITE")
    print("\n" + "💥 " * 30)

    all_bugs = []

    # Run all tests
    all_bugs.extend(test_crash_scenarios())
    all_bugs.extend(test_regex_catastrophic_backtracking())
    all_bugs.extend(test_memory_issues())

    # Print summary
    print("\n\n" + "=" * 80)
    print("\n📋 CRASH AND STABILITY BUGS FOUND\n")
    print("=" * 80)

    if all_bugs:
        print(f"\n🚨 Found {len(all_bugs)} bugs:\n")
        for i, bug in enumerate(all_bugs, 1):
            print(f"{i}. {bug}")
        exit(1)
    else:
        print("\n✅ No crash or stability bugs detected!")
        exit(0)
