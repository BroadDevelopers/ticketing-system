-- Ticketing System Database Schema for Lakebase

-- Drop tables if they exist (for fresh setup)
DROP TABLE IF EXISTS ticket_messages CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;

-- Create tickets table
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    category VARCHAR(100) DEFAULT 'general',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_status CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    CONSTRAINT check_priority CHECK (priority IN ('low', 'medium', 'high'))
);

-- Create ticket_messages table
CREATE TABLE ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);

-- Insert sample data for testing
INSERT INTO tickets (title, description, status, priority, category, created_by) VALUES
    ('Login Issue', 'Users unable to login to the system', 'open', 'high', 'technical', 'john@example.com'),
    ('Feature Request: Dark Mode', 'Please add dark mode to the application', 'open', 'low', 'feature', 'jane@example.com'),
    ('Database Performance', 'Queries are running slowly', 'in_progress', 'high', 'technical', 'admin@example.com');

-- Add initial messages to the first ticket
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (1, 'This issue started after the latest deployment', 'john@example.com'),
    (1, 'We are investigating the authentication service', 'support@example.com');

-- Verify the setup
SELECT 'Schema created successfully!' as status;
SELECT COUNT(*) as ticket_count FROM tickets;
SELECT COUNT(*) as message_count FROM ticket_messages;