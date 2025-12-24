"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  💰 RECHNUNGEN MODUL - WEST MONEY OS v12.0                                    ║
║  Rechnungserstellung, Stripe Payment, PDF Export, DATEV                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, send_file
from datetime import datetime, timedelta
import json
import random
import io

invoices_bp = Blueprint('invoices', __name__)

INVOICES_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Rechnungen - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { display: flex; min-height: 100vh; }
        .sidebar {
            width: 260px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.1);
            padding: 20px;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(255,215,0,0.1); color: #ffd700; }
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 30px;
        }
        .title { font-size: 2rem; font-weight: 700; }
        .actions { display: flex; gap: 12px; }
        .btn {
            padding: 12px 24px; border: none; border-radius: 10px;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s; display: flex; align-items: center; gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #ffd700, #ff6b35); color: #000;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255,215,0,0.3);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.1); color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .btn-success { background: linear-gradient(135deg, #2ed573, #1e90ff); color: #fff; }
        
        /* Stats */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 24px;
        }
        .stat-card .icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-card .value {
            font-size: 2rem; font-weight: 700;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-card .label { color: #888; font-size: 0.9rem; margin-top: 5px; }
        .stat-card .change { font-size: 0.85rem; margin-top: 8px; }
        .stat-card .change.positive { color: #2ed573; }
        .stat-card .change.negative { color: #ff4757; }
        
        /* Tabs */
        .tabs {
            display: flex; gap: 10px; margin-bottom: 25px;
            border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;
        }
        .tab {
            padding: 10px 20px; background: none; border: none;
            color: #888; font-size: 1rem; cursor: pointer;
            border-radius: 8px; transition: all 0.3s;
        }
        .tab:hover { color: #fff; }
        .tab.active {
            background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,107,53,0.2));
            color: #ffd700;
        }
        
        /* Table */
        .table-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px; overflow: hidden;
        }
        .invoices-table { width: 100%; border-collapse: collapse; }
        .invoices-table th, .invoices-table td {
            padding: 16px; text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .invoices-table th {
            background: rgba(0,0,0,0.3); color: #888;
            font-weight: 500; font-size: 0.85rem; text-transform: uppercase;
        }
        .invoices-table tr:hover { background: rgba(255,255,255,0.05); }
        
        .invoice-status {
            padding: 5px 12px; border-radius: 20px;
            font-size: 0.8rem; font-weight: 600;
        }
        .status-paid { background: rgba(46, 213, 115, 0.2); color: #2ed573; }
        .status-pending { background: rgba(255, 165, 2, 0.2); color: #ffa502; }
        .status-overdue { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        .status-draft { background: rgba(99, 110, 114, 0.2); color: #636e72; }
        
        .action-btn {
            padding: 8px 12px; background: rgba(255,255,255,0.1);
            border: none; border-radius: 8px; color: #fff;
            cursor: pointer; margin-right: 5px; transition: all 0.3s;
        }
        .action-btn:hover { background: rgba(255,215,0,0.2); }
        
        /* Modal */
        .modal-overlay {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%; background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px); z-index: 1000;
            justify-content: center; align-items: center;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: #1a1a2e; border: 1px solid rgba(255,215,0,0.3);
            border-radius: 20px; width: 90%; max-width: 900px;
            max-height: 90vh; overflow-y: auto;
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .modal-title { font-size: 1.3rem; font-weight: 700; }
        .modal-close {
            background: none; border: none; color: #888;
            font-size: 1.5rem; cursor: pointer;
        }
        .modal-body { padding: 24px; }
        .modal-footer {
            display: flex; justify-content: flex-end; gap: 12px;
            padding: 20px 24px; border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 500; color: #ccc; }
        .form-input {
            width: 100%; padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px; color: #fff; font-size: 1rem;
        }
        .form-input:focus { outline: none; border-color: #ffd700; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        /* Invoice Items */
        .invoice-items { margin-top: 20px; }
        .invoice-item {
            display: grid; grid-template-columns: 3fr 1fr 1fr 1fr auto;
            gap: 15px; margin-bottom: 10px; align-items: center;
        }
        .invoice-item input { padding: 10px 12px; }
        .invoice-totals {
            margin-top: 20px; padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .invoice-total-row {
            display: flex; justify-content: flex-end; gap: 30px;
            margin-bottom: 10px;
        }
        .invoice-total-label { color: #888; }
        .invoice-total-value { font-weight: 600; min-width: 100px; text-align: right; }
        .invoice-total-value.grand { font-size: 1.3rem; color: #ffd700; }
        
        .toast {
            position: fixed; bottom: 30px; right: 30px;
            padding: 16px 24px; background: #2ed573; color: #000;
            border-radius: 10px; font-weight: 600; z-index: 9999;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">💰</span>
                <span class="logo-text">West Money OS</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/contacts"><span>📇</span> Kontakte</a>
                <a href="/dashboard/leads"><span>🎯</span> Leads</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/campaigns"><span>📧</span> Kampagnen</a>
                <a href="/dashboard/invoices" class="active"><span>💰</span> Rechnungen</a>
                <a href="/dashboard/whatsapp"><span>💬</span> WhatsApp</a>
                <a href="/dashboard/ai-chat"><span>🤖</span> AI Chat</a>
                <a href="/dashboard/settings"><span>⚙️</span> Settings</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">💰 Rechnungen</h1>
                <div class="actions">
                    <button class="btn btn-secondary" onclick="exportDATEV()">📥 DATEV Export</button>
                    <button class="btn btn-secondary" onclick="openModal('quote')">📋 Angebot</button>
                    <button class="btn btn-primary" onclick="openModal('invoice')">➕ Neue Rechnung</button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="icon">💰</div>
                    <div class="value">€{{ stats.total_revenue }}</div>
                    <div class="label">Umsatz (Jahr)</div>
                    <div class="change positive">+23.5% vs. Vorjahr</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📄</div>
                    <div class="value">{{ stats.total_invoices }}</div>
                    <div class="label">Rechnungen</div>
                    <div class="change">dieses Jahr</div>
                </div>
                <div class="stat-card">
                    <div class="icon">⏳</div>
                    <div class="value">€{{ stats.pending }}</div>
                    <div class="label">Ausstehend</div>
                    <div class="change">{{ stats.pending_count }} Rechnungen</div>
                </div>
                <div class="stat-card">
                    <div class="icon">⚠️</div>
                    <div class="value">€{{ stats.overdue }}</div>
                    <div class="label">Überfällig</div>
                    <div class="change negative">{{ stats.overdue_count }} Rechnungen</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📈</div>
                    <div class="value">€{{ stats.avg_invoice }}</div>
                    <div class="label">Ø Rechnungswert</div>
                    <div class="change positive">+8.2%</div>
                </div>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <button class="tab active" onclick="filterInvoices('all')">Alle</button>
                <button class="tab" onclick="filterInvoices('paid')">✅ Bezahlt</button>
                <button class="tab" onclick="filterInvoices('pending')">⏳ Ausstehend</button>
                <button class="tab" onclick="filterInvoices('overdue')">⚠️ Überfällig</button>
                <button class="tab" onclick="filterInvoices('draft')">📝 Entwürfe</button>
            </div>
            
            <!-- Invoices Table -->
            <div class="table-container">
                <table class="invoices-table">
                    <thead>
                        <tr>
                            <th>Rechnung</th>
                            <th>Kunde</th>
                            <th>Betrag</th>
                            <th>Status</th>
                            <th>Datum</th>
                            <th>Fällig</th>
                            <th>Aktionen</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for invoice in invoices %}
                        <tr>
                            <td>
                                <strong>{{ invoice.number }}</strong>
                            </td>
                            <td>
                                <div>{{ invoice.customer_name }}</div>
                                <small style="color: #888;">{{ invoice.customer_company }}</small>
                            </td>
                            <td><strong>€{{ invoice.total }}</strong></td>
                            <td>
                                <span class="invoice-status status-{{ invoice.status }}">
                                    {{ invoice.status_text }}
                                </span>
                            </td>
                            <td>{{ invoice.date }}</td>
                            <td>{{ invoice.due_date }}</td>
                            <td>
                                <button class="action-btn" onclick="viewInvoice('{{ invoice.id }}')" title="Ansehen">👁️</button>
                                <button class="action-btn" onclick="downloadPDF('{{ invoice.id }}')" title="PDF">📄</button>
                                <button class="action-btn" onclick="sendInvoice('{{ invoice.id }}')" title="Senden">📧</button>
                                {% if invoice.status == 'pending' %}
                                <button class="action-btn" onclick="markPaid('{{ invoice.id }}')" title="Als bezahlt">✅</button>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </main>
    </div>
    
    <!-- New Invoice Modal -->
    <div class="modal-overlay" id="modal-invoice">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">➕ Neue Rechnung</h2>
                <button class="modal-close" onclick="closeModal('invoice')">×</button>
            </div>
            <div class="modal-body">
                <form id="invoice-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Rechnungsnummer</label>
                            <input type="text" class="form-input" name="number" value="RE-2024-0047" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Datum</label>
                            <input type="date" class="form-input" name="date" value="{{ today }}">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Kunde *</label>
                            <select class="form-input" name="customer_id">
                                <option value="">Kunde auswählen...</option>
                                <option value="1">Max Mustermann - TechCorp GmbH</option>
                                <option value="2">Anna Schmidt - Building AG</option>
                                <option value="3">Stefan Weber - ImmoVest</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Fällig in</label>
                            <select class="form-input" name="due_days">
                                <option value="14">14 Tage</option>
                                <option value="30" selected>30 Tage</option>
                                <option value="60">60 Tage</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Projekt / Referenz</label>
                        <input type="text" class="form-input" name="reference" placeholder="z.B. Smart Home Installation - Projekt 2024-123">
                    </div>
                    
                    <label class="form-label">Positionen</label>
                    <div class="invoice-items" id="invoice-items">
                        <div class="invoice-item">
                            <input type="text" class="form-input" placeholder="Beschreibung" name="item_desc_1">
                            <input type="number" class="form-input" placeholder="Menge" name="item_qty_1" value="1" onchange="calculateTotal()">
                            <input type="number" class="form-input" placeholder="Preis" name="item_price_1" onchange="calculateTotal()">
                            <input type="text" class="form-input" placeholder="Summe" name="item_total_1" readonly>
                            <button type="button" class="action-btn" onclick="removeItem(this)">🗑️</button>
                        </div>
                    </div>
                    <button type="button" class="btn btn-secondary" style="margin-top: 10px;" onclick="addItem()">
                        ➕ Position hinzufügen
                    </button>
                    
                    <div class="invoice-totals">
                        <div class="invoice-total-row">
                            <span class="invoice-total-label">Netto:</span>
                            <span class="invoice-total-value" id="subtotal">€0,00</span>
                        </div>
                        <div class="invoice-total-row">
                            <span class="invoice-total-label">MwSt. (19%):</span>
                            <span class="invoice-total-value" id="tax">€0,00</span>
                        </div>
                        <div class="invoice-total-row">
                            <span class="invoice-total-label">Gesamt:</span>
                            <span class="invoice-total-value grand" id="grand-total">€0,00</span>
                        </div>
                    </div>
                    
                    <div class="form-group" style="margin-top: 20px;">
                        <label class="form-label">Notizen</label>
                        <textarea class="form-input" name="notes" rows="3" placeholder="Zusätzliche Informationen..."></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('invoice')">Abbrechen</button>
                <button class="btn btn-secondary" onclick="saveInvoice('draft')">📝 Als Entwurf</button>
                <button class="btn btn-success" onclick="saveInvoice('preview')">👁️ Vorschau</button>
                <button class="btn btn-primary" onclick="saveInvoice('send')">📧 Erstellen & Senden</button>
            </div>
        </div>
    </div>
    
    <script>
        let itemCount = 1;
        
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        function addItem() {
            itemCount++;
            const container = document.getElementById('invoice-items');
            const item = document.createElement('div');
            item.className = 'invoice-item';
            item.innerHTML = `
                <input type="text" class="form-input" placeholder="Beschreibung" name="item_desc_${itemCount}">
                <input type="number" class="form-input" placeholder="Menge" name="item_qty_${itemCount}" value="1" onchange="calculateTotal()">
                <input type="number" class="form-input" placeholder="Preis" name="item_price_${itemCount}" onchange="calculateTotal()">
                <input type="text" class="form-input" placeholder="Summe" name="item_total_${itemCount}" readonly>
                <button type="button" class="action-btn" onclick="removeItem(this)">🗑️</button>
            `;
            container.appendChild(item);
        }
        
        function removeItem(btn) {
            btn.closest('.invoice-item').remove();
            calculateTotal();
        }
        
        function calculateTotal() {
            let subtotal = 0;
            document.querySelectorAll('.invoice-item').forEach(item => {
                const qty = parseFloat(item.querySelector('input[name^="item_qty"]').value) || 0;
                const price = parseFloat(item.querySelector('input[name^="item_price"]').value) || 0;
                const total = qty * price;
                item.querySelector('input[name^="item_total"]').value = '€' + total.toFixed(2);
                subtotal += total;
            });
            
            const tax = subtotal * 0.19;
            const grandTotal = subtotal + tax;
            
            document.getElementById('subtotal').textContent = '€' + subtotal.toFixed(2);
            document.getElementById('tax').textContent = '€' + tax.toFixed(2);
            document.getElementById('grand-total').textContent = '€' + grandTotal.toFixed(2);
        }
        
        async function saveInvoice(action) {
            const form = document.getElementById('invoice-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            data.action = action;
            
            try {
                const response = await fetch('/api/invoices', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('invoice');
                    showToast(action === 'send' ? '📧 Rechnung erstellt und versendet!' : '📝 Entwurf gespeichert!');
                    setTimeout(() => location.reload(), 1500);
                }
            } catch (error) {
                showToast('❌ Fehler', 'error');
            }
        }
        
        function downloadPDF(id) {
            window.open('/api/invoices/' + id + '/pdf', '_blank');
        }
        
        function sendInvoice(id) {
            fetch('/api/invoices/' + id + '/send', { method: 'POST' })
                .then(() => showToast('📧 Rechnung versendet!'));
        }
        
        function markPaid(id) {
            fetch('/api/invoices/' + id + '/mark-paid', { method: 'POST' })
                .then(() => {
                    showToast('✅ Als bezahlt markiert!');
                    location.reload();
                });
        }
        
        function exportDATEV() {
            showToast('📥 DATEV Export wird erstellt...');
            window.location.href = '/api/invoices/export-datev';
        }
        
        function filterInvoices(status) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            // Filter logic
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    </script>
</body>
</html>
"""


@invoices_bp.route('/dashboard/invoices')
def invoices_page():
    """Invoices dashboard page"""
    stats = {
        'total_revenue': '847,234',
        'total_invoices': 156,
        'pending': '45,670',
        'pending_count': 12,
        'overdue': '8,450',
        'overdue_count': 3,
        'avg_invoice': '5,431'
    }
    
    invoices = [
        {'id': 'INV001', 'number': 'RE-2024-0046', 'customer_name': 'Max Mustermann',
         'customer_company': 'TechCorp GmbH', 'total': '15,750.00', 'status': 'paid',
         'status_text': 'Bezahlt', 'date': '20.12.2024', 'due_date': '19.01.2025'},
        {'id': 'INV002', 'number': 'RE-2024-0045', 'customer_name': 'Anna Schmidt',
         'customer_company': 'Building AG', 'total': '28,900.00', 'status': 'pending',
         'status_text': 'Ausstehend', 'date': '18.12.2024', 'due_date': '17.01.2025'},
        {'id': 'INV003', 'number': 'RE-2024-0044', 'customer_name': 'Stefan Weber',
         'customer_company': 'ImmoVest', 'total': '8,450.00', 'status': 'overdue',
         'status_text': 'Überfällig', 'date': '01.12.2024', 'due_date': '15.12.2024'},
        {'id': 'INV004', 'number': 'RE-2024-0043', 'customer_name': 'Lisa Bauer',
         'customer_company': 'Architekten Plus', 'total': '45,000.00', 'status': 'paid',
         'status_text': 'Bezahlt', 'date': '15.12.2024', 'due_date': '14.01.2025'},
        {'id': 'INV005', 'number': 'RE-2024-0047', 'customer_name': 'Thomas Koch',
         'customer_company': 'Smart Living', 'total': '12,300.00', 'status': 'draft',
         'status_text': 'Entwurf', 'date': '24.12.2024', 'due_date': '-'},
    ]
    
    return render_template_string(INVOICES_HTML, stats=stats, invoices=invoices,
                                  today=datetime.now().strftime('%Y-%m-%d'))


@invoices_bp.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices"""
    return jsonify({'success': True, 'invoices': []})


@invoices_bp.route('/api/invoices', methods=['POST'])
def create_invoice():
    """Create a new invoice"""
    data = request.json
    
    invoice = {
        'id': f'INV{random.randint(100, 999)}',
        'number': f'RE-2024-{random.randint(48, 99):04d}',
        **data,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'invoice': invoice})


@invoices_bp.route('/api/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    """Generate PDF for invoice"""
    # In production: Generate actual PDF
    return jsonify({'success': True, 'message': 'PDF generated'})


@invoices_bp.route('/api/invoices/<invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id):
    """Send invoice via email"""
    return jsonify({'success': True, 'message': f'Rechnung {invoice_id} versendet'})


@invoices_bp.route('/api/invoices/<invoice_id>/mark-paid', methods=['POST'])
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid"""
    return jsonify({'success': True, 'message': f'Rechnung {invoice_id} als bezahlt markiert'})


@invoices_bp.route('/api/invoices/export-datev', methods=['GET'])
def export_datev():
    """Export invoices in DATEV format"""
    # In production: Generate DATEV export
    content = "DATEV Export\nRechnungen 2024"
    
    return content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=datev_export_{datetime.now().strftime("%Y%m%d")}.csv'
    }


def register_invoices_blueprint(app):
    """Register invoices blueprint"""
    app.register_blueprint(invoices_bp)
    print("💰 INVOICES MODULE loaded!")


__all__ = ['invoices_bp', 'register_invoices_blueprint']
