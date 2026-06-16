import os
import re
import time
import argparse

def analyze_file(filepath):
    errors = []
    warnings = []
    infos = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except (UnicodeDecodeError, OSError):
        return errors, warnings, infos

    # Line by line checks
    for i, line in enumerate(lines):
        line_num = i + 1

        # HTML/CSS/JS Checks
        if filepath.endswith(('.html', '.js', '.css')):
            if 'var ' in line and '.js' in filepath:
                 warnings.append({"line": line_num, "type": "Style", "message": "Use let/const instead of var."})
            if 'document.write' in line:
                 warnings.append({"line": line_num, "type": "Vulnerability", "message": "document.write found (potential XSS)"})
            if 'eval(' in line:
                 warnings.append({"line": line_num, "type": "Vulnerability", "message": "eval() found (potential security issue)"})
            if 'console.log' in line:
                 infos.append({"line": line_num, "type": "Style", "message": "console.log found."})

            # Check for memory guideline: no blue/cyan themes
            if re.search(r'#(00FFFF|0000FF|00FFFF|00BFFF|1E90FF|87CEEB|87CEFA|4682B4|ADD8E6)', line, re.IGNORECASE) or \
               re.search(r'rgba?\(\s*0\s*,\s*0\s*,\s*255', line, re.IGNORECASE) or \
               'cyan' in line.lower() or 'blue' in line.lower():
                 warnings.append({"line": line_num, "type": "Style", "message": "Potential use of blue/cyan theme found which is rejected by branding."})

    # Full file content checks
    if filepath.endswith('.html'):
        if '<script>' in content and '</script>' not in content:
            errors.append({"line": 0, "type": "Syntax", "message": "Unclosed <script> tag"})

    return errors, warnings, infos

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Code Analyzer")
    parser.add_argument("--dir", type=str, default=".", help="Directory to scan")
    parser.add_argument("--output", type=str, default="analysis_report.md", help="Output report file")
    args = parser.parse_args()

    total_files = 0
    scanned_files = 0
    all_errors = []
    start_time = time.time()

    # Collect files to scan
    files_to_scan = []
    for root, dirs, files in os.walk(args.dir):
        # Skip node_modules and .git
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            if file.endswith(('.html', '.js', '.css', '.py')):
                files_to_scan.append(os.path.join(root, file))

    total_files = len(files_to_scan)

    print(f"Starting analysis of {total_files} files in directory: {args.dir}...")

    for filepath in files_to_scan:
        print(f"Analyzing {filepath}... ({scanned_files + 1}/{total_files}) - {(scanned_files + 1) / total_files * 100:.1f}%")

        errors, warnings, infos = analyze_file(filepath)
        for e in errors:
            all_errors.append({"severity": "critical", "path": filepath, "line": e.get("line", 0), "message": e["message"]})
        for w in warnings:
            all_errors.append({"severity": "warning", "path": filepath, "line": w.get("line", 0), "message": w["message"]})
        for i in infos:
            all_errors.append({"severity": "info", "path": filepath, "line": i.get("line", 0), "message": i["message"]})

        scanned_files += 1

        # Estimate time remaining (simplistic)
        elapsed_time = time.time() - start_time
        if scanned_files > 0:
            avg_time_per_file = elapsed_time / scanned_files
            remaining_files = total_files - scanned_files
            etc = avg_time_per_file * remaining_files
            print(f"  ETC: {etc:.2f} seconds")

    print("\n--- Generating Final Report ---")

    criticals = [e for e in all_errors if e['severity'] == 'critical']
    warnings = [e for e in all_errors if e['severity'] == 'warning']
    infos = [e for e in all_errors if e['severity'] == 'info']

    with open(args.output, "w") as f:
        f.write(f"# Code Analysis Report\n\n")
        f.write(f"**Directory Scanned**: `{args.dir}` (recursive)\n")
        f.write(f"**Total Files Scanned**: {total_files}\n\n")

        f.write(f"## Summary\n\n")
        f.write(f"**Total Issues Found**: {len(all_errors)}\n")
        f.write(f"- **Critical**: {len(criticals)}\n")
        f.write(f"- **Warning**: {len(warnings)}\n")
        f.write(f"- **Info**: {len(infos)}\n\n")

        f.write(f"## Details\n\n")
        if len(all_errors) > 0:
            f.write(f"| Severity | File | Line | Message |\n")
            f.write(f"| -------- | ---- | ---- | ------- |\n")
            for err in all_errors:
                f.write(f"| {err['severity'].capitalize()} | `{err['path']}` | {err['line']} | {err['message']} |\n")
        else:
            f.write("No issues found.\n")

        f.write(f"\n## Suggested Fixes / Recommendations\n\n")
        if len(warnings) > 0:
            f.write("- Address style warnings (like blue/cyan colors) to align with branding guidelines.\n")
            f.write("- Replace any deprecated or insecure functions (like document.write or eval) if found.\n")
        if len(infos) > 0:
            f.write("- Review console.logs before production deployment.\n")
        f.write("- Consider using a dedicated linter (e.g., ESLint for JS, HTMLHint for HTML) for more robust analysis.\n")

    print(f"Analysis complete. Report saved to {args.output}")

if __name__ == "__main__":
    main()
