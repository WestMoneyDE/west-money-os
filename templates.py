#!/usr/bin/env python3
"""
================================================================================
    WEST MONEY OS v9.1 - GODMODE HTML TEMPLATES
    Enterprise Universe GmbH - Award-Winning Design
    
    47+ Awards | 4.9/5.0 Rating | 180+ Countries
    
    (c) 2025 Ömer Hüseyin Coşkun - GOD MODE ULTRA INSTINCT
================================================================================
"""

# =============================================================================
# AWARDS DATA - Enterprise Universe GmbH 2025
# =============================================================================

AWARDS_DATA = {
    'summary': {
        'total': 47,
        'diamond': 3,
        'platinum': 6,
        'gold': 10,
        'silver': 4,
        'nominations': 9,
        'rating': 4.9,
        'countries': 180
    },
    'diamond': [
        {'name': 'Diamond Excellence Award 2025', 'org': 'Global Tech Award', 'desc': 'Highest distinction for technological excellence'},
        {'name': 'AI Excellence Award 2025', 'org': 'Machine Learning Award', 'desc': 'Outstanding achievement in AI integration'},
        {'name': 'Diamond Certified Excellence', 'org': 'Quality Certification', 'desc': 'Premium quality standard certification'},
    ],
    'platinum': [
        {'name': 'Platinum Design Award 2025', 'org': 'UX World Award', 'desc': 'Excellence in user experience design'},
        {'name': 'System Architecture Excellence', 'org': 'OASIS Award', 'desc': 'Superior system architecture implementation'},
        {'name': 'User Experience Innovation', 'org': 'OASIS Award', 'desc': 'Groundbreaking UX innovations'},
        {'name': 'Security Implementation', 'org': 'OASIS Award', 'desc': 'Industry-leading security standards'},
        {'name': 'Performance Optimization', 'org': 'OASIS Award', 'desc': 'Outstanding system performance'},
        {'name': 'Platinum Partner Elite Status', 'org': 'Partner Certification', 'desc': 'Elite partnership tier achievement'},
    ],
    'gold': [
        {'name': 'Best Innovation Award 2025', 'org': 'Meta Universe Award', 'desc': 'Pioneering innovations in meta technologies'},
        {'name': '5-Star User Choice Award 2025', 'org': 'User Recognition', 'desc': 'Community-voted excellence award'},
        {'name': 'Innovation Excellence Award 2025', 'org': 'Technology Category', 'desc': 'AtomicCore 4.0# recognition'},
        {'name': 'AI Pioneer Award 2025', 'org': 'AI/ML Category', 'desc': 'Neuronal Chip Tech breakthrough'},
        {'name': 'Interface Design Award', 'org': 'OASIS Award', 'desc': 'Outstanding UI implementation'},
        {'name': 'Code Quality Award', 'org': 'OASIS Award', 'desc': 'Excellence in code standards'},
        {'name': 'Documentation Award', 'org': 'OASIS Award', 'desc': 'Comprehensive documentation'},
        {'name': 'Scalability Award', 'org': 'OASIS Award', 'desc': 'Superior scalability design'},
        {'name': 'Gold Standard Quality', 'org': 'Quality Certification', 'desc': 'Gold-tier quality certification'},
        {'name': 'Best Health Integration 2025', 'org': 'Healthcare Category', 'desc': 'HPV Prevention Module'},
    ],
    'silver': [
        {'name': 'Accessibility Award', 'org': 'OASIS Award', 'desc': 'Outstanding accessibility features'},
        {'name': 'Internationalization Award', 'org': 'OASIS Award', 'desc': '36+ language support'},
        {'name': 'Integration Capability Award', 'org': 'OASIS Award', 'desc': 'Seamless system integrations'},
        {'name': 'Support Excellence Award', 'org': 'OASIS Award', 'desc': 'Superior customer support'},
    ],
    'certifications': [
        {'name': 'ISO 27001 Compliant', 'desc': 'Information security management'},
        {'name': 'DSGVO/GDPR Certified', 'desc': 'Data protection compliance'},
        {'name': 'Smart Home Certified', 'desc': 'LOXONE & ComfortClick certified'},
    ],
    'nominations': [
        {'name': 'Red Dot Design Award 2025', 'status': 'QUALIFIED', 'desc': 'Design Excellence | Platform UI/UX'},
        {'name': 'UX Award 2025', 'status': 'QUALIFIED', 'desc': 'User Experience | West Money OS Interface'},
        {'name': 'Meta Design Excellence Award', 'status': 'PENDING', 'desc': 'Full Platform Suite'},
        {'name': 'Innovation in AI Award', 'status': 'PENDING', 'desc': 'West Money OS AI Engine'},
        {'name': 'Best AR/VR Experience', 'status': 'PENDING', 'desc': 'Meta Quest 3 & Vision Pro'},
        {'name': 'Digital Transformation Award', 'status': 'PENDING', 'desc': 'Enterprise Ecosystem'},
        {'name': 'Creative Technology Award', 'status': 'PENDING', 'desc': 'GOD MODE System'},
    ]
}


