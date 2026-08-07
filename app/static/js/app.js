// ============================================================
// API Calls
// ============================================================

async function fetchTickets(status = 'all') {
    const response = await fetch(`/api/tickets?status=${status}`);
    if (!response.ok) throw new Error('Failed to fetch tickets');
    return await response.json();
}

async function fetchTicketDetail(ticketId) {
    const response = await fetch(`/api/tickets/${ticketId}`);
    if (!response.ok) throw new Error('Failed to fetch ticket details');
    return await response.json();
}

async function createTicket(data) {
    const response = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to create ticket');
    return result;
}

async function addMessage(ticketId, data) {
    const response = await fetch(`/api/tickets/${ticketId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to add message');
    return result;
}

async function updateStatus(ticketId, status) {
    const response = await fetch(`/api/tickets/${ticketId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to update status');
    return result;
}

async function deleteTicketApi(ticketId) {
    const response = await fetch(`/api/tickets/${ticketId}`, {
        method: 'DELETE'
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Failed to delete ticket');
    return result;
}

// ============================================================
// UI Functions
// ============================================================

let currentTicketId = null;

function viewTicket(ticketId) {
    currentTicketId = ticketId;
    document.getElementById('ticket-list').style.display = 'none';
    document.getElementById('ticket-detail').style.display = 'block';
    loadTicketDetail(ticketId);
}

function closeDetail() {
    document.getElementById('ticket-detail').style.display = 'none';
    document.getElementById('ticket-list').style.display = 'block';
    location.reload();
}

async function loadTicketDetail(ticketId) {
    const detail = await fetchTicketDetail(ticketId);
    const ticket = detail.ticket;
    const messages = detail.messages;
    
    const container = document.getElementById('detail-content');
    
    let html = `
        <h2>${ticket.title}</h2>
        <div class="ticket-meta">
            <span><strong>Status:</strong> <span class="status-badge status-${ticket.status}">${ticket.status}</span></span>
            <span><strong>Priority:</strong> ${ticket.priority}</span>
            <span><strong>Category:</strong> ${ticket.category}</span>
            <span><strong>Created by:</strong> ${ticket.created_by}</span>
            <span><strong>Created:</strong> ${new Date(ticket.created_at).toLocaleString()}</span>
        </div>
        ${ticket.description ? `<p style="margin-bottom:12px;">${ticket.description}</p>` : ''}
        
        <div class="status-update">
            <label for="status-select"><strong>Update Status:</strong></label>
            <select id="status-select">
                <option value="open" ${ticket.status === 'open' ? 'selected' : ''}>Open</option>
                <option value="in_progress" ${ticket.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                <option value="resolved" ${ticket.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                <option value="closed" ${ticket.status === 'closed' ? 'selected' : ''}>Closed</option>
            </select>
            <button onclick="handleStatusUpdate(${ticket.ticket_id})" class="btn btn-secondary">Update</button>
        </div>
        
        <h4 style="margin:16px 0 8px;">Messages (${messages.length})</h4>
        <div id="messages-container">
            ${messages.map(m => `
                <div class="message">
                    <strong>${m.author}</strong>
                    <span class="meta">${new Date(m.created_at).toLocaleString()}</span>
                    <p>${m.message_text}</p>
                </div>
            `).join('')}
        </div>
        
        <div style="margin-top:16px;">
            <h4>Add Message</h4>
            <textarea id="new-message" placeholder="Type your message..." rows="3"></textarea>
            <input type="text" id="message-author" placeholder="Your name" style="margin-top:8px; padding:8px 14px; border:1px solid #d1d5db; border-radius:8px; width:100%;">
            <button onclick="handleAddMessage(${ticket.ticket_id})" class="btn btn-primary" style="margin-top:8px;">Send Message</button>
        </div>
    `;
    container.innerHTML = html;
}

async function handleAddMessage(ticketId) {
    const messageText = document.getElementById('new-message').value.trim();
    const author = document.getElementById('message-author').value.trim() || 'Anonymous';
    
    if (!messageText) {
        alert('Message cannot be empty');
        return;
    }
    
    try {
        await addMessage(ticketId, { message_text: messageText, author });
        document.getElementById('new-message').value = '';
        await loadTicketDetail(ticketId);
    } catch (error) {
        alert(error.message);
    }
}

async function handleStatusUpdate(ticketId) {
    const status = document.getElementById('status-select').value;
    try {
        await updateStatus(ticketId, status);
        await loadTicketDetail(ticketId);
    } catch (error) {
        alert(error.message);
    }
}

// ============================================================
// Create Ticket
// ============================================================

function showCreateTicket() {
    document.getElementById('create-modal').style.display = 'flex';
}

function closeCreateTicket() {
    document.getElementById('create-modal').style.display = 'none';
}

async function handleCreateTicket(event) {
    event.preventDefault();
    
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    const createdBy = document.getElementById('created_by').value.trim() || 'Anonymous';
    const priority = document.getElementById('priority').value;
    const category = document.getElementById('category').value;
    
    // Validation
    const titleError = document.getElementById('title-error');
    if (title.length < 3) {
        titleError.textContent = 'Title must be at least 3 characters';
        return;
    }
    titleError.textContent = '';
    
    try {
        await createTicket({ title, description, created_by: createdBy, priority, category });
        closeCreateTicket();
        location.reload();
    } catch (error) {
        alert(error.message);
    }
}

// ============================================================
// Delete Ticket
// ============================================================

let deleteTargetId = null;

function deleteTicket() {
    if (!currentTicketId) return;
    deleteTargetId = currentTicketId;
    document.getElementById('delete-modal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('delete-modal').style.display = 'none';
    deleteTargetId = null;
}

async function confirmDelete() {
    if (!deleteTargetId) return;
    try {
        await deleteTicketApi(deleteTargetId);
        closeDeleteModal();
        location.reload();
    } catch (error) {
        alert(error.message);
        closeDeleteModal();
    }
}

// ============================================================
// Filter
// ============================================================

function applyFilter() {
    const status = document.getElementById('status-filter').value;
    fetchTickets(status).then(tickets => {
        const container = document.getElementById('tickets-container');
        container.innerHTML = tickets.map(t => `
            <div class="ticket-card priority-${t.priority}" onclick="viewTicket(${t.ticket_id})">
                <div class="ticket-header">
                    <h3>${t.title}</h3>
                    <span class="status-badge status-${t.status}">${t.status}</span>
                </div>
                <div class="ticket-meta">
                    <span>Priority: <strong>${t.priority}</strong></span>
                    <span>Category: ${t.category}</span>
                    <span>Created by: ${t.created_by}</span>
                    <span>${new Date(t.created_at).toLocaleString()}</span>
                </div>
                <div class="ticket-description">${(t.description || 'No description').substring(0, 100)}${(t.description || '').length > 100 ? '...' : ''}</div>
            </div>
        `).join('');
    }).catch(error => {
        alert('Failed to load tickets: ' + error.message);
    });
}

// ============================================================
// Close modals on outside click
// ============================================================

document.getElementById('create-modal').addEventListener('click', function(e) {
    if (e.target === this) closeCreateTicket();
});

document.getElementById('delete-modal').addEventListener('click', function(e) {
    if (e.target === this) closeDeleteModal();
});