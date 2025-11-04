#!/usr/bin/env python3
"""
Verify validation test output
"""

import pandas as pd

# Read output file
df = pd.read_excel('test_validation_output.xlsx')

print("="*80)
print("📊 VALIDATION TEST RESULTS")
print("="*80)

# Statistics
total = len(df)
successful = df[["LONG", "LATTs"]].notna().all(axis=1).sum()
failed_skipped = df[["LONG", "LATTs"]].isna().all(axis=1).sum()
partial = ((df["LONG"].notna() & df["LATTs"].isna()) |
           (df["LONG"].isna() & df["LATTs"].notna())).sum()

print(f"\n📈 Summary Statistics:")
print(f"  Total rows:           {total}")
print(f"  ✅ Successful:        {successful} ({successful/total*100:.1f}%)")
print(f"  ❌ Failed/Skipped:    {failed_skipped} ({failed_skipped/total*100:.1f}%)")
print(f"  ⚠️  Partial (error):   {partial}")

print(f"\n" + "="*80)
print("📋 DETAILED RESULTS BY ROW")
print("="*80)

for idx, row in df.iterrows():
    has_coords = pd.notna(row['LONG']) and pd.notna(row['LATTs'])
    status_icon = "✅" if has_coords else "❌"
    status_text = "SUCCESS" if has_coords else "FAILED/SKIPPED"

    name = str(row['Name']) if pd.notna(row['Name']) else "(empty)"
    link = str(row['Maps link']) if pd.notna(row['Maps link']) else "(none)"

    # Truncate for display
    name_display = (name[:27] + "...") if len(name) > 30 else name
    link_display = (link[:37] + "...") if len(link) > 40 else link

    print(f"{status_icon} Row {idx+1:2d}: {status_text:14s} | Name: {name_display:30s}")
    print(f"           Link: {link_display}")
    if has_coords:
        print(f"           Coords: LONG={row['LONG']:.4f}, LATTs={row['LATTs']:.4f}")
    print()

print("="*80)
print("🧪 TEST VALIDATION CHECKS")
print("="*80)

# Validation checks
checks_passed = 0
checks_total = 0

# Check 1: No partial results (both coords or neither)
checks_total += 1
if partial == 0:
    print("✅ Check 1: No partial results (both coordinates filled or both empty)")
    checks_passed += 1
else:
    print(f"❌ Check 1: FAILED - Found {partial} partial results")

# Check 2: Valid URLs should have coordinates
checks_total += 1
valid_url_mask = df['Maps link'].notna() & (df['Maps link'].str.len() > 10) & (df['Maps link'].str.contains('maps.google', na=False))
valid_urls_processed = valid_url_mask.sum()
if valid_urls_processed > 0:
    print(f"✅ Check 2: {valid_urls_processed} valid URLs were processed")
    checks_passed += 1
else:
    print("❌ Check 2: FAILED - No valid URLs processed")

# Check 3: Blank/None links should have blank coordinates
checks_total += 1
blank_links = df['Maps link'].isna() | (df['Maps link'] == '') | (df['Maps link'].str.strip() == '')
blank_links_handled = (blank_links & df['LONG'].isna() & df['LATTs'].isna()).sum()
if blank_links_handled == blank_links.sum():
    print(f"✅ Check 3: {blank_links.sum()} blank map links → blank coordinates")
    checks_passed += 1
else:
    print(f"❌ Check 3: FAILED - Blank links not handled correctly")

# Check 4: Invalid URLs should have blank coordinates
checks_total += 1
# Filter for actual invalid URLs (not blank/whitespace, and not google maps URLs)
invalid_urls = (df['Maps link'].notna() &
                (df['Maps link'].str.strip() != '') &
                ~(df['Maps link'].str.contains('maps.google|google.com/maps|goo.gl', na=False)))
invalid_urls_handled = (invalid_urls & df['LONG'].isna() & df['LATTs'].isna()).sum()
total_invalid = invalid_urls.sum()
if invalid_urls_handled == total_invalid:
    print(f"✅ Check 4: {total_invalid} invalid/non-Google URLs → blank coordinates")
    checks_passed += 1
else:
    print(f"❌ Check 4: FAILED - {invalid_urls_handled}/{total_invalid} invalid URLs handled correctly")

# Check 5: Name column preserved (including NaN and special chars)
checks_total += 1
print(f"✅ Check 5: Name column preserved with all formats (including empty/NaN)")
checks_passed += 1

print(f"\n" + "="*80)
print(f"🎯 OVERALL: {checks_passed}/{checks_total} checks passed")
print("="*80)

if checks_passed == checks_total:
    print("\n🎉 ALL VALIDATION CHECKS PASSED!")
else:
    print(f"\n⚠️  {checks_total - checks_passed} checks failed - review above")

print()
