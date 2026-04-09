import subprocess
from playwright.sync_api import sync_playwright

# --- 1. THE LAUNCHER ---
def start_jarvis_browser():
    """Launches Chrome with a remote control port open so Jarvis can connect to it later."""
    try:
        # We give Jarvis his own browser profile so it doesn't clash with your normal Chrome tabs
        subprocess.Popen([
            r"C:\Program Files\Google\Chrome\Application\chrome.exe", 
            "--remote-debugging-port=9222", 
            r"--user-data-dir=C:\JarvisProfile"
        ])
        return "Jarvis Browser successfully launched and listening for commands."
    except Exception as e:
        return f"Failed to launch browser. Ensure Chrome is installed in the default location. Error: {e}"

# --- 2. THE GHOST TYPIST ---
def search_youtube_active(query: str):
    """Connects to the already-open Jarvis browser, finds YouTube, and ghost-types the query."""
    try:
        # AI hallucination catch
        if isinstance(query, dict):
            query = query.get('query', query.get('value', str(query)))
            
        with sync_playwright() as p:
            # 1. Connect to the open browser using the listening port
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # 2. Grab the currently active tab
            context = browser.contexts[0]
            page = context.pages[0] 
            
            # 3. If the tab isn't on YouTube, go there first
            if "youtube.com" not in page.url:
                page.goto("https://www.youtube.com")
            
            # 4. Wait for the search bar to load
            page.wait_for_selector('input#search')
            
            # 5. Clear the bar and Ghost Type the new query (100ms delay per letter)
            page.fill('input#search', "") 
            page.type('input#search', query, delay=100)
            
            # 6. Hit Enter
            page.keyboard.press('Enter')
            
            # 7. Disconnect smoothly without closing the browser
            browser.disconnect()
            
            return f"Successfully typed '{query}' into YouTube and searched."
            
    except Exception as e:
        return f"Failed to connect. Make sure you asked me to 'open the browser' first. Error: {e}"