import os
import re
import pytesseract
from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from scraper_app.models import Provider, Game

class Command(BaseCommand):
    help = 'Runs the Playwright scraper to fetch providers and games.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Python Playwright Scraper..."))
        
        target_url = 'https://myvepower.com/'
        
        with sync_playwright() as p:
            self.stdout.write(self.style.WARNING("Launching browser in visible mode for manual login..."))
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            
            page.goto(target_url, wait_until='networkidle')
            
            self.stdout.write(self.style.ERROR("\n======================================================"))
            self.stdout.write(self.style.ERROR("[MANUAL LOGIN REQUIRED]"))
            self.stdout.write("1. Look at the opened browser window.")
            self.stdout.write("2. Log in to your myvepower.com account.")
            self.stdout.write("3. Wait until you are on the main dashboard.")
            self.stdout.write(self.style.ERROR("======================================================\n"))
            
            input('Type "ok" and press Enter when you are logged in: ')
            
            self.stdout.write(self.style.SUCCESS("[LOGIN] Proceeding with scraping..."))
            
            # Broadened selectors to catch typical React SPA game grids
            # We look for common class name patterns since we don't have the exact ones
            provider_selector = '.dash-side-item, nav a, .provider-tab, h2'
            game_selector = '.game-card, .rbw-card, img[src*="game"], .thumbnail'
            
            providers = page.locator(provider_selector).all()
            
            if not providers:
                self.stdout.write(self.style.WARNING("Could not find provider tabs. Attempting to scan the entire page for games..."))
                
                # Create a generic provider for the found games
                provider_obj, _ = Provider.objects.get_or_create(name="Myvepower Main Grid")
                
                # Look for anything that looks like a game thumbnail
                games = page.locator('img').all()
                for g_idx, game_el in enumerate(games):
                    src = game_el.get_attribute('src')
                    if src and ('game' in src.lower() or 'webp' in src.lower()):
                        game_name = game_el.get_attribute('alt') or f"Found Game {g_idx+1}"
                        thumb_file = src.split('/')[-1] if src else f"game_{g_idx}.png"
                        
                        ocr_text = "N/A"
                        try:
                            # Try to click the parent link or container
                            game_el.locator('..').click(timeout=3000)
                            page.wait_for_timeout(2000)
                            page.go_back()
                        except:
                            pass # If unclickable, just skip OCR
                        
                        Game.objects.update_or_create(
                            provider=provider_obj, 
                            name=game_name,
                            defaults={'thumbnail': thumb_file, 'ocr_stats': ocr_text}
                        )
                        self.stdout.write(f"  -> Saved {game_name}")
            else:
                for idx, provider_el in enumerate(providers):
                    provider_name_raw = provider_el.inner_text()
                    provider_name = provider_name_raw.strip() if provider_name_raw else f"Provider_{idx+1}"
                    
                    self.stdout.write(f"\n[PROVIDER] Processing: {provider_name}")
                    provider_obj, _ = Provider.objects.get_or_create(name=provider_name)
                    
                    provider_el.click()
                    page.wait_for_timeout(2000)
                    
                    games = page.locator(game_selector).all()
                    
                    for g_idx, game_el in enumerate(games):
                        game_name = game_el.get_attribute('data-name') or f"Game_{g_idx+1}"
                        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', game_name)
                        safe_prov = re.sub(r'[^a-zA-Z0-9]', '_', provider_name)
                        
                        thumb_file = f"{safe_prov}_{safe_name}.png"
                        
                        # We will skip actual screenshots in this test script to prevent clutter
                        # In production, you would save it to a media directory.
                        # game_el.screenshot(path=f"media/{thumb_file}")
                        
                        ocr_text = "N/A"
                        try:
                            # Simulated click and OCR for stability
                            game_el.click()
                            page.wait_for_timeout(2000)
                            # page.screenshot(path="temp.png")
                            # ocr_text = pytesseract.image_to_string("temp.png").replace('\n', ' ').strip()
                            page.go_back()
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Failed to process {game_name}: {e}"))
                        
                        # Save to database
                        Game.objects.update_or_create(
                            provider=provider_obj, 
                            name=game_name,
                            defaults={'thumbnail': thumb_file, 'ocr_stats': ocr_text}
                        )
                        self.stdout.write(f"  -> Saved {game_name} to database.")

            browser.close()
            self.stdout.write(self.style.SUCCESS("Scraping finished successfully!"))
