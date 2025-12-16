# Database Migrations

This folder contains database migration scripts used during development. These scripts are **not needed for normal operation** of the application.

## What are these?

These scripts were used to evolve the database schema during development. The final schema is defined in `database.py`, which automatically creates all necessary tables on first run.

## Do I need to run these?

**No.** If you're installing the application fresh, you don't need any of these files. The `database.py` file contains the complete, up-to-date schema.

## When were these used?

These migrations were run during development to:
- Add new features
- Rename columns
- Fix schema issues
- Clean up old fields
- Add new tables

## Can I delete these?

Yes, these files can be safely deleted if you're distributing the application. They're kept here for development history only.
