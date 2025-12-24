"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎨 THEME SELECTOR - WEST MONEY OS v12.0                                      ║
║  6 Themes: GOD MODE, Ultra Instinct, Broly, Enterprise, Cyberpunk, Gold      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session
import json

theme_bp = Blueprint('theme', __name__)

# ============================================================================
# THEME DEFINITIONS
# ============================================================================

THEMES = {
    'cyberpunk': {
        'name': 'Cyberpunk',
        'icon': '🎮',
        'description': 'Neon Pink & Cyan - DedSec Style',
        'primary': '#ff00ff',
        'secondary': '#00ffff',
        'bg_start': '#0a0a15',
        'bg_mid': '#150a1a',
        'bg_end': '#0a0510',
        'text': '#ffffff',
        'accent': '#ff00ff',
        'success': '#00ffff',
        'card_bg': 'rgba(255,0,255,0.1)',
        'card_border': 'rgba(255,0,255,0.3)',
        'glow': 'rgba(255,0,255,0.4)'
    },
    'god_mode': {
        'name': 'GOD MODE',
        'icon': '🔥',
        'description': 'Rot & Gold - Dragon Ball Super',
        'primary': '#ff3333',
        'secondary': '#ff6600',
        'bg_start': '#1a0a0a',
        'bg_mid': '#2a1010',
        'bg_end': '#1a0505',
        'text': '#ffffff',
        'accent': '#ff4444',
        'success': '#ff6600',
        'card_bg': 'rgba(255,0,0,0.1)',
        'card_border': 'rgba(255,0,0,0.3)',
        'glow': 'rgba(255,0,0,0.4)'
    },
    'ultra_instinct': {
        'name': 'Ultra Instinct',
        'icon': '❄️',
        'description': 'Silber & Blau - Clean & Minimalistisch',
        'primary': '#c0d0ff',
        'secondary': '#8090c0',
        'bg_start': '#0a0a1a',
        'bg_mid': '#101025',
        'bg_end': '#0a0a15',
        'text': '#ffffff',
        'accent': '#a0c0ff',
        'success': '#c0d0ff',
        'card_bg': 'rgba(180,200,255,0.1)',
        'card_border': 'rgba(180,200,255,0.2)',
        'glow': 'rgba(180,200,255,0.3)'
    },
    'broly_rage': {
        'name': 'Broly Rage',
        'icon': '💚',
        'description': 'Neon Grün - Legendary Power',
        'primary': '#00ff44',
        'secondary': '#88ff00',
        'bg_start': '#0a1a0a',
        'bg_mid': '#102510',
        'bg_end': '#051005',
        'text': '#ffffff',
        'accent': '#00ff44',
        'success': '#88ff00',
        'card_bg': 'rgba(0,255,0,0.1)',
        'card_border': 'rgba(0,255,0,0.25)',
        'glow': 'rgba(0,255,0,0.4)'
    },
    'enterprise': {
        'name': 'Enterprise',
        'icon': '🏢',
        'description': 'Blau - Professionell & Business',
        'primary': '#0099ff',
        'secondary': '#0066cc',
        'bg_start': '#0a0a1a',
        'bg_mid': '#0a1525',
        'bg_end': '#051020',
        'text': '#ffffff',
        'accent': '#0099ff',
        'success': '#00cc66',
        'card_bg': 'rgba(0,150,255,0.1)',
        'card_border': 'rgba(0,150,255,0.25)',
        'glow': 'rgba(0,150,255,0.3)'
    },
    'luxury_gold': {
        'name': 'Luxury Gold',
        'icon': '👑',
        'description': 'Gold & Schwarz - Premium Edition',
        'primary': '#ffd700',
        'secondary': '#ff8c00',
        'bg_start': '#0a0a0a',
        'bg_mid': '#1a1510',
        'bg_end': '#0a0805',
        'text': '#ffffff',
        'accent': '#ffd700',
        'success': '#ffa500',
        'card_bg': 'rgba(255,215,0,0.1)',
        'card_border': 'rgba(255,215,0,0.25)',
        'glow': 'rgba(255,215,0,0.3)'
    }
}

# Default theme
DEFAULT_THEME = 'cyberpunk'

# ============================================================================
# THEME SELECTOR PAGE
# ============================================================================

