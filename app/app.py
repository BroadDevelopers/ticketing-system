"""
Support App - Flask Backend with Lakebase (Enhanced with Bonuses)
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import lakebase

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("support-app")

app = Flask(__name__)

# ===== HELPER FUNCTIONS =====

def get_all_tickets(status_filter=None):
    """Fetch all tickets, optionally filtered by status."""
    if status_filter and status_filter != 'all':
        return lakebase.run_query("""
            SELECT ticket_id, title, description, status, priority, category, created_by, created_at, updated_at
            FROM tickets
            WHERE status = %s
            ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                END,
                created_at DESC
        """, (status_filter,))
    else:
        return lakebase.run_query("""
            SELECT ticket_id, title, description, status, priority, category, created_by, created_at, updated_at
            FROM tickets
            ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                END,
                created_at DESC
        """)

def get_ticket_by_id(ticket_id):
    """Fetch a single ticket by ID."""
    result = lakebase.run_query("""
        SELECT ticket_id, title, description, status, priority, category, created_by, created_at, updated_at
        FROM tickets
        WHERE ticket_id = %s
    """, (ticket_id,))
    return result[0] if result else None

def get_ticket_messages(ticket_id):
    """Fetch all messages for a specific ticket."""
    return lakebase.run_query("""
        SELECT message_id, ticket_id, message_text, author, created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC
    """, (ticket_id,))

def create_ticket(title, description, created_by, priority='medium', category='general'):
    """Create a new ticket in Lakebase."""
    result = lakebase.run_write("""
        INSERT INTO tickets (title, description, created_by, priority, category, status)
        VALUES (%s, %s, %s, %s, %s, 'open')
        RETURNING ticket_id
    """, (title, description, created_by, priority, category))
    return result[0][0] if result else None

def add_message(ticket_id, message_text, author):
    """Add a message to an existing ticket."""
    lakebase.run_write("""
        INSERT INTO ticket_messages (ticket_id, message_text, author)
        VALUES (%s, %s, %s)
    """, (ticket_id, message_text, author))
    # Update the ticket's updated_at timestamp
    lakebase.run_write("""
        UPDATE tickets SET updated_at = now() WHERE ticket_id = %s
    """, (ticket_id,))

def update_ticket_status(ticket_id, new_status):
    """Update the status of a ticket."""
    lakebase.run_write("""
        UPDATE tickets
        SET status = %s, updated_at = now()
        WHERE ticket_id = %s
    """, (new_status, ticket_id))

def delete_ticket(ticket_id):
    """Delete a ticket and its messages (cascade)."""
    lakebase.run_write("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))

def get_ticket_stats():
    """Get ticket statistics."""
    stats = lakebase.run_query("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'open' THEN 1 END) as open,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
            COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
            COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed,
            COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority,
            COUNT(CASE WHEN priority = 'medium' THEN 1 END) as medium_priority,
            COUNT(CASE WHEN priority = 'low' THEN 1 END) as low_priority
        FROM tickets
    """)
    return stats[0] if stats else {}

# ===== ROUTES =====

@app.route('/')
def index():
    """Main page - displays all tickets."""
    tickets = get_all_tickets()
    stats = get_ticket_stats()
    return render_template('index.html', tickets=tickets, stats=stats)

@app.route('/api/tickets')
def api_tickets():
    """API endpoint to get all tickets with optional status filter."""
    status_filter = request.args.get('status', 'all')
    tickets = get_all_tickets(status_filter)
    return jsonify(tickets)

@app.route('/api/tickets/<int:ticket_id>')
def api_ticket_detail(ticket_id):
    """API endpoint to get a single ticket with its messages."""
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    messages = get_ticket_messages(ticket_id)
    return jsonify({'ticket': ticket, 'messages': messages})

@app.route('/api/tickets', methods=['POST'])
def api_create_ticket():
    """API endpoint to create a new ticket."""
    data = request.json
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    created_by = data.get('created_by', 'Anonymous').strip()
    priority = data.get('priority', 'medium')
    category = data.get('category', 'general')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    if len(title) < 3:
        return jsonify({'error': 'Title must be at least 3 characters'}), 400
    
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'error': 'Invalid priority'}), 400
    
    ticket_id = create_ticket(title, description, created_by, priority, category)
    
    if ticket_id:
        return jsonify({'ticket_id': ticket_id, 'message': 'Ticket created successfully'})
    else:
        return jsonify({'error': 'Failed to create ticket'}), 500

@app.route('/api/tickets/<int:ticket_id>/messages', methods=['POST'])
def api_add_message(ticket_id):
    """API endpoint to add a message to a ticket."""
    data = request.json
    message_text = data.get('message_text', '').strip()
    author = data.get('author', 'Anonymous').strip()
    
    if not message_text:
        return jsonify({'error': 'Message text is required'}), 400
    
    if len(message_text) < 1:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Verify ticket exists
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    add_message(ticket_id, message_text, author)
    return jsonify({'message': 'Message added successfully'})

@app.route('/api/tickets/<int:ticket_id>/status', methods=['PUT'])
def api_update_status(ticket_id):
    """API endpoint to update ticket status."""
    data = request.json
    new_status = data.get('status')
    
    valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
    
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    update_ticket_status(ticket_id, new_status)
    return jsonify({'message': f'Status updated to {new_status}'})

@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def api_delete_ticket(ticket_id):
    """API endpoint to delete a ticket with confirmation."""
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    delete_ticket(ticket_id)
    return jsonify({'message': 'Ticket deleted successfully'})

@app.route('/api/stats')
def api_stats():
    """API endpoint to get ticket statistics."""
    return jsonify(get_ticket_stats())

@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    app.run(debug=True, host=host, port=port)