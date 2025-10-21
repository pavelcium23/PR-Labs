#!/usr/bin/env python3
"""
Script to generate sample content for the HTTP server
Creates HTML, PNG, and PDF files with nested directories
FLOPTROPICA EDITION - The Ultimate Flop Library
Based on official Floptok Wiki lore!
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_directories():
    """Create the directory structure."""
    dirs = [
        'content',
        'content/badussy-war',
        'content/government',
        'content/tourist-guide',
        'downloads'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    print("✓ Directories created")

def create_flop_pdf(filename, title, content_lines, subtitle=""):
    """Create a fabulous Floptropica-themed PDF file."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Cute pastel background
    c.setFillColorRGB(1, 0.9, 0.95)  # Light pink
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Title box with gradient effect
    c.setFillColorRGB(1, 0.4, 0.7)  # Bright pink
    c.rect(40, height - 110, width - 80, 70, fill=True, stroke=False)
    
    # Decorative corners
    c.setFillColorRGB(1, 0.7, 0.85)
    c.circle(50, height - 50, 15, fill=True)
    c.circle(width - 50, height - 50, 15, fill=True)
    
    # Title
    c.setFillColorRGB(1, 1, 1)  # White
    c.setFont("Helvetica-Bold", 26)
    text_width = c.stringWidth(title, "Helvetica-Bold", 26)
    c.drawString((width - text_width) / 2, height - 80, title)
    
    # Subtitle
    if subtitle:
        c.setFont("Helvetica-Oblique", 13)
        c.setFillColorRGB(1, 1, 0.9)
        text_width = c.stringWidth(subtitle, "Helvetica-Oblique", 13)
        c.drawString((width - text_width) / 2, height - 100, subtitle)
    
    # Content box
    c.setFillColorRGB(1, 1, 1)  # White
    c.roundRect(50, 90, width - 100, height - 230, 15, fill=True, stroke=True)
    
    # Content
    c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray text
    c.setFont("Helvetica", 11)
    y_position = height - 150
    for line in content_lines:
        if line.startswith('###'):
            # Section header
            c.setFont("Helvetica-Bold", 13)
            c.setFillColorRGB(1, 0.2, 0.6)
            c.drawString(70, y_position, line.replace('###', '').strip())
            c.setFont("Helvetica", 11)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            y_position -= 22
        elif line.startswith('•'):
            # Bullet point
            c.setFillColorRGB(1, 0.5, 0.7)
            c.circle(75, y_position + 3, 3, fill=True)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawString(85, y_position, line.replace('•', '').strip())
            y_position -= 16
        elif line.strip() == '':
            y_position -= 8
        else:
            # Regular text
            c.drawString(70, y_position, line)
            y_position -= 16
        
        if y_position < 110:  # New page if needed
            c.showPage()
            c.setFillColorRGB(1, 0.9, 0.95)
            c.rect(0, 0, width, height, fill=True, stroke=False)
            c.setFillColorRGB(1, 1, 1)
            c.roundRect(50, 90, width - 100, height - 180, 15, fill=True, stroke=True)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 11)
            y_position = height - 110
    
    # Footer with emoji decorations
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(1, 0.4, 0.7)
    footer_text = "🌺 THE UNITED QUEENDOM OF FLOPTROPICA 🌺"
    text_width = c.stringWidth(footer_text, "Helvetica-Bold", 9)
    c.drawString((width - text_width) / 2, 60, footer_text)
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    motto = 'Official Motto: "AURGHHH" ✨'
    text_width = c.stringWidth(motto, "Helvetica-Oblique", 8)
    c.drawString((width - text_width) / 2, 45, motto)
    
    c.save()

