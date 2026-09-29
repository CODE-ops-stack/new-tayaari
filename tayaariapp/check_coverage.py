import os

os.chdir('C:/Users/harsh/Downloads/tayaari/tayaariapp/source-material')

files = [
    'ncert_xi_india_env.txt',
    'ncert_xii_human_geo.txt',
    'ncert_xii_india_economy.txt',
    'ncert_xi_physical_geo.txt',
    'ncert_x_geo.txt',
    'geography_extracted.txt',
    'geography_extracted_2.txt',
    'question_extracted.txt'
]

print("Files found:")
for fname in [
    'ncert_xi_india_env.txt',
    'ncert_xii_human_geo.txt',
    'ncert_xii_india_economy.txt',
    'ncert_xi_physical_geo.txt',
    'ncert_x_geo.txt',
    'geography_extracted.txt',
    'geography_extracted_2.txt',
    'question_extracted.txt'
]:
    if os.path.exists(fname):
        size = os.path.getsize(fname)
        print(f'{fname}: {size} bytes')
    else:
        print(f'{fname}: NOT FOUND')
"