# =============================================================================
# LANDING PAGE - GODMODE v9.1 with Awards
# =============================================================================

LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS v9.1 - GODMODE Enterprise Supreme</title>
    <meta name="description" content="Die ultimative All-in-One Business Platform - 47+ Awards, WhatsApp Business, AI Chatbots, CRM">
    <meta name="author" content="Enterprise Universe GmbH">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #8b5cf6;
            --primary-dark: #7c3aed;
            --gold: #fbbf24;
            --diamond: #60a5fa;
            --platinum: #a78bfa;
            --silver: #94a3b8;
            --bg-dark: #0f0f1a;
            --bg-card: rgba(255,255,255,0.05);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: #fff;
            overflow-x: hidden;
        }
        
        /* Animated Background */
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(59, 130, 246, 0.05) 0%, transparent 70%);
        }
        
        /* GOD MODE Badge */
        .godmode-badge {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: linear-gradient(135deg, #f97316, #ef4444, #f97316);
            background-size: 200% 200%;
            animation: gradient-shift 2s ease infinite, pulse-glow 1.5s ease-in-out infinite alternate;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 800;
            font-size: 14px;
            letter-spacing: 1px;
            box-shadow: 0 0 30px rgba(249, 115, 22, 0.5);
        }
        
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        @keyframes pulse-glow {
            from { box-shadow: 0 0 20px rgba(249, 115, 22, 0.5); }
            to { box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); }
        }
        
        /* Hero Section */
        .hero {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 100px 20px 60px;
            text-align: center;
            position: relative;
        }
        
        .logo-container {
            position: relative;
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 120px;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 0 30px rgba(139, 92, 246, 0.5));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        
        .logo-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            border: 3px solid rgba(139, 92, 246, 0.3);
            border-radius: 50%;
            animation: rotate-ring 10s linear infinite;
        }
        
        @keyframes rotate-ring {
            from { transform: translate(-50%, -50%) rotate(0deg); }
            to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        
        h1 {
            font-size: clamp(48px, 8vw, 80px);
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #667eea 100%);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient-text 5s ease infinite;
            margin-bottom: 10px;
        }
        
        @keyframes gradient-text {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .version {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 20px;
            letter-spacing: 3px;
        }
        
        .subtitle {
            font-size: 20px;
            color: rgba(255,255,255,0.7);
            max-width: 700px;
            line-height: 1.6;
            margin-bottom: 40px;
        }
        
        /* Stats Bar */
        .stats-bar {
            display: flex;
            gap: 40px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 50px;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px 30px;
            background: var(--bg-card);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            min-width: 150px;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--gold), #fcd34d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label {
            font-size: 14px;
            color: rgba(255,255,255,0.6);
            margin-top: 5px;
        }
        
        /* Feature Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            max-width: 1000px;
            margin: 0 auto 50px;
            padding: 0 20px;
        }
        
        .feature-card {
            background: var(--bg-card);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 20px 40px rgba(139, 92, 246, 0.2);
        }
        
        .feature-icon {
            font-size: 40px;
            margin-bottom: 15px;
        }
        
        .feature-name {
            font-weight: 600;
            font-size: 15px;
        }
        
        /* Buttons */
        .buttons {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 60px;
        }
        
        .btn {
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        }
        
        .btn-outline {
            background: transparent;
            border: 2px solid rgba(255,255,255,0.3);
            color: white;
        }
        
        .btn-outline:hover {
            border-color: var(--primary);
            background: rgba(139, 92, 246, 0.1);
        }
        
        /* Awards Section */
        .awards-section {
            padding: 80px 20px;
            background: linear-gradient(180deg, transparent, rgba(139, 92, 246, 0.05), transparent);
        }
        
        .section-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 20px;
        }
        
        .section-subtitle {
            text-align: center;
            color: rgba(255,255,255,0.6);
            font-size: 18px;
            margin-bottom: 60px;
        }
        
        .awards-summary {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-bottom: 60px;
        }
        
        .award-summary-card {
            padding: 30px 40px;
            border-radius: 20px;
            text-align: center;
            min-width: 160px;
        }
        
        .award-summary-card.diamond {
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(96, 165, 250, 0.05));
            border: 2px solid var(--diamond);
        }
        
        .award-summary-card.platinum {
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(167, 139, 250, 0.05));
            border: 2px solid var(--platinum);
        }
        
        .award-summary-card.gold {
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.05));
            border: 2px solid var(--gold);
        }
        
        .award-summary-card.silver {
            background: linear-gradient(135deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.05));
            border: 2px solid var(--silver);
        }
        
        .award-count {
            font-size: 48px;
            font-weight: 800;
        }
        
        .diamond .award-count { color: var(--diamond); }
        .platinum .award-count { color: var(--platinum); }
        .gold .award-count { color: var(--gold); }
        .silver .award-count { color: var(--silver); }
        
        .award-type {
            font-size: 14px;
            color: rgba(255,255,255,0.7);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 10px;
        }
        
        /* Award Cards */
        .awards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .award-card {
            background: var(--bg-card);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s ease;
        }
        
        .award-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        }
        
        .award-card.diamond { border-left: 4px solid var(--diamond); }
        .award-card.platinum { border-left: 4px solid var(--platinum); }
        .award-card.gold { border-left: 4px solid var(--gold); }
        .award-card.silver { border-left: 4px solid var(--silver); }
        
        .award-tier {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        
        .award-card.diamond .award-tier { color: var(--diamond); }
        .award-card.platinum .award-tier { color: var(--platinum); }
        .award-card.gold .award-tier { color: var(--gold); }
        .award-card.silver .award-tier { color: var(--silver); }
        
        .award-name {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .award-org {
            font-size: 13px;
            color: var(--primary);
            margin-bottom: 10px;
        }
        
        .award-desc {
            font-size: 14px;
            color: rgba(255,255,255,0.6);
            line-height: 1.5;
        }
        
        /* Certifications */
        .certifications {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 60px;
            padding: 0 20px;
        }
        
        .cert-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 15px 25px;
            border-radius: 50px;
        }
        
        .cert-check {
            color: #22c55e;
            font-size: 20px;
        }
        
        .cert-name {
            font-weight: 600;
            font-size: 14px;
        }
        
        /* Footer */
        footer {
            text-align: center;
            padding: 60px 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .footer-brand {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 15px;
        }
        
        .footer-info {
            color: rgba(255,255,255,0.5);
            font-size: 14px;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
        }
        
        .footer-links a {
            color: rgba(255,255,255,0.6);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s;
        }
        
        .footer-links a:hover {
            color: var(--primary);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .godmode-badge {
                top: 10px;
                right: 10px;
                padding: 8px 16px;
                font-size: 12px;
            }
            
            .logo { font-size: 80px; }
            
            .stats-bar { gap: 20px; }
            
            .stat-item {
                padding: 15px 20px;
                min-width: 120px;
            }
            
            .stat-value { font-size: 28px; }
            
            .buttons { flex-direction: column; align-items: center; }
            
            .btn { width: 100%; max-width: 300px; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <div class="godmode-badge">⚡ GODMODE ENTERPRISE SUPREME</div>
    
    <!-- Hero Section -->
    <section class="hero">
        <div class="logo-container">
            <div class="logo-ring"></div>
            <div class="logo">💰</div>
        </div>
        
        <h1>West Money OS</h1>
        <div class="version">v9.1 ENTERPRISE SUPREME</div>
        
        <p class="subtitle">
            Die ultimative All-in-One Business Platform für Smart Home, 
            CRM, WhatsApp Business, KI-Assistenten und mehr. 
            <strong>47+ Awards</strong> • <strong>180+ Länder</strong> • <strong>4.9/5.0 Rating</strong>
        </p>
        
        <!-- Stats -->
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value">47+</div>
                <div class="stat-label">Awards Won</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">4.9</div>
                <div class="stat-label">User Rating</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">12+</div>
                <div class="stat-label">Nominations</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">180+</div>
                <div class="stat-label">Countries</div>
            </div>
        </div>
        
        <!-- Features -->
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <div class="feature-name">WhatsApp Business</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-name">AI Chatbots</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💼</div>
                <div class="feature-name">CRM & Leads</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🏦</div>
                <div class="feature-name">Revolut Banking</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💳</div>
                <div class="feature-name">Stripe Payments</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <div class="feature-name">DedSec Security</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎤</div>
                <div class="feature-name">Voice Agent</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🏠</div>
                <div class="feature-name">Smart Home</div>
            </div>
        </div>
        
        <!-- Buttons -->
        <div class="buttons">
            <a href="/login" class="btn btn-primary">🚀 Dashboard öffnen</a>
            <a href="/pricing" class="btn btn-outline">💎 Preise ansehen</a>
            <a href="/api/health" class="btn btn-outline">📊 API Status</a>
        </div>
    </section>
    
    <!-- Awards Section -->
    <section class="awards-section">
        <h2 class="section-title">🏆 Awards & Auszeichnungen 2025</h2>
        <p class="section-subtitle">Enterprise Universe GmbH - Mehrfach ausgezeichnete Excellence</p>
        
        <!-- Summary Cards -->
        <div class="awards-summary">
            <div class="award-summary-card diamond">
                <div class="award-count">3</div>
                <div class="award-type">💎 Diamond</div>
            </div>
            <div class="award-summary-card platinum">
                <div class="award-count">6</div>
                <div class="award-type">🔷 Platinum</div>
            </div>
            <div class="award-summary-card gold">
                <div class="award-count">10</div>
                <div class="award-type">🥇 Gold</div>
            </div>
            <div class="award-summary-card silver">
                <div class="award-count">4</div>
                <div class="award-type">🥈 Silver</div>
            </div>
        </div>
        
        <!-- Diamond Awards -->
        <div class="awards-grid">
            <div class="award-card diamond">
                <div class="award-tier">💎 Diamond Tier</div>
                <div class="award-name">Diamond Excellence Award 2025</div>
                <div class="award-org">Global Tech Award</div>
                <div class="award-desc">Highest distinction for technological excellence</div>
            </div>
            <div class="award-card diamond">
                <div class="award-tier">💎 Diamond Tier</div>
                <div class="award-name">AI Excellence Award 2025</div>
                <div class="award-org">Machine Learning Award</div>
                <div class="award-desc">Outstanding achievement in AI integration</div>
            </div>
            <div class="award-card diamond">
                <div class="award-tier">💎 Diamond Tier</div>
                <div class="award-name">Diamond Certified Excellence</div>
                <div class="award-org">Quality Certification</div>
                <div class="award-desc">Premium quality standard certification</div>
            </div>
            
            <!-- Platinum Awards -->
            <div class="award-card platinum">
                <div class="award-tier">🔷 Platinum Tier</div>
                <div class="award-name">Platinum Design Award 2025</div>
                <div class="award-org">UX World Award</div>
                <div class="award-desc">Excellence in user experience design</div>
            </div>
            <div class="award-card platinum">
                <div class="award-tier">🔷 Platinum Tier</div>
                <div class="award-name">System Architecture Excellence</div>
                <div class="award-org">OASIS Award</div>
                <div class="award-desc">Superior system architecture implementation</div>
            </div>
            <div class="award-card platinum">
                <div class="award-tier">🔷 Platinum Tier</div>
                <div class="award-name">Security Implementation</div>
                <div class="award-org">OASIS Award</div>
                <div class="award-desc">Industry-leading security standards</div>
            </div>
            
            <!-- Gold Awards -->
            <div class="award-card gold">
                <div class="award-tier">🥇 Gold Tier</div>
                <div class="award-name">Best Innovation Award 2025</div>
                <div class="award-org">Meta Universe Award</div>
                <div class="award-desc">Pioneering innovations in meta technologies</div>
            </div>
            <div class="award-card gold">
                <div class="award-tier">🥇 Gold Tier</div>
                <div class="award-name">5-Star User Choice Award</div>
                <div class="award-org">User Recognition</div>
                <div class="award-desc">Community-voted excellence award</div>
            </div>
            <div class="award-card gold">
                <div class="award-tier">🥇 Gold Tier</div>
                <div class="award-name">AI Pioneer Award 2025</div>
                <div class="award-org">AI/ML Category</div>
                <div class="award-desc">Neuronal Chip Tech breakthrough</div>
            </div>
            
            <!-- Silver Awards -->
            <div class="award-card silver">
                <div class="award-tier">🥈 Silver Tier</div>
                <div class="award-name">Accessibility Award</div>
                <div class="award-org">OASIS Award</div>
                <div class="award-desc">Outstanding accessibility features</div>
            </div>
            <div class="award-card silver">
                <div class="award-tier">🥈 Silver Tier</div>
                <div class="award-name">Internationalization Award</div>
                <div class="award-org">OASIS Award</div>
                <div class="award-desc">36+ language support</div>
            </div>
            <div class="award-card silver">
                <div class="award-tier">🥈 Silver Tier</div>
                <div class="award-name">Support Excellence Award</div>
                <div class="award-org">OASIS Award</div>
                <div class="award-desc">Superior customer support</div>
            </div>
        </div>
        
        <!-- Certifications -->
        <div class="certifications">
            <div class="cert-badge">
                <span class="cert-check">✓</span>
                <span class="cert-name">ISO 27001 Compliant</span>
            </div>
            <div class="cert-badge">
                <span class="cert-check">✓</span>
                <span class="cert-name">DSGVO/GDPR Certified</span>
            </div>
            <div class="cert-badge">
                <span class="cert-check">✓</span>
                <span class="cert-name">Smart Home Certified</span>
            </div>
            <div class="cert-badge">
                <span class="cert-check">✓</span>
                <span class="cert-name">Red Dot Qualified</span>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer>
        <div class="footer-brand">Enterprise Universe GmbH</div>
        <div class="footer-info">
            CEO: Ömer Hüseyin Coşkun • Frankfurt am Main • Founded 2024
        </div>
        <div class="footer-links">
            <a href="/legal/impressum">Impressum</a>
            <a href="/legal/datenschutz">Datenschutz</a>
            <a href="/pricing">Preise</a>
            <a href="/api/health">API</a>
            <a href="https://enterprise-universe.com" target="_blank">Enterprise Universe</a>
        </div>
    </footer>
</body>
</html>
"""


# =============================================================================
# LOGIN PAGE
# =============================================================================

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0f0f1a;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .bg-effects {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: 
                radial-gradient(ellipse at 30% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 70% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
        }
        
        .login-container {
            width: 100%;
            max-width: 420px;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 50px 40px;
            backdrop-filter: blur(20px);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
        
        .logo-text {
            font-size: 28px;
            font-weight: 800;
            color: white;
        }
        
        .logo-version {
            font-size: 12px;
            color: #8b5cf6;
            font-weight: 600;
            letter-spacing: 2px;
        }
        
        h1 {
            color: white;
            font-size: 24px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        input {
            width: 100%;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-family: inherit;
            transition: all 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .error-message {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 14px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .divider {
            display: flex;
            align-items: center;
            margin: 30px 0;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
        }
        
        .divider span {
            padding: 0 15px;
            color: rgba(255, 255, 255, 0.4);
            font-size: 13px;
        }
        
        .demo-info {
            text-align: center;
            color: rgba(255, 255, 255, 0.5);
            font-size: 13px;
        }
        
        .demo-info code {
            background: rgba(139, 92, 246, 0.2);
            padding: 3px 8px;
            border-radius: 4px;
            color: #a78bfa;
            font-family: monospace;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 25px;
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s;
        }
        
        .back-link:hover {
            color: #8b5cf6;
        }
    </style>
</head>
<body>
    <div class="bg-effects"></div>
    
    <div class="login-container">
        <div class="login-card">
            <div class="logo">
                <div class="logo-icon">💰</div>
                <div class="logo-text">West Money OS</div>
                <div class="logo-version">GODMODE v9.1</div>
            </div>
            
            <h1>Willkommen zurück</h1>
            
            {error_html}
            
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Benutzername oder E-Mail</label>
                    <input type="text" id="username" name="username" placeholder="admin" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Passwort</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required>
                </div>
                
                <button type="submit" class="btn">🚀 Einloggen</button>
            </form>
            
            <div class="divider"><span>Demo-Zugang</span></div>
            
            <div class="demo-info">
                <p>User: <code>admin</code></p>
                <p>Pass: <code>WestMoney2025!</code></p>
            </div>
            
            <a href="/" class="back-link">← Zurück zur Startseite</a>
        </div>
    </div>
</body>
</html>
"""


# =============================================================================
# DASHBOARD PAGE
# =============================================================================

def get_dashboard_html(user):
    """Generate dashboard HTML for logged-in user"""
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #0f0f1a;
            color: white;
            min-height: 100vh;
        }}
        
        /* Sidebar */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 260px;
            height: 100vh;
            background: rgba(15, 15, 26, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 25px;
            overflow-y: auto;
        }}
        
        .sidebar-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 40px;
        }}
        
        .sidebar-logo-icon {{
            font-size: 36px;
        }}
        
        .sidebar-logo-text {{
            font-size: 18px;
            font-weight: 800;
        }}
        
        .sidebar-logo-version {{
            font-size: 10px;
            color: #8b5cf6;
            font-weight: 600;
        }}
        
        .nav-section {{
            margin-bottom: 30px;
        }}
        
        .nav-section-title {{
            font-size: 11px;
            color: rgba(255, 255, 255, 0.4);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 15px;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: all 0.2s;
            margin-bottom: 5px;
        }}
        
        .nav-item:hover, .nav-item.active {{
            background: rgba(139, 92, 246, 0.15);
            color: white;
        }}
        
        .nav-item.active {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(236, 72, 153, 0.2));
        }}
        
        .nav-icon {{
            font-size: 18px;
        }}
        
        /* Main Content */
        .main {{
            margin-left: 260px;
            padding: 30px;
            min-height: 100vh;
        }}
        
        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .welcome {{
            font-size: 28px;
            font-weight: 700;
        }}
        
        .welcome span {{
            color: #8b5cf6;
        }}
        
        .user-menu {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .user-avatar {{
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }}
        
        .user-info {{
            text-align: right;
        }}
        
        .user-name {{
            font-weight: 600;
            font-size: 15px;
        }}
        
        .user-plan {{
            font-size: 12px;
            color: #8b5cf6;
            font-weight: 600;
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(139, 92, 246, 0.3);
        }}
        
        .stat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .stat-icon {{
            font-size: 24px;
        }}
        
        .stat-change {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
        }}
        
        .stat-change.positive {{
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
        }}
        
        .stat-change.negative {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.5);
        }}
        
        /* Quick Actions */
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        
        .actions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .action-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            text-decoration: none;
            color: white;
            transition: all 0.3s;
        }}
        
        .action-card:hover {{
            transform: translateY(-3px);
            background: rgba(139, 92, 246, 0.1);
            border-color: rgba(139, 92, 246, 0.3);
        }}
        
        .action-icon {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .action-title {{
            font-weight: 600;
            font-size: 14px;
        }}
        
        /* GODMODE Banner */
        .godmode-banner {{
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(239, 68, 68, 0.1));
            border: 1px solid rgba(249, 115, 22, 0.3);
            border-radius: 16px;
            padding: 30px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .godmode-icon {{
            font-size: 48px;
        }}
        
        .godmode-content h3 {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #fbbf24;
        }}
        
        .godmode-content p {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            line-height: 1.5;
        }}
        
        /* Logout */
        .logout-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 10px;
            color: #f87171;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .logout-btn:hover {{
            background: rgba(239, 68, 68, 0.2);
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}
            
            .main {{
                margin-left: 0;
            }}
        }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-logo">
            <span class="sidebar-logo-icon">💰</span>
            <div>
                <div class="sidebar-logo-text">West Money</div>
                <div class="sidebar-logo-version">GODMODE v9.1</div>
            </div>
        </div>
        
        <nav>
            <div class="nav-section">
                <div class="nav-section-title">Übersicht</div>
                <a href="/dashboard" class="nav-item active">
                    <span class="nav-icon">📊</span>
                    Dashboard
                </a>
                <a href="/api/dashboard/stats" class="nav-item">
                    <span class="nav-icon">📈</span>
                    Statistiken
                </a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">CRM</div>
                <a href="/api/contacts" class="nav-item">
                    <span class="nav-icon">👥</span>
                    Kontakte
                </a>
                <a href="/api/leads" class="nav-item">
                    <span class="nav-icon">💼</span>
                    Leads
                </a>
                <a href="/api/campaigns" class="nav-item">
                    <span class="nav-icon">📧</span>
                    Kampagnen
                </a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Finanzen</div>
                <a href="/api/banking/accounts" class="nav-item">
                    <span class="nav-icon">🏦</span>
                    Banking
                </a>
                <a href="/api/invoices" class="nav-item">
                    <span class="nav-icon">📄</span>
                    Rechnungen
                </a>
                <a href="/api/analytics/revenue" class="nav-item">
                    <span class="nav-icon">💰</span>
                    Revenue
                </a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Kommunikation</div>
                <a href="/api/whatsapp/status" class="nav-item">
                    <span class="nav-icon">📱</span>
                    WhatsApp
                </a>
                <a href="/api/ai/chat" class="nav-item">
                    <span class="nav-icon">🤖</span>
                    AI Chat
                </a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">System</div>
                <a href="/api/health" class="nav-item">
                    <span class="nav-icon">💚</span>
                    API Status
                </a>
                <a href="/api/security/events" class="nav-item">
                    <span class="nav-icon">🔒</span>
                    Security
                </a>
                <a href="/logout" class="nav-item">
                    <span class="nav-icon">🚪</span>
                    Logout
                </a>
            </div>
        </nav>
    </aside>
    
    <!-- Main Content -->
    <main class="main">
        <header class="header">
            <div class="welcome">
                Willkommen zurück, <span>{user.name or user.username}</span>! 👋
            </div>
            
            <div class="user-menu">
                <div class="user-info">
                    <div class="user-name">{user.name or user.username}</div>
                    <div class="user-plan">{user.plan.upper()} Plan</div>
                </div>
                <div class="user-avatar">
                    {(user.name or user.username)[:2].upper()}
                </div>
            </div>
        </header>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">👥</span>
                    <span class="stat-change positive">+12%</span>
                </div>
                <div class="stat-value">847</div>
                <div class="stat-label">Kontakte</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">💼</span>
                    <span class="stat-change positive">+8%</span>
                </div>
                <div class="stat-value">156</div>
                <div class="stat-label">Aktive Leads</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">💰</span>
                    <span class="stat-change positive">+23%</span>
                </div>
                <div class="stat-value">€847K</div>
                <div class="stat-label">Revenue YTD</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">📧</span>
                    <span class="stat-change negative">-3%</span>
                </div>
                <div class="stat-value">94.2%</div>
                <div class="stat-label">Zustellrate</div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <h2 class="section-title">⚡ Schnellzugriff</h2>
        <div class="actions-grid">
            <a href="/api/contacts" class="action-card">
                <div class="action-icon">➕</div>
                <div class="action-title">Kontakt anlegen</div>
            </a>
            <a href="/api/leads" class="action-card">
                <div class="action-icon">💼</div>
                <div class="action-title">Lead erstellen</div>
            </a>
            <a href="/api/whatsapp/send" class="action-card">
                <div class="action-icon">📱</div>
                <div class="action-title">WhatsApp senden</div>
            </a>
            <a href="/api/campaigns" class="action-card">
                <div class="action-icon">📧</div>
                <div class="action-title">Kampagne starten</div>
            </a>
            <a href="/api/invoices" class="action-card">
                <div class="action-icon">📄</div>
                <div class="action-title">Rechnung erstellen</div>
            </a>
            <a href="/api/ai/chat" class="action-card">
                <div class="action-icon">🤖</div>
                <div class="action-title">AI Assistant</div>
            </a>
        </div>
        
        <!-- GODMODE Banner -->
        <div class="godmode-banner">
            <div class="godmode-icon">🔥</div>
            <div class="godmode-content">
                <h3>⚡ GODMODE ENTERPRISE SUPREME AKTIV</h3>
                <p>
                    Alle Enterprise-Features freigeschaltet: WhatsApp Business API, Claude AI Integration, 
                    Revolut Banking, Stripe Payments, HubSpot CRM Sync, DedSec Security und 47+ weitere Integrationen.
                </p>
            </div>
        </div>
    </main>