def create_flop_image(filename, text, width=800, height=400, style="pink"):
    """Create a super cute Floptropica-themed PNG image."""
    # Cuter pastel colors
    if style == "pink":
        bg_color = (255, 192, 203)  # Baby pink
        border_color = (255, 105, 180)  # Hot pink
    elif style == "purple":
        bg_color = (221, 160, 221)  # Plum
        border_color = (186, 85, 211)  # Medium orchid
    elif style == "blue":
        bg_color = (173, 216, 230)  # Light blue
        border_color = (135, 206, 250)  # Sky blue
    else:
        bg_color = (255, 228, 225)  # Misty rose
        border_color = (255, 182, 193)  # Light pink
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_emoji = ImageFont.load_default()
    
    # Draw kawaii decorations
    emoji_list = ["🌺", "✨", "💖", "🌸", "💕", "🦋", "🌴", "🌊"]
    import random
    for i in range(15):
        x = random.randint(30, width-60)
        y = random.randint(30, height-60)
        emoji = random.choice(emoji_list)
        draw.text((x, y), emoji, fill=border_color, font=font_emoji)
    
    # Draw rounded border
    border_width = 10
    draw.rounded_rectangle(
        [(border_width, border_width), (width-border_width, height-border_width)],
        radius=25,
        outline=border_color,
        width=border_width
    )
    
    # Text with cute shadow
    bbox = draw.textbbox((0, 0), text, font=font_title)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2 - 20)
    
    # Kawaii shadow effect
    for offset in range(4, 0, -1):
        shadow_color = tuple(max(0, c - offset * 30) for c in bg_color)
        draw.text((position[0]+offset, position[1]+offset), text, fill=shadow_color, font=font_title)
    draw.text(position, text, fill=(255, 255, 255), font=font_title)
    
    # Subtitle with hearts
    subtitle = "💖 FLOPTROPICA 💖"
    try:
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font_sub = font_emoji
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    subtitle_width = bbox[2] - bbox[0]
    sub_position = ((width - subtitle_width) // 2, position[1] + 70)
    draw.text(sub_position, subtitle, fill=border_color, font=font_sub)
    
    img.save(filename)

def create_html_file():
    """Create the main HTML index file - ACCURATE FLOPTROPICA EDITION."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌺 The United Queendom of Floptropica 🌺</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Quicksand', 'Comic Sans MS', cursive, sans-serif;
            background: linear-gradient(-45deg, #FFB6C1, #FFD1DC, #E0BBE4, #D4A5A5, #FFDEE9, #FEC8D8);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .floating-emoji {
            position: fixed;
            font-size: 2em;
            opacity: 0.6;
            pointer-events: none;
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(10deg); }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 40px;
            box-shadow: 0 30px 80px rgba(255, 105, 180, 0.4);
            overflow: hidden;
            border: 6px solid #FFB6C1;
            position: relative;
        }

        .container::before {
            content: "🌸";
            position: absolute;
            top: 20px;
            left: 30px;
            font-size: 60px;
            z-index: 1;
            animation: pulse 2s ease infinite;
        }

        .container::after {
            content: "🦋";
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 60px;
            z-index: 1;
            animation: pulse 2s ease infinite 1s;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }

        header {
            background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 50%, #FF1493 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            position: relative;
            border-bottom: 5px solid #FF1493;
        }

        header h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);
            font-weight: 700;
            letter-spacing: 2px;
        }

        header .subtitle {
            font-size: 1.3em;
            opacity: 0.95;
            font-weight: 600;
            margin-bottom: 5px;
        }

        header .motto {
            font-size: 1.8em;
            font-weight: 700;
            margin-top: 15px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: 3px;
        }

        .info-banner {
            background: linear-gradient(135deg, #E0BBE4 0%, #D4A5A5 100%);
            padding: 20px;
            text-align: center;
            color: white;
            font-weight: 600;
            font-size: 1.1em;
        }

        .banner {
            width: 100%;
            padding: 40px;
            text-align: center;
            background: linear-gradient(to bottom, #FFF0F5 0%, #FFE4E1 100%);
            position: relative;
        }

        .banner img {
            max-width: 700px;
            width: 100%;
            height: auto;
            border-radius: 30px;
            box-shadow: 0 20px 50px rgba(255, 105, 180, 0.4);
            transition: transform 0.4s ease;
            border: 6px solid white;
        }

        .banner img:hover {
            transform: scale(1.05) rotate(-1deg);
        }

        .content {
            padding: 50px 40px;
            background: white;
        }

        .welcome-section {
            background: linear-gradient(135deg, #FFE4E1 0%, #FFF0F5 100%);
            padding: 30px;
            border-radius: 25px;
            margin-bottom: 40px;
            border: 3px solid #FFB6C1;
            text-align: center;
        }

        .welcome-section h2 {
            color: #FF1493;
            font-size: 2em;
            margin-bottom: 15px;
        }

        .welcome-section p {
            color: #8B4789;
            font-size: 1.1em;
            line-height: 1.8;
        }

        .section {
            margin-bottom: 50px;
        }

        .section h2 {
            color: #FF1493;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(255, 105, 180, 0.3);
            font-weight: 700;
            position: relative;
            padding-bottom: 15px;
        }

        .section h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 5px;
            background: linear-gradient(90deg, transparent, #FF69B4, transparent);
            border-radius: 10px;
        }

        .pdf-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .pdf-card {
            background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
            border-radius: 25px;
            padding: 30px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            border: 3px solid #FFB6C1;
            position: relative;
            overflow: hidden;
        }

        .pdf-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 105, 180, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s;
        }

        .pdf-card:hover::before {
            opacity: 1;
        }

        .pdf-card:hover {
            transform: translateY(-15px) rotate(-2deg) scale(1.05);
            box-shadow: 0 25px 50px rgba(255, 105, 180, 0.4);
            border-color: #FF1493;
        }

        .pdf-icon {
            font-size: 5em;
            margin-bottom: 20px;
            filter: drop-shadow(0 5px 10px rgba(255, 105, 180, 0.4));
            animation: iconBounce 2s ease infinite;
        }

        @keyframes iconBounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .pdf-card h3 {
            color: #FF1493;
            margin-bottom: 15px;
            font-size: 1.5em;
            font-weight: 700;
        }

        .pdf-card p {
            color: #8B4789;
            font-size: 1em;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        .pdf-card a {
            display: inline-block;
            background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
            color: white;
            padding: 14px 32px;
            border-radius: 30px;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 700;
            font-size: 1.05em;
            box-shadow: 0 8px 20px rgba(255, 105, 180, 0.4);
            position: relative;
            overflow: hidden;
        }

        .pdf-card a::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .pdf-card a:hover::before {
            width: 300px;
            height: 300px;
        }

        .pdf-card a:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 30px rgba(255, 105, 180, 0.6);
        }

        .directory-link {
            background: linear-gradient(135deg, #E0BBE4 0%, #D4A5A5 100%);
            padding: 30px;
            border-radius: 25px;
            margin-top: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.4s ease;
            border: 3px solid #D4A5A5;
            box-shadow: 0 5px 15px rgba(212, 165, 165, 0.3);
        }

        .directory-link:hover {
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 15px 35px rgba(212, 165, 165, 0.5);
            border-color: #BA55D3;
        }

        .directory-link span {
            font-size: 1.5em;
            color: white;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        .directory-link a {
            background: white;
            color: #BA55D3;
            padding: 14px 28px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .directory-link a:hover {
            background: #BA55D3;
            color: white;
            transform: scale(1.15);
            box-shadow: 0 8px 20px rgba(186, 85, 211, 0.4);
        }

        footer {
            background: linear-gradient(135deg, #8B4789 0%, #663399 100%);
            color: white;
            text-align: center;
            padding: 40px;
            font-size: 1em;
        }

        footer p {
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            margin: 8px 0;
            font-weight: 600;
        }

        .footer-emoji {
            font-size: 1.5em;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <!-- Floating emojis -->
    <div class="floating-emoji" style="top: 10%; left: 5%;">🌺</div>
    <div class="floating-emoji" style="top: 20%; right: 8%; animation-delay: 1s;">🦋</div>
    <div class="floating-emoji" style="top: 60%; left: 3%; animation-delay: 2s;">🌸</div>
    <div class="floating-emoji" style="bottom: 15%; right: 5%; animation-delay: 1.5s;">💖</div>
    <div class="floating-emoji" style="top: 40%; right: 10%; animation-delay: 0.5s;">✨</div>
    <div class="floating-emoji" style="bottom: 30%; left: 7%; animation-delay: 2.5s;">🌴</div>

    <div class="container">
        <header>
            <h1>🌺 The United Queendom of Floptropica 🌺</h1>
            <p class="subtitle">Official Archives & Tourist Information</p>
            <p class="motto">"AURGHHH" ✨</p>
        </header>

        <div class="info-banner">
            🏝️ Capital: Floptopia | Largest City: Jilu | Population: 2,500,000 | Languages: English, Spanish, Mandarin, Cantonese 🏝️
        </div>

        <div class="banner">
            <img src="floptropica_welcome.png" alt="Welcome to Floptropica">
        </div>

        <div class="content">
            <div class="welcome-section">
                <h2>🌴 Welcome to Paradise! 🌴</h2>
                <p>
                    The United Queendom of Floptropica is a tropical paradise in the Pacific Ocean, 
                    founded by the legendary Founding Mothers. Our beautiful islands are home to stunning 
                    beaches, lush rainforests, and a vibrant flop culture that welcomes everyone! 
                    Established in 1522, Floptropica has a rich history of resilience, fabulousness, 
                    and unwavering dedication to slay. Come visit Jiafei Plaza, relax at our luxury 
                    resorts, and experience the warm hospitality of our 2.5 million citizens! 💖
                </p>
            </div>

            <div class="section">
                <h2>👑 Government & Leadership 👑</h2>
                <div class="pdf-grid">
                    <div class="pdf-card">
                        <div class="pdf-icon">👸</div>
                        <h3>Queen Jiafei</h3>
                        <p>The beloved reigning monarch of Floptropica, descendant of the legendary Founding Mothers</p>
                        <a href="queen_jiafei.pdf">Royal Biography</a>
                    </div>

                    <div class="pdf-card">
                        <div class="pdf-icon">🏛️</div>
                        <h3>Prime Minister Deborah Ali-Williams</h3>
                        <p>Head of government and fearless leader who guided us through the Badussy Wars</p>
                        <a href="pm_deborah.pdf">Political Profile</a>
                    </div>

                    <div class="pdf-card">
                        <div class="pdf-icon">📜</div>
                        <h3>Floptropican Constitution</h3>
                        <p>The supreme law protecting Native Floptropicans and guaranteeing freedom for all</p>
                        <a href="constitution.pdf">Read Document</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎭 Cultural Icons 🎭</h2>
                <div class="pdf-grid">
                    <div class="pdf-card">
                        <div class="pdf-icon">💎</div>
                        <h3>CupcakKe</h3>
                        <p>Legendary poet and cultural icon whose work defines modern Floptropican art</p>
                        <a href="cupcakke_icon.pdf">Artist Profile</a>
                    </div>

                    <div class="pdf-card">
                        <div class="pdf-icon">👑</div>
                        <h3>Nicki Minaj</h3>
                        <p>Queen of Barbz Kingdom and fashion revolutionary from the Minajian migration</p>
                        <a href="nicki_minaj.pdf">Royal Archive</a>
                    </div>

                    <div class="pdf-card">
                        <div class="pdf-icon">🌟</div>
                        <h3>Celebrity Residents</h3>
                        <p>Learn about the A-list celebrities who call Floptropica home!</p>
                        <a href="celebrities.pdf">View All</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🗺️ Explore More 🗺️</h2>
                <div class="directory-link">
                    <span>⚔️ The Badussy Wars Archives</span>
                    <a href="badussy-war/">Explore History</a>
                </div>
                <div class="directory-link">
                    <span>🏛️ Government Documents</span>
                    <a href="government/">View Records</a>
                </div>
                <div class="directory-link">
                    <span>🏝️ Tourist Guide & Attractions</span>
                    <a href="tourist-guide/">Plan Your Visit</a>
                </div>
            </div>
        </div>

        <footer>
            <p class="footer-emoji">🌺 ✨ 💖 🦋 🌸 💕 🌴 🌊</p>
            <p>The United Queendom of Floptropica and Other Governed Territories</p>
            <p>Est. 1522 by the Founding Mothers | Native Floptropicans since 2200 BCE</p>
            <p>Official Motto: "AURGHHH" | Capital: Floptopia | Largest City: Jilu</p>
            <p class="footer-emoji">🌺 ✨ 💖 🦋 🌸 💕 🌴 🌊</p>
        </footer>
    </div>

    <script>
        // Create floating hearts
        setInterval(() => {
            const emojis = ['💖', '✨', '🌸', '🦋', '💕', '🌺'];
            const heart = document.createElement('div');
            heart.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            heart.style.position = 'fixed';
            heart.style.left = Math.random() * window.innerWidth + 'px';
            heart.style.top = window.innerHeight + 'px';
            heart.style.fontSize = (Math.random() * 20 + 25) + 'px';
            heart.style.opacity = '0.7';
            heart.style.pointerEvents = 'none';
            heart.style.transition = 'all 4s ease-out';
            heart.style.zIndex = '1000';
            document.body.appendChild(heart);
            
            setTimeout(() => {
                heart.style.top = '-100px';
                heart.style.opacity = '0';
            }, 100);
            
            setTimeout(() => heart.remove(), 4100);
        }, 800);
    </script>
</body>
</html>"""
    
    with open('content/index.html', 'w') as f:
        f.write(html_content)
    print("✓ HTML file created")

def create_all_content():
    """Create all sample content - ACCURATE FLOPTROPICA EDITION."""
    print("🌺 Creating Official Floptropica Archives...\n")
    
    # Create directories
    create_directories()
    
    # Create HTML file
    create_html_file()
    
    # Create main images
    print("\n✨ Creating images...")
    create_flop_image('content/floptropica_welcome.png', 'FLOPTROPICA', 800, 400, "pink")
    print("✓ floptropica_welcome.png created")
    
    # Create PDFs in main directory
    print("\n👑 Creating government documents...")
    
    create_flop_pdf(
        'content/queen_jiafei.pdf',
        '👑 QUEEN JIAFEI',
        [
            '### Her Majesty Queen Jiafei of Floptropica',
            '',
            'Queen Jiafei is the beloved reigning monarch of The United',
            'Queendom of Floptropica, descended from the legendary',
            'Founding Mothers who established our nation in 1522.',
            '',
            '### Royal Lineage:',
            '• Direct descendant of the Founding Mothers',
            '• Coronated in a magnificent ceremony in Floptopia',
            '• Resides in the Royal Palace in the capital',
            '• Beloved by all 2.5 million Floptropican citizens',
            '',
            '### Reign Achievements:',
            '• Modernized Floptropica while honoring traditions',
            '• Strengthened ties with ally nations',
            '• Promoted tourism and economic growth',
            '• Protected Native Floptropican rights',
            '• Led cultural renaissance',
            '',
            '### The Royal Family:',
            'Queen Jiafei leads the constitutional monarchy,',
            'working alongside Prime Minister Deborah Ali-Williams',
            'to ensure prosperity for all Floptropicans.',
            '',
            '### Royal Duties:',
            '• State ceremonies and diplomatic visits',
            '• Patron of the arts and culture',
            '• Guardian of Floptropican heritage',
            '• Symbol of national unity',
            '',
            '### Famous Quote:',
            '"Every Floptropican deserves to live fabulously',
            'in peace and prosperity. AURGHHH!" - Queen Jiafei',
        ],
        "Reigning Monarch of Floptropica"
    )
    print("✓ queen_jiafei.pdf created")
    
    create_flop_pdf(
        'content/pm_deborah.pdf',
        '🏛️ PM DEBORAH ALI-WILLIAMS',
        [
            '### Prime Minister Deborah Ali-Williams',
            '',
            'The Honorable Deborah Ali-Williams serves as Prime',
            'Minister of Floptropica, leading the government with',
            'courage, wisdom, and unwavering dedication.',
            '',
            '### Political Career:',
            '• Elected Prime Minister by popular vote',
            '• Leader of the Floptropican Parliament',
            '• Former Minister of Defense',
            '• War hero from the Badussy Wars',
            '',
            '### The Badussy Wars Leadership:',
            'PM Deborah led Floptropica through the devastating',
            'Badussy Wars (2022-2023) against Badussyland, Da Boyz',
            'Republic, and Scamland. Her strategic brilliance and',
            'fierce determination secured victory for our nation.',
            '',
            '### Major Accomplishments:',
            '• Victory in the Badussy Wars',
            '• Economic recovery programs',
            '• Infrastructure modernization',
            '• Healthcare expansion',
            '• Education reform',
            '• Environmental protection initiatives',
            '',
            '### Government Structure:',
            'Works with Queen Jiafei in constitutional monarchy.',
            'Leads Cabinet and Parliament in Floptopia.',
            '',
            '### Famous Speeches:',
            '"We will defend Floptropica against all threats!"',
            '"Our diversity is our strength - Native Floptropicans,',
            'immigrants, and all citizens united as one!"',
            '',
            '### Vision for Floptropica:',
            'A prosperous, peaceful nation that welcomes all',
            'while protecting its unique culture and values.',
        ],
        "Head of Government"
    )
    print("✓ pm_deborah.pdf created")
    
    create_flop_pdf(
        'content/constitution.pdf',
        '📜 FLOPTROPICAN CONSTITUTION',
        [
            '### The Constitution of Floptropica',
            '',
            'We, the people of Floptropica, in order to form',
            'a more perfect union, establish justice, ensure',
            'domestic tranquility, and secure the blessings',
            'of liberty, do ordain this Constitution.',
            '',
            '### Article I: Native Rights',
            '• Protection of Native Floptropican peoples',
            '• Recognition of indigenous culture and lands',
            '• Preservation of traditional heritage',
            '• Rights dating back to 2200 BCE settlements',
            '',
            '### Article II: Universal Rights',
            '• Freedom of expression and identity',
            '• Right to live authentically',
            '• Protection from discrimination',
            '• Equal treatment under law',
            '• Religious and cultural freedom',
            '',
            '### Article III: Government',
            '• Constitutional monarchy with Queen as head of state',
            '• Parliamentary democracy with elected officials',
            '• Independent judiciary',
            '• Separation of powers',
            '',
            '### Article IV: Immigration',
            '• Welcome to all who respect our values',
            '• Path to citizenship for immigrants',
            '• Multicultural society (English, Spanish, Mandarin, Cantonese)',
            '• Integration while preserving heritage',
            '',
            '### Article V: The National Motto',
            'Official motto: "AURGHHH"',
            'Symbolizing strength, unity, and fabulousness',
        ],
        "Supreme Law of the Land"
    )
    print("✓ constitution.pdf created")
    
    create_flop_pdf(
        'content/cupcakke_icon.pdf',
        '💎 CUPCAKKE',
        [
            '### CupcakKe: Cultural Icon',
            '',
            'CupcakKe is one of Floptropica\'s most celebrated',
            'artists, known for bold expression and revolutionary',
            'artistic contributions that defined modern culture.',
            '',
            '### Artistic Legacy:',
            '• Pioneer of authentic self-expression',
            '• Fearless lyricist and poet',
            '• Cultural ambassador worldwide',
            '• Inspiration to millions',
            '',
            '### Contributions to Floptropican Culture:',
            '• Redefined artistic boundaries',
            '• Championed body positivity',
            '• Promoted sexual liberation',
            '• Advocated for LGBTQ+ rights',
            '• Broke taboos through art',
            '',
            '### Famous Works:',
            '• "Deepthroat" - Cultural phenomenon',
            '• "Duck Duck Goose" - Viral sensation',
            '• "Squidward Nose" - Comedy masterpiece',
            '• "Spoiled Milk Titties" - Avant-garde art',
            '',
            '### Awards and Recognition:',
            '• Floptropican Medal of Arts',
            '• Cultural Heritage Award',
            '• Lifetime Achievement Honor',
            '• People\'s Choice Icon',
            '',
            '### Impact Statement:',
            'CupcakKe\'s fearless artistry inspired an entire',
            'generation to be unapologetically themselves.',
            'Her influence on Floptropican culture is immeasurable.',
            '',
            '### Quote:',
            '"Be yourself, always. The world needs your authentic',
            'voice." - CupcakKe',
        ],
        "Legendary Poet & Artist"
    )
    print("✓ cupcakke_icon.pdf created")
    
    create_flop_pdf(
        'content/nicki_minaj.pdf',
        '👑 NICKI MINAJ',
        [
            '### Nicki Minaj: Queen of Barbz',
            '',
            'Nicki Minaj, the Harajuku Barbie, arrived in Floptropica',
            'during the Minajian Migration and became a beloved',
            'cultural icon and fashion revolutionary.',
            '',
            '### Background:',
            '• Born Onika Tanya Maraj-Petty',
            '• Arrived during Minajian Migration wave',
            '• Established Barbz Kingdom within Floptropica',
            '• Royal status granted by Queen Jiafei',
            '',
            '### The Barbz Kingdom:',
            'Nicki established the Barbz Kingdom as a cultural',
            'region within Floptropica, welcoming her millions',
            'of followers (Barbz) to celebrate pink, wigs, and fabulousness.',
            '',
            '### Fashion Revolution:',
            '• Pioneered the "Barbie" aesthetic',
            '• Made wigs mainstream fashion',
            '• Colorful, bold style influence',
            '• Fashion icon for generations',
            '',
            '### Cultural Contributions:',
            '• Music that empowers women',
            '• LGBTQ+ advocacy and allyship',
            '• Business woman role model',
            '• Philanthropy and education support',
            '',
            '### Famous Quotes:',
            '"I\'m not a businessman, I\'m a business, woman!"',
            '"You could be the king but watch the queen conquer!"',
            '',
            '### Legacy in Floptropica:',
            'Nicki\'s influence transformed Floptropican fashion',
            'and inspired countless citizens to embrace their',
            'unique style and personality.',
        ],
        "Fashion Icon & Barbz Queen"
    )
    print("✓ nicki_minaj.pdf created")
    
    create_flop_pdf(
        'content/celebrities.pdf',
        '🌟 CELEBRITY RESIDENTS',
        [
            '### Famous Floptropicans',
            '',
            'Floptropica is home to many A-list celebrities who',
            'chose our tropical paradise as their residence!',
            '',
            '### Music Icons:',
            '',
            '### Cardi B',
            '• Arrived from the Bronx',
            '• Cultural ambassador',
            '• "Okurrr" became national catchphrase',
            '• Owns luxury villa in Jilu',
            '',
            '### Doja Cat',
            '• Planet Her themed estate',
            '• Innovation in music and fashion',
            '• Advocate for creative freedom',
            '',
            '### Megan Thee Stallion',
            '• Hot Girl Summer ambassador',
            '• Education advocate',
            '• Empowerment icon',
            '',
            '### Lil Nas X',
            '• LGBTQ+ rights champion',
            '• Montero Mountain property owner',
            '• Social media innovator',
            '',
            '### Ice Spice',
            '• Y2K revival leader',
            '• Bronx to Floptropica bridge',
            '• Youth culture icon',
            '',
            '### International Stars:',
            '',
            '### Lady Gaga',
            '• Born This Way Foundation headquarters',
            '• LGBTQ+ icon',
            '• Art and fashion innovator',
            '',
            '### Ariana Grande',
            '• Sweetener residence',
            '• Pop princess of Floptropica',
            '',
            '### And Many More!',
            'Floptropica attracts celebrities who value',
            'freedom, creativity, and fabulousness!',
        ],
        "Who\'s Who in Floptropica"
    )
    print("✓ celebrities.pdf created")
    
    # Create PDFs in badussy-war subdirectory
    print("\n⚔️ Creating Badussy Wars archives...")
    
    create_flop_pdf(
        'content/badussy-war/war_history.pdf',
        '⚔️ THE BADUSSY WARS',
        [
            '### The Badussy Wars (2022-2023)',
            '',
            'The Badussy Wars were a series of devastating conflicts',
            'that threatened Floptropica\'s very existence. Through',
            'courage and unity, we emerged victorious.',
            '',
            '### The Enemy Alliance:',
            '• Badussyland - Aggressive neighbor nation',
            '• Da Boyz Republic - Misogynistic regime',
            '• Scamland - Deceptive territory',
            '',
            '### Causes of War:',
            '• Territorial disputes',
            '• Cultural differences',
            '• Economic competition',
            '• Ideological conflicts',
            '• Threats to Floptropican sovereignty',
            '',
            '### Timeline of Events:',
            '',
            '### 2022: War Begins',
            '• Badussyland invades northern territories',
            '• PM Deborah declares state of emergency',
            '• Military mobilization',
            '• International condemnation of aggressors',
            '',
            '### 2022-2023: Major Battles',
            '• Battle of Floptopia - Defense of capital',
            '• Siege of Jilu - 60-day standoff',
            '• Operation Pink Thunder - Counter-offensive',
            '• Liberation campaigns',
            '',
            '### 2023: Victory',
            '• Decisive Floptropican victories',
            '• Enemy forces retreat',
            '• Peace negotiations begin',
            '• Treaty signed in Floptopia',
            '',
            '### Casualties and Impact:',
            'Thousands of brave soldiers defended our nation.',
            'We honor their sacrifice and remember the cost of freedom.',
        ],
        "A Nation\'s Greatest Trial"
    )
    print("✓ badussy-war/war_history.pdf created")
    
    create_flop_pdf(
        'content/badussy-war/heroes.pdf',
        '🎖️ WAR HEROES',
        [
            '### Heroes of the Badussy Wars',
            '',
            'These brave Floptropicans defended our nation',
            'with courage, sacrifice, and unwavering dedication.',
            '',
            '### Military Leadership:',
            '',
            '### Prime Minister Deborah Ali-Williams',
            '• Supreme Commander of Armed Forces',
            '• Strategic mastermind',
            '• Inspired the nation through darkest hours',
            '• Led us to victory',
            '',
            '### General Jiafei',
            '• Commander of Ground Forces',
            '• Brilliant tactical leader',
            '• Hero of the Battle of Floptopia',
            '',
            '### Admiral CupcakKe',
            '• Naval Forces Commander',
            '• Secured maritime borders',
            '• Protected supply lines',
            '',
            '### Air Marshal Nicki',
            '• Air Force Commander',
            '• Achieved air superiority',
            '• Key to final victory',
            '',
            '### Notable Heroes:',
            '',
            '### Sergeant Trish Paytas',
            '• Special Forces operative',
            '• Conducted daring rescue missions',
            '• Decorated for bravery',
            '',
            '### Captain Cardi B',
            '• Infantry commander',
            '• Led troops with fierce determination',
            '• Never backed down',
            '',
            '### The Civilian Heroes:',
            'Countless civilians supported the war effort:',
            '• Medical personnel',
            '• Supply coordinators',
            '• Communications specialists',
            '• Home front organizers',
            '',
            '### Remembrance:',
            'We will never forget their sacrifice.',
            'Freedom was not free.',
        ],
        "Honoring the Brave"
    )
    print("✓ badussy-war/heroes.pdf created")
    
    create_flop_pdf(
        'content/badussy-war/peace_treaty.pdf',
        '🕊️ PEACE TREATY',
        [
            '### Treaty of Floptopia',
            '',
            'The Treaty of Floptopia officially ended the Badussy',
            'Wars and established lasting peace in the region.',
            '',
            '### Signing Date: December 2023',
            'Location: Royal Palace, Floptopia',
            '',
            '### Key Terms:',
            '',
            '### Article I: Cessation of Hostilities',
            '• Immediate ceasefire',
            '• Withdrawal of all forces',
            '• Demilitarized zones established',
            '• No future aggression',
            '',
            '### Article II: Recognition',
            '• Full recognition of Floptropican sovereignty',
            '• Respect for territorial integrity',
            '• Protection of Native Floptropican rights',
            '• Cultural autonomy guaranteed',
            '',
            '### Article III: Reparations',
            '• Compensation for war damages',
            '• Rebuilding assistance',
            '• Return of stolen cultural artifacts',
            '• Repatriation of prisoners',
            '',
            '### Article IV: Reconciliation',
            '• Truth and reconciliation commission',
            '• War crimes tribunals',
            '• Memorials for victims',
            '• Education programs',
            '',
            '### Article V: Future Relations',
            '• Diplomatic normalization',
            '• Trade agreements',
            '• Cultural exchanges',
            '• Peaceful coexistence',
            '',
            '### Signatories:',
            'Prime Minister Deborah Ali-Williams - Floptropica',
            'Representatives of former enemy nations',
            'International mediators',
            '',
            '### Legacy:',
            'This treaty ensures Floptropica\'s peace and',
            'security for generations to come.',
        ],
        "Foundation for Peace"
    )
    print("✓ badussy-war/peace_treaty.pdf created")
    
    create_flop_image('content/badussy-war/memorial.png', 'IN REMEMBRANCE', 600, 400, "purple")
    print("✓ badussy-war/memorial.png created")
    
    # Create content in government subdirectory
    print("\n🏛️ Creating government documents...")
    
    create_flop_pdf(
        'content/government/parliament.pdf',
        '🏛️ FLOPTROPICAN PARLIAMENT',
        [
            '### The Parliament of Floptropica',
            '',
            'The Floptropican Parliament is the legislative body',
            'that creates laws and represents the people.',
            '',
            '### Structure:',
            '',
            '### House of Representatives',
            '• 150 elected members',
            '• Represents districts across Floptropica',
            '• 4-year terms',
            '• Passes legislation',
            '',
            '### Senate',
            '• 50 senators',
            '• Represents territories and regions',
            '• 6-year terms',
            '• Reviews and approves laws',
            '',
            '### Leadership:',
            '• Prime Minister Deborah Ali-Williams',
            '• Speaker of the House',
            '• Senate Majority Leader',
            '• Cabinet Ministers',
            '',
            '### Key Ministries:',
            '• Ministry of Defense',
            '• Ministry of Culture',
            '• Ministry of Tourism',
            '• Ministry of Health',
            '• Ministry of Education',
            '• Ministry of Foreign Affairs',
            '',
            '### Legislative Process:',
            '1. Bill introduction',
            '2. Committee review',
            '3. House debate and vote',
            '4. Senate review and vote',
            '5. Royal assent from Queen Jiafei',
            '6. Law implementation',
            '',
            '### Recent Major Legislation:',
            '• Native Rights Protection Act',
            '• Universal Healthcare Expansion',
            '• Education Reform Bill',
            '• Environmental Protection Act',
            '• Tourism Development Initiative',
        ],
        "The People\'s Voice"
    )
    print("✓ government/parliament.pdf created")
    
    create_flop_pdf(
        'content/government/economy.pdf',
        '💰 FLOPTROPICAN ECONOMY',
        [
            '### Economic Profile of Floptropica',
            '',
            '### Overview:',
            'Floptropica has a thriving mixed economy based on',
            'tourism, agriculture, fishing, and creative industries.',
            '',
            '### Key Economic Sectors:',
            '',
            '### Tourism (40% of GDP)',
            '• Luxury beach resorts',
            '• Cultural attractions',
            '• Eco-tourism',
            '• Annual visitors: 5 million',
            '',
            '### Agriculture (20% of GDP)',
            '• Tropical fruits export',
            '• Coffee and cocoa',
            '• Sustainable farming',
            '• Organic products',
            '',
            '### Fishing Industry (15% of GDP)',
            '• Sustainable fishing practices',
            '• Seafood export',
            '• Aquaculture',
            '',
            '### Creative Industries (15% of GDP)',
            '• Music and arts',
            '• Fashion design',
            '• Film and media production',
            '• Digital content creation',
            '',
            '### Other Sectors (10% of GDP)',
            '• Technology',
            '• Financial services',
            '• Manufacturing',
            '• Renewable energy',
            '',
            '### Currency:',
            'Floptropican Dollar (FTD)',
            'Stable and strong currency',
            '',
            '### Trade Partners:',
            '• United States',
            '• Canada',
            '• European Union',
            '• Asian markets',
            '',
            '### Economic Indicators:',
            '• GDP: $85 billion',
            '• Per capita income: $34,000',
            '• Unemployment: 4.2%',
            '• Growth rate: 5.8% annually',
        ],
        "Prosperity for All"
    )
    print("✓ government/economy.pdf created")
    
    create_flop_image('content/government/parliament_building.png', 'PARLIAMENT', 700, 400, "blue")
    print("✓ government/parliament_building.png created")
    
    # Create tourist guide content
    print("\n🏝️ Creating tourist guides...")
    
    create_flop_pdf(
        'content/tourist-guide/attractions.pdf',
        '🏝️ TOP ATTRACTIONS',
        [
            '### Must-See Destinations in Floptropica!',
            '',
            '### 🌴 Floptopia - The Capital',
            '• Royal Palace tours',
            '• Jiafei Plaza shopping district',
            '• National Museum of Floptropican History',
            '• Government buildings',
            '• Vibrant nightlife',
            '',
            '### 🏙️ Jilu - Largest City',
            '• Modern skyline',
            '• Beach boardwalk',
            '• Fashion district',
            '• Entertainment venues',
            '• Culinary scene',
            '',
            '### 🏖️ Paradise Beaches',
            '• Crystal clear waters',
            '• White sand beaches',
            '• Water sports',
            '• Luxury beach resorts',
            '• Sunset viewing spots',
            '',
            '### 🌺 Cultural Sites',
            '• Native Floptropican heritage sites',
            '• Traditional villages',
            '• Ancient temples (dating to 2200 BCE)',
            '• Cultural festivals',
            '• Art galleries',
            '',
            '### 🌳 Natural Wonders',
            '• Tropical rainforest reserves',
            '• Volcano hiking trails',
            '• Waterfalls',
            '• Wildlife sanctuaries',
            '• Coral reefs for diving',
            '',
            '### 🎭 Entertainment',
            '• CupcakKe Cultural Center',
            '• Nicki Minaj Fashion Museum',
            '• Live music venues',
            '• Theater district',
            '• Night clubs',
            '',
            '### 🍽️ Dining',
            'Experience fusion of Native Floptropican cuisine',
            'with international flavors!',
        ],
        "Your Vacation Guide"
    )
    print("✓ tourist-guide/attractions.pdf created")
    
    create_flop_pdf(
        'content/tourist-guide/visitor_info.pdf',
        '✈️ VISITOR INFORMATION',
        [
            '### Planning Your Trip to Floptropica',
            '',
            '### 🛂 Visa Requirements:',
            '• Tourist visa: Valid for 90 days',
            '• Available on arrival for most countries',
            '• Online e-visa application',
            '• Passport valid for 6 months',
            '',
            '### ✈️ Getting There:',
            '• Floptopia International Airport (FIA)',
            '• Jilu International Airport (JIA)',
            '• Direct flights from major cities worldwide',
            '• Cruise ship ports',
            '',
            '### 🏨 Accommodation:',
            '• 5-star luxury resorts',
            '• Boutique hotels',
            '• Budget-friendly hostels',
            '• Vacation rentals',
            '• All-inclusive packages',
            '',
            '### 💱 Money Matters:',
            '• Currency: Floptropican Dollar (FTD)',
            '• Credit cards widely accepted',
            '• ATMs available everywhere',
            '• Tipping: 10-15% customary',
            '',
            '### 🗣️ Languages:',
            '• English (primary)',
            '• Spanish',
            '• Mandarin',
            '• Cantonese',
            '• Most people multilingual',
            '',
            '### 🌡️ Climate:',
            '• Tropical year-round',
            '• Average temp: 78-88°F (26-31°C)',
            '• Dry season: November-April',
            '• Rainy season: May-October',
            '',
            '### 🚗 Transportation:',
            '• Modern public transit',
            '• Taxis and ride-sharing',
            '• Car rentals available',
            '• Inter-island ferries',
            '• Bike-friendly cities',
            '',
            '### 📱 Stay Connected:',
            '• Free WiFi widely available',
            '• Tourist SIM cards at airport',
            '• 5G coverage in cities',
        ],
        "Everything You Need to Know"
    )
    print("✓ tourist-guide/visitor_info.pdf created")
    
    create_flop_image('content/tourist-guide/beach_paradise.png', 'PARADISE', 800, 500, "blue")
    print("✓ tourist-guide/beach_paradise.png created")
    
    print("\n" + "="*50)
    print("🌺 ✨ Official Floptropica Archives Complete! ✨ 🌺")
    print("="*50)
    print("\nContent structure:")
    print("content/")
    print("  ├── index.html")
    print("  ├── floptropica_welcome.png")
    print("  ├── queen_jiafei.pdf")
    print("  ├── pm_deborah.pdf")
    print("  ├── constitution.pdf")
    print("  ├── cupcakke_icon.pdf")
    print("  ├── nicki_minaj.pdf")
    print("  ├── celebrities.pdf")
    print("  ├── badussy-war/")
    print("  │   ├── war_history.pdf")
    print("  │   ├── heroes.pdf")
    print("  │   ├── peace_treaty.pdf")
    print("  │   └── memorial.png")
    print("  ├── government/")
    print("  │   ├── parliament.pdf")
    print("  │   ├── economy.pdf")
    print("  │   └── parliament_building.png")
    print("  └── tourist-guide/")
    print("      ├── attractions.pdf")
    print("      ├── visitor_info.pdf")
    print("      └── beach_paradise.png")
    print("\n💖 AURGHHH! The archives are ready! 💖")
    print("🌺 Welcome to The United Queendom of Floptropica! 🌺")

if __name__ == "__main__":
    create_all_content()