import ast
import os
import glob

def audit_file(filepath):
    print(f"\n--- Auditing AST for {filepath} ---")
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)

    facades = []
    hardcoded_returns = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for dummy implementations (e.g. only `pass` or `return <literal>`)
            statements = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))] # filter docstrings
            if len(statements) == 1:
                stmt = statements[0]
                if isinstance(stmt, ast.Pass):
                    facades.append((node.name, node.lineno, "Pass-only function"))
                elif isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                    # Exclude boolean or None properties if normal
                    facades.append((node.name, node.lineno, f"Returns constant: {stmt.value.value}"))
                elif isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call):
                    if hasattr(stmt.exc.func, "id") and stmt.exc.func.id == "NotImplementedError":
                        facades.append((node.name, node.lineno, "NotImplementedError stub"))

    print(f"Total functions audited: {len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])}")
    if facades:
        print(f"Flagged potential facades ({len(facades)}):")
        for fn, lineno, reason in facades:
            print(f"  Line {lineno}: {fn}() -> {reason}")
    else:
        print("No dummy facades detected.")

for p in ["v13_discovery/normalizer.py", "v13_discovery/semantic_extractor.py", "tests/test_v13_semantic_extractor.py"]:
    audit_file(p)
