import pandas as pd

df = pd.read_excel('test_with_bad_link_output.xlsx')

print('Columns:', df.columns.tolist())
print('\nResults with Comments column:')
print('='*100)
for idx, row in df.iterrows():
    name = row['Name'] if pd.notna(row['Name']) else 'N/A'
    long_val = f"{row['LONG']:.4f}" if pd.notna(row['LONG']) else 'N/A'
    lat_val = f"{row['LATTs']:.4f}" if pd.notna(row['LATTs']) else 'N/A'
    comment = row['Comments'] if pd.notna(row['Comments']) else 'N/A'
    print(f"Row {idx+1}: {name:20s} | LONG={long_val:10s} | LATTs={lat_val:10s} | {comment}")
print('='*100)
