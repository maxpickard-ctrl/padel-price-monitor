#!/usr/bin/env python3
"""Padel Outlet Price Monitor - Cloud Version"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

PADELOUTLET_URL = "https://www.padeloutlet.ae"
ALERT_EMAIL = "gm@padelart.ae"

COMPETITORS = {
    "amazon_ae": "https://www.amazon.ae/s?k=",
    "noon": "https://www.noon.com/uae/en/search?q=",
    "padelsouq": "https://www.padelsouq.com/search?q=",
    "padel4less": "https://www.padel4less.ae/search?q=",
    "racketshop": "https://www.racketshop.ae/search?q=",
    "elpadel": "https://www.elpadel.ae/search?q=",
    "urbanfitnesscart": "https://www.urbanfitnesscart.com/search?q=",
}

def scrape_padeloutlet():
    """Get products from your website"""
    print("🔍 Scraping Padel Outlet...")
    try:
        response = requests.get(PADELOUTLET_URL, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        products = {}
        
        product_elements = soup.find_all('div', class_=['product', 'item'])
        
        for elem in product_elements[:30]:
            try:
                name_elem = elem.find(['h2', 'h3', 'span'], class_=['name', 'title', 'product-name'])
                price_elem = elem.find(['span', 'div'], class_=['price', 'product-price'])
                
                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    price_text = price_elem.text.strip().replace('AED', '').replace(',', '').strip()
                    try:
                        price = float(price_text.split()[0])
                        products[name] = price
                    except:
                        pass
            except:
                pass
        
        print(f"✅ Found {len(products)} products")
        return products
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def search_competitor(product_name, competitor_url):
    """Search for product on competitor"""
    try:
        search_url = f"{competitor_url}{product_name.replace(' ', '+')}"
        response = requests.get(search_url, timeout=10)
        prices = []
        
        if 'AED' in response.text:
            soup = BeautifulSoup(response.text, 'html.parser')
            for text in soup.stripped_strings:
                if 'AED' in text and any(char.isdigit() for char in text):
                    try:
                        price_str = text.replace('AED', '').replace(',', '').split()[0]
                        price = float(price_str)
                        if 50 < price < 2000:
                            prices.append(price)
                    except:
                        pass
        
        return min(prices) if prices else None
    except:
        return None

def send_email(smtp_user, smtp_password, alerts):
    """Send alert email"""
    if not alerts:
        print("ℹ️  No undercuts found")
        return
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"🏓 Padel Outlet Price Alert - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = smtp_user
        msg['To'] = ALERT_EMAIL
        
        html = f"""<html><body style='font-family: Arial; max-width: 800px;'>
            <div style='background: #1a1a2e; color: white; padding: 20px; border-radius: 10px;'>
                <h1>🏓 Padel Outlet Price Alert</h1>
                <p>Found <strong>{len(alerts)}</strong> price undercuts!</p>
            </div>
            
            <table style='border-collapse: collapse; width: 100%; margin-top: 20px;'>
            <tr style='background: #333; color: white;'>
                <th style='border: 1px solid #ddd; padding: 12px; text-align: left;'>Product</th>
                <th style='border: 1px solid #ddd; padding: 12px; text-align: left;'>Your Price</th>
                <th style='border: 1px solid #ddd; padding: 12px; text-align: left;'>Competitor</th>
                <th style='border: 1px solid #ddd; padding: 12px; text-align: left;'>Their Price</th>
                <th style='border: 1px solid #ddd; padding: 12px; text-align: left;'>Difference</th>
            </tr>
        """
        
        for alert in sorted(alerts, key=lambda x: x['difference'], reverse=True):
            html += f"""
            <tr style='background: #ffe6e6;'>
                <td style='border: 1px solid #ddd; padding: 12px;'>{alert['product']}</td>
                <td style='border: 1px solid #ddd; padding: 12px;'>AED {alert['outlet_price']:.2f}</td>
                <td style='border: 1px solid #ddd; padding: 12px;'>{alert['competitor']}</td>
                <td style='border: 1px solid #ddd; padding: 12px; color: red; font-weight: bold;'>AED {alert['comp_price']:.2f}</td>
                <td style='border: 1px solid #ddd; padding: 12px; color: red; font-weight: bold;'>-AED {alert['difference']:.2f}</td>
            </tr>
            """
        
        html += """</table>
            <p style='margin-top: 30px; color: #666; font-size: 12px;'>
                <em>Automatic report from Padel Outlet Price Monitor</em>
            </p>
        </body></html>"""
        
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {ALERT_EMAIL}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def run_check(smtp_user, smtp_password):
    """Main function"""
    print(f"\n{'='*60}")
    print(f"📊 PADEL OUTLET PRICE CHECK")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Get your products
    products = scrape_padeloutlet()
    if not products:
        print("❌ No products found")
        return
    
    # Check competitors
    alerts = []
    for i, (product_name, outlet_price) in enumerate(list(products.items())[:15], 1):
        print(f"[{i}] Checking: {product_name} (AED {outlet_price})")
        
        for comp_name, comp_url in COMPETITORS.items():
            comp_price = search_competitor(product_name, comp_url)
            
            if comp_price and comp_price < outlet_price:
                difference = outlet_price - comp_price
                percent = (difference / outlet_price) * 100
                alerts.append({
                    'product': product_name,
                    'outlet_price': outlet_price,
                    'competitor': comp_name.replace('_', ' ').title(),
                    'comp_price': comp_price,
                    'difference': difference
                })
                print(f"    ⚠️  {comp_name.upper()}: AED {comp_price} (-AED {difference:.2f} / -{percent:.1f}%)")
            
            time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"📈 Results: {len(alerts)} undercuts found")
    print(f"{'='*60}\n")
    
    send_email(smtp_user, smtp_password, alerts)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 deploy_price_monitor.py <gmail> <app_password>")
        sys.exit(1)
    run_check(sys.argv[1], sys.argv[2])
