
PC Games Releases Site - V6 Stable

FINAL Production-Ready Version

Core Improvements:
- Strict case-sensitive DAT ↔ 1fichier matching
- MIA releases skipped
- Duplicate-safe batch processing
- Bulk INSERT and UPDATE in single transaction
- Updates only download link for existing releases
- Optimized for 100k+ entries
- Safe to delete database.db anytime (init_db recreates schema)

Setup:
1. python -m venv venv
2. venv\Scripts\activate
3. pip install flask lxml requests
4. python app.py

Admin:
- Provide 1fichier directory links
- Upload ZIP or single DAT
- Process

This version is stable and ready for further development.
