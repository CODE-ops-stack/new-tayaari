import os
import glob
import json

def scan_all_files(root_dir):
    records = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip .git, .gradle, build, node_modules, app/build
        if any(skip in dirpath for skip in [".git", ".gradle", "build", "node_modules", "intermediates"]):
            continue
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root_dir)
            size = os.path.getsize(full_path)
            ext = os.path.splitext(f)[1].lower()
            records.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "name": f,
                "size_bytes": size,
                "ext": ext
            })
    return records

if __name__ == "__main__":
    tayaari_root = r"c:\Users\harsh\Downloads\tayaari"
    records = scan_all_files(tayaari_root)
    print(f"Total non-build files found in {tayaari_root}: {len(records)}")
    
    # Categorize by extension
    by_ext = {}
    for r in records:
        by_ext[r['ext']] = by_ext.get(r['ext'], 0) + 1
    print("\nFiles by extension:")
    for ext, count in sorted(by_ext.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {ext or '(no ext)'}: {count}")
        
    # Specifically list pdf, txt, md, json, db
    print("\nText & Data files:")
    for r in sorted(records, key=lambda x: x['size_bytes'], reverse=True):
        if r['ext'] in ['.pdf', '.txt', '.md', '.json', '.db', '']:
            print(f"  {r['size_bytes']:>10} bytes | {r['ext']:<6} | {r['rel_path']}")
