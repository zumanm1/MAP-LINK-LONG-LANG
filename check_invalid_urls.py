import pandas as pd

df = pd.read_excel('test_validation_output.xlsx')
invalid_urls = (df['Maps link'].notna() &
                (df['Maps link'].str.strip() != '') &
                ~(df['Maps link'].str.contains('maps.google|goo.gl', na=False)))

print('Invalid URLs that should have blank coordinates:')
for idx, row in df[invalid_urls].iterrows():
    has_coords = pd.notna(row['LONG']) or pd.notna(row['LATTs'])
    status = "❌ HAS COORDS (ERROR)" if has_coords else "✅ Blank (correct)"
    print(f'  {status} Row {idx+1}: {row["Maps link"][:60]}')
    print(f'           LONG={row["LONG"]}, LATTs={row["LATTs"]}')
