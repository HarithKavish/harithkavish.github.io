"""
Test theme persistence across GitHub Pages subpaths using Playwright.
Tests that dark mode preference carries over from main portfolio to Object Detection page.
"""

from playwright.sync_api import sync_playwright
import time

def test_theme_persistence():
    print("🧪 Testing Theme Persistence Across Pages\n")
    
    with sync_playwright() as p:
        # Launch browser with visible window
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 60)
        print("STEP 1: Navigate to Main Portfolio")
        print("=" * 60)
        
        # Navigate to main portfolio (GitHub Pages)
        page.goto("https://harithkavish.github.io/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Check initial theme
        initial_dark_mode = page.evaluate("document.body.classList.contains('dark-mode')")
        initial_theme = page.evaluate("localStorage.getItem('theme')")
        print(f"✓ Page loaded: https://harithkavish.github.io/")
        print(f"  Initial dark mode: {initial_dark_mode}")
        print(f"  Initial localStorage theme: {initial_theme}")
        print()
        
        print("=" * 60)
        print("STEP 2: Toggle Dark Mode ON")
        print("=" * 60)
        
        # Find and click the dark mode toggle button
        dark_mode_toggle = page.locator("#darkModeToggle")
        
        # Toggle to dark mode if not already dark
        if not initial_dark_mode:
            print("  Clicking dark mode toggle button...")
            dark_mode_toggle.click()
            time.sleep(1)
        else:
            print("  Already in dark mode, toggling to light then back to dark...")
            dark_mode_toggle.click()  # Toggle to light
            time.sleep(1)
            dark_mode_toggle.click()  # Toggle back to dark
            time.sleep(1)
        
        # Verify dark mode is now active
        dark_mode_active = page.evaluate("document.body.classList.contains('dark-mode')")
        stored_theme = page.evaluate("localStorage.getItem('theme')")
        toggle_icon = dark_mode_toggle.text_content()
        
        print(f"✓ Dark mode toggled")
        print(f"  Body has .dark-mode class: {dark_mode_active}")
        print(f"  localStorage.theme: '{stored_theme}'")
        print(f"  Toggle button icon: {toggle_icon}")
        print()
        
        if not dark_mode_active or stored_theme != 'dark':
            print("❌ ERROR: Dark mode not properly activated on main portfolio!")
            browser.close()
            return False
        
        print("=" * 60)
        print("STEP 3: Navigate to Object Detection Page")
        print("=" * 60)
        
        # Navigate to Object Detection page
        print("  Navigating to Multi-Object-Detection-using-YOLO...")
        page.goto("https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print(f"✓ Page loaded: https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/")
        print()
        
        print("=" * 60)
        print("STEP 4: Verify Theme Persisted")
        print("=" * 60)
        
        # Check if theme persisted
        detection_page_theme = page.evaluate("localStorage.getItem('theme')")
        detection_page_dark_mode = page.evaluate("""
            document.documentElement.classList.contains('dark-mode') || 
            document.body.classList.contains('dark-mode')
        """)
        
        print(f"  localStorage.theme on Object Detection page: '{detection_page_theme}'")
        print(f"  Has .dark-mode class: {detection_page_dark_mode}")
        print()
        
        # Check background color (should be dark if dark mode is active)
        bg_color = page.evaluate("""
            window.getComputedStyle(document.body).backgroundColor
        """)
        print(f"  Body background color: {bg_color}")
        print()
        
        print("=" * 60)
        print("STEP 5: Navigate Back to Main Portfolio")
        print("=" * 60)
        
        # Go back to main portfolio
        page.goto("https://harithkavish.github.io/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Verify theme still persisted
        back_to_main_theme = page.evaluate("localStorage.getItem('theme')")
        back_to_main_dark_mode = page.evaluate("document.body.classList.contains('dark-mode')")
        
        print(f"✓ Returned to main portfolio")
        print(f"  localStorage.theme: '{back_to_main_theme}'")
        print(f"  Dark mode still active: {back_to_main_dark_mode}")
        print()
        
        print("=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        
        # Determine success
        success = (
            stored_theme == 'dark' and
            detection_page_theme == 'dark' and
            back_to_main_theme == 'dark' and
            dark_mode_active and
            back_to_main_dark_mode
        )
        
        if success:
            print("✅ SUCCESS! Theme persistence works correctly!")
            print()
            print("Summary:")
            print(f"  1. Set theme to 'dark' on main portfolio: ✓")
            print(f"  2. localStorage saved correctly: ✓")
            print(f"  3. Object Detection page read theme: ✓")
            print(f"  4. Theme persisted when returning: ✓")
        else:
            print("❌ FAILED! Theme did not persist correctly.")
            print()
            print("Issues detected:")
            if stored_theme != 'dark':
                print(f"  - Main portfolio didn't save 'dark' theme (got: '{stored_theme}')")
            if detection_page_theme != 'dark':
                print(f"  - Object Detection page didn't read 'dark' theme (got: '{detection_page_theme}')")
            if not detection_page_dark_mode:
                print(f"  - Object Detection page didn't apply .dark-mode class")
            if back_to_main_theme != 'dark':
                print(f"  - Theme lost when returning to main portfolio")
        
        print()
        print("Keeping browser open for 5 seconds for visual inspection...")
        time.sleep(5)
        
        browser.close()
        return success

if __name__ == "__main__":
    try:
        result = test_theme_persistence()
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