THEME_SELECTOR_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Theme Selector - West Money OS</title>
    <style>
        :root {
            --primary: {{ theme.primary }};
            --secondary: {{ theme.secondary }};
            --bg-start: {{ theme.bg_start }};
            --bg-mid: {{ theme.bg_mid }};
            --bg-end: {{ theme.bg_end }};
            --text: {{ theme.text }};
            --accent: {{ theme.accent }};
            --success: {{ theme.success }};
            --card-bg: {{ theme.card_bg }};
            --card-border: {{ theme.card_border }};
            --glow: {{ theme.glow }};
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-mid) 50%, var(--bg-end) 100%);
            min-height: 100vh;
            color: var(--text);
        }
        .container { display: flex; min-height: 100vh; }
        
        .sidebar {
            width: 260px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--card-border);
            padding: 20px;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { 
            background: var(--card-bg); 
            color: var(--primary); 
        }
        
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        
        .header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 30px;
        }
        .title { font-size: 2rem; font-weight: 700; }
        .subtitle { color: #888; margin-top: 5px; }
        
        /* Theme Grid */
        .theme-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .theme-card {
            background: rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
        }
        .theme-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        .theme-card.active {
            border-color: var(--primary);
            box-shadow: 0 0 30px var(--glow);
        }
        .theme-card.active::after {
            content: '✓ AKTIV';
            position: absolute;
            top: 15px;
            right: 15px;
            background: var(--primary);
            color: #000;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        
        .theme-preview {
            height: 180px;
            position: relative;
            overflow: hidden;
        }
        
        .theme-info {
            padding: 20px;
        }
        .theme-name {
            display: flex; align-items: center; gap: 10px;
            font-size: 1.3rem; font-weight: 700;
            margin-bottom: 8px;
        }
        .theme-desc {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        .theme-colors {
            display: flex; gap: 8px;
        }
        .color-dot {
            width: 24px; height: 24px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        /* Preview Styles for each theme */
        .preview-cyberpunk {
            background: linear-gradient(135deg, #0a0a15 0%, #150a1a 50%, #0a0510 100%);
        }
        .preview-cyberpunk .preview-card { background: rgba(255,0,255,0.15); border-color: rgba(255,0,255,0.4); }
        .preview-cyberpunk .preview-value { color: #00ffff; }
        .preview-cyberpunk .preview-nav { border-color: rgba(255,0,255,0.3); }
        .preview-cyberpunk .preview-active { color: #ff00ff; }
        
        .preview-god_mode {
            background: linear-gradient(135deg, #1a0a0a 0%, #2a1010 50%, #1a0505 100%);
        }
        .preview-god_mode .preview-card { background: rgba(255,0,0,0.15); border-color: rgba(255,0,0,0.4); }
        .preview-god_mode .preview-value { color: #ff4444; }
        .preview-god_mode .preview-nav { border-color: rgba(255,0,0,0.3); }
        .preview-god_mode .preview-active { color: #ff3333; }
        
        .preview-ultra_instinct {
            background: linear-gradient(135deg, #0a0a1a 0%, #101025 50%, #0a0a15 100%);
        }
        .preview-ultra_instinct .preview-card { background: rgba(180,200,255,0.15); border-color: rgba(180,200,255,0.3); }
        .preview-ultra_instinct .preview-value { color: #a0c0ff; }
        .preview-ultra_instinct .preview-nav { border-color: rgba(180,200,255,0.2); }
        .preview-ultra_instinct .preview-active { color: #c0d0ff; }
        
        .preview-broly_rage {
            background: linear-gradient(135deg, #0a1a0a 0%, #102510 50%, #051005 100%);
        }
        .preview-broly_rage .preview-card { background: rgba(0,255,0,0.15); border-color: rgba(0,255,0,0.4); }
        .preview-broly_rage .preview-value { color: #00ff44; }
        .preview-broly_rage .preview-nav { border-color: rgba(0,255,0,0.3); }
        .preview-broly_rage .preview-active { color: #00ff44; }
        
        .preview-enterprise {
            background: linear-gradient(135deg, #0a0a1a 0%, #0a1525 50%, #051020 100%);
        }
        .preview-enterprise .preview-card { background: rgba(0,150,255,0.15); border-color: rgba(0,150,255,0.3); }
        .preview-enterprise .preview-value { color: #0099ff; }
        .preview-enterprise .preview-nav { border-color: rgba(0,150,255,0.2); }
        .preview-enterprise .preview-active { color: #0099ff; }
        
        .preview-luxury_gold {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1510 50%, #0a0805 100%);
        }
        .preview-luxury_gold .preview-card { background: rgba(255,215,0,0.15); border-color: rgba(255,215,0,0.3); }
        .preview-luxury_gold .preview-value { color: #ffd700; }
        .preview-luxury_gold .preview-nav { border-color: rgba(255,215,0,0.2); }
        .preview-luxury_gold .preview-active { color: #ffd700; }
        
        /* Mini Preview Elements */
        .preview-header {
            padding: 10px 15px;
            display: flex; align-items: center; gap: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .preview-logo { font-size: 1rem; }
        .preview-title { font-size: 0.8rem; font-weight: 600; }
        
        .preview-cards {
            display: flex; gap: 10px;
            padding: 15px;
        }
        .preview-card {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid;
            text-align: center;
        }
        .preview-icon { font-size: 1rem; }
        .preview-value { font-size: 1rem; font-weight: 700; }
        .preview-label { font-size: 0.6rem; color: #888; }
        
        .preview-nav {
            position: absolute;
            bottom: 0; left: 0; right: 0;
            padding: 8px 15px;
            display: flex; gap: 15px;
            font-size: 0.7rem;
            background: rgba(0,0,0,0.5);
            border-top: 1px solid;
        }
        .preview-nav span { color: #666; }
        
        /* Buttons */
        .btn {
            padding: 14px 28px; border: none; border-radius: 12px;
            font-size: 1rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s; display: inline-flex; align-items: center; gap: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #000;
        }
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px var(--glow);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: var(--text);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 18px 28px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #000;
            border-radius: 12px;
            font-weight: 600;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Section Title */
        .section-title {
            font-size: 1.1rem;
            color: #888;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">🎨</span>
                <span class="logo-text">Theme Selector</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/settings"><span>⚙️</span> Settings</a>
                <a href="/dashboard/theme" class="active"><span>🎨</span> Themes</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <div>
                    <h1 class="title">🎨 Theme auswählen</h1>
                    <p class="subtitle">Wähle dein bevorzugtes Design für West Money OS</p>
                </div>
                <button class="btn btn-secondary" onclick="location.href='/dashboard/settings'">
                    ⚙️ Zurück zu Settings
                </button>
            </div>
            
            <div class="section-title">Verfügbare Themes</div>
            
            <div class="theme-grid">
                {% for theme_id, t in themes.items() %}
                <div class="theme-card {% if theme_id == current_theme %}active{% endif %}" 
                     onclick="selectTheme('{{ theme_id }}')"
                     data-theme="{{ theme_id }}">
                    
                    <div class="theme-preview preview-{{ theme_id }}">
                        <div class="preview-header">
                            <span class="preview-logo">🔐</span>
                            <span class="preview-title" style="color: {{ t.primary }}">WEST MONEY OS</span>
                        </div>
                        <div class="preview-cards">
                            <div class="preview-card">
                                <div class="preview-icon">👥</div>
                                <div class="preview-value">1,234</div>
                                <div class="preview-label">Kontakte</div>
                            </div>
                            <div class="preview-card">
                                <div class="preview-icon">🎯</div>
                                <div class="preview-value">89</div>
                                <div class="preview-label">Leads</div>
                            </div>
                            <div class="preview-card">
                                <div class="preview-icon">💰</div>
                                <div class="preview-value">€847K</div>
                                <div class="preview-label">Umsatz</div>
                            </div>
                        </div>
                        <div class="preview-nav">
                            <span class="preview-active">📊 Dashboard</span>
                            <span>🐉 Broly</span>
                            <span>📧 Kampagnen</span>
                        </div>
                    </div>
                    
                    <div class="theme-info">
                        <div class="theme-name">
                            <span>{{ t.icon }}</span>
                            <span>{{ t.name }}</span>
                        </div>
                        <div class="theme-desc">{{ t.description }}</div>
                        <div class="theme-colors">
                            <div class="color-dot" style="background: {{ t.primary }};"></div>
                            <div class="color-dot" style="background: {{ t.secondary }};"></div>
                            <div class="color-dot" style="background: {{ t.bg_mid }};"></div>
                            <div class="color-dot" style="background: {{ t.accent }};"></div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #666; margin-bottom: 20px;">
                    Das ausgewählte Theme wird auf alle Module angewendet.
                </p>
            </div>
        </main>
    </div>
    
    <script>
        function selectTheme(themeId) {
            // Remove active from all cards
            document.querySelectorAll('.theme-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Add active to selected
            document.querySelector(`[data-theme="${themeId}"]`).classList.add('active');
            
            // Save theme
            fetch('/api/theme/set', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: themeId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`${data.theme.icon} ${data.theme.name} Theme aktiviert!`);
                    
                    // Reload after short delay to apply theme
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                }
            });
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

# ============================================================================
# CSS VARIABLES GENERATOR
# ============================================================================

def get_theme_css(theme_id: str) -> str:
    """Generate CSS variables for a theme"""
    theme = THEMES.get(theme_id, THEMES[DEFAULT_THEME])
    
    return f"""
    :root {{
        --primary: {theme['primary']};
        --secondary: {theme['secondary']};
        --bg-start: {theme['bg_start']};
        --bg-mid: {theme['bg_mid']};
        --bg-end: {theme['bg_end']};
        --text: {theme['text']};
        --accent: {theme['accent']};
        --success: {theme['success']};
        --card-bg: {theme['card_bg']};
        --card-border: {theme['card_border']};
        --glow: {theme['glow']};
    }}
    
    body {{
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-mid) 50%, var(--bg-end) 100%);
    }}
    
    .logo-text {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .btn-primary {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
    }}
    
    .btn-primary:hover {{
        box-shadow: 0 8px 25px var(--glow);
    }}
    
    .stat-card, .card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
    }}
    
    .stat-value, .value {{
        color: var(--primary);
    }}
    
    .nav a:hover, .nav a.active {{
        background: var(--card-bg);
        color: var(--primary);
    }}
    
    .sidebar {{
        border-right: 1px solid var(--card-border);
    }}
    """


def get_theme_style_tag(theme_id: str) -> str:
    """Generate a complete style tag with theme CSS"""
    css = get_theme_css(theme_id)
    return f"<style>{css}</style>"


# ============================================================================
# ROUTES
# ============================================================================

@theme_bp.route('/dashboard/theme')
def theme_page():
    """Theme selector page"""
    current_theme = session.get('theme', DEFAULT_THEME)
    theme = THEMES.get(current_theme, THEMES[DEFAULT_THEME])
    
    return render_template_string(
        THEME_SELECTOR_HTML,
        themes=THEMES,
        current_theme=current_theme,
        theme=theme
    )


@theme_bp.route('/api/theme/current', methods=['GET'])
def get_current_theme():
    """Get current theme"""
    theme_id = session.get('theme', DEFAULT_THEME)
    theme = THEMES.get(theme_id, THEMES[DEFAULT_THEME])
    
    return jsonify({
        'success': True,
        'theme_id': theme_id,
        'theme': theme,
        'css': get_theme_css(theme_id)
    })


@theme_bp.route('/api/theme/set', methods=['POST'])
def set_theme():
    """Set theme"""
    data = request.json
    theme_id = data.get('theme', DEFAULT_THEME)
    
    if theme_id not in THEMES:
        return jsonify({'success': False, 'error': 'Unknown theme'}), 400
    
    session['theme'] = theme_id
    theme = THEMES[theme_id]
    
    return jsonify({
        'success': True,
        'theme_id': theme_id,
        'theme': theme,
        'message': f'{theme["name"]} Theme aktiviert!'
    })


@theme_bp.route('/api/theme/list', methods=['GET'])
def list_themes():
    """List all available themes"""
    return jsonify({
        'success': True,
        'themes': THEMES,
        'current': session.get('theme', DEFAULT_THEME)
    })


@theme_bp.route('/api/theme/css/<theme_id>', methods=['GET'])
def get_theme_css_endpoint(theme_id: str):
    """Get CSS for a specific theme"""
    if theme_id not in THEMES:
        theme_id = DEFAULT_THEME
    
    css = get_theme_css(theme_id)
    return css, 200, {'Content-Type': 'text/css'}


# ============================================================================
# HELPER FUNCTIONS FOR OTHER MODULES
# ============================================================================

def get_current_theme_id() -> str:
    """Get current theme ID from session"""
    return session.get('theme', DEFAULT_THEME)


def get_current_theme() -> dict:
    """Get current theme dictionary"""
    theme_id = get_current_theme_id()
    return THEMES.get(theme_id, THEMES[DEFAULT_THEME])


def inject_theme_css() -> str:
    """Get CSS to inject into pages"""
    return get_theme_style_tag(get_current_theme_id())


# ============================================================================
# REGISTER BLUEPRINT
# ============================================================================

def register_theme_blueprint(app):
    """Register Theme blueprint"""
    app.register_blueprint(theme_bp)
    print("🎨 THEME SELECTOR loaded!")


__all__ = [
    'theme_bp', 
    'register_theme_blueprint',
    'THEMES',
    'get_current_theme',
    'get_current_theme_id',
    'get_theme_css',
    'inject_theme_css'
]
