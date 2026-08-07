# Support App - Lakebase-Powered AI Support System

A full-featured support ticket system built with Flask and Lakebase.

## Features

✅ View all support tickets with priority and category
✅ Filter tickets by status
✅ View messages for a ticket
✅ Create new tickets with priority and category
✅ Add messages to existing tickets
✅ Update ticket status
✅ Delete tickets with confirmation
✅ Ticket statistics dashboard
✅ Input validation with error messages
✅ Modern responsive UI

## Local Development

1. Create `.env` from `.env.example`
2. Install dependencies: `pip install -r app/requirements.txt`
3. Run: `python app/app.py`
4. Open http://localhost:8000

## Deployment

1. Push to GitHub
2. Create Lakebase instance and run schema
3. Store Lakebase URL as secret in Databricks
4. Deploy as Databricks App

## Bonus Features Completed

- Ticket priority (low, medium, high)
- Ticket categories
- Filtering by ticket status
- Input validation and error messages
- Ticket statistics dashboard
- Delete functionality with confirmation
- Improved visual design