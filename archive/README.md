# Archive Directory

This directory contains archived files that were previously scattered throughout the codebase. Files have been organized here for reference but are not part of the active production system.

## Directory Structure

### backend-backups/
Contains backup copies of the main backend files from various development iterations:
- `main_enhanced_backup_*.py` - Timestamped backups of main_enhanced.py
- `main_inmemory_backup_*.py` - Backups from when in-memory storage was used

### test-archives/
Historical test results and reports that are no longer actively referenced:
- Test reports from previous development phases
- Migration verification reports
- UAT test results

### old-scripts/
Utility scripts that may have been used during development but are not part of regular operations.

### pdf-samples/
Sample PDF files and test documents used during development:
- Direct deposit form variations
- Employee hire packets
- Form field visualization tests

## Important Notes

1. **DO NOT DELETE** - These files may contain useful reference information
2. **DO NOT IMPORT** - Do not import or reference these files in production code
3. **FOR REFERENCE ONLY** - Use these files only for historical context or debugging

## Restoration

If any file needs to be restored to active use:
1. Copy (don't move) the file from archive to its proper location
2. Update imports and references as needed
3. Test thoroughly before committing

Last Updated: 2024-01-26