</body>
</html>
"""


# =============================================================================
# PRICING PAGE
# =============================================================================

PRICING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preise - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0f0f1a;
            color: white;
            min-height: 100vh;
            padding: 60px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            font-size: 18px;
            margin-bottom: 60px;
        }
        
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }
        
        .plan-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 40px 30px;
            position: relative;
            transition: all 0.3s;
        }
        
        .plan-card:hover {
            transform: translateY(-5px);
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        .plan-card.popular {
            border-color: #8b5cf6;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.05));
        }
        
        .popular-badge {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }
        
        .plan-name {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .plan-price {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 5px;
        }
        
        .plan-price span {
            font-size: 18px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.5);
        }
        
        .plan-billing {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.5);
            margin-bottom: 30px;
        }
        
        .plan-features {
            list-style: none;
            margin-bottom: 30px;
        }
        
        .plan-features li {
            padding: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 15px;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .plan-features li::before {
            content: '✓';
            color: #22c55e;
            font-weight: bold;
        }
        
        .plan-btn {
            display: block;
            width: 100%;
            padding: 16px;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .plan-btn:hover {
            background: rgba(139, 92, 246, 0.3);
        }
        
        .plan-card.popular .plan-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 50px;
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
        }
        
        .back-link:hover {
            color: #8b5cf6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💎 Preise</h1>
        <p class="subtitle">Wähle den Plan, der zu deinem Business passt</p>
        
        <div class="pricing-grid">
            <div class="plan-card">
                <div class="plan-name">Free</div>
                <div class="plan-price">€0 <span>/mo</span></div>
                <div class="plan-billing">Kostenlos für immer</div>
                <ul class="plan-features">
                    <li>3 Kontakte</li>
                    <li>2 Leads</li>
                    <li>Basic Dashboard</li>
                    <li>Community Support</li>
                </ul>
                <a href="/login" class="plan-btn">Kostenlos starten</a>
            </div>
            
            <div class="plan-card">
                <div class="plan-name">Starter</div>
                <div class="plan-price">€29 <span>/mo</span></div>
                <div class="plan-billing">€290/Jahr (2 Monate gratis)</div>
                <ul class="plan-features">
                    <li>50 Kontakte</li>
                    <li>25 Leads</li>
                    <li>Handelsregister API</li>
                    <li>Export (CSV/PDF)</li>
                    <li>E-Mail Support</li>
                </ul>
                <a href="/login" class="plan-btn">Plan wählen</a>
            </div>
            
            <div class="plan-card popular">
                <div class="popular-badge">⭐ BELIEBT</div>
                <div class="plan-name">Professional</div>
                <div class="plan-price">€99 <span>/mo</span></div>
                <div class="plan-billing">€990/Jahr (2 Monate gratis)</div>
                <ul class="plan-features">
                    <li>Unlimited Kontakte</li>
                    <li>WhatsApp Business API</li>
                    <li>HubSpot Integration</li>
                    <li>API Zugang</li>
                    <li>Team Features</li>
                    <li>Priority Support</li>
                </ul>
                <a href="/login" class="plan-btn">Jetzt upgraden</a>
            </div>
            
            <div class="plan-card">
                <div class="plan-name">Enterprise</div>
                <div class="plan-price">€299 <span>/mo</span></div>
                <div class="plan-billing">€2990/Jahr (2 Monate gratis)</div>
                <ul class="plan-features">
                    <li>Alles aus Professional</li>
                    <li>White Label Option</li>
                    <li>Custom Integrations</li>
                    <li>SLA 99.9%</li>
                    <li>AI Concierge</li>
                    <li>Dedicated Account Manager</li>
                </ul>
                <a href="/login" class="plan-btn">Kontakt aufnehmen</a>
            </div>
        </div>
        
        <a href="/" class="back-link">← Zurück zur Startseite</a>
    </div>
</body>
</html>
"""
