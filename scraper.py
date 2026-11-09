import os
import time
import requests
from playwright.sync_api import sync_playwright

def download_instagram_video(ig_url, output_filename="facebook_ready.mp4"):
    # 55+ Best Instagram Downloader Websites ki list (No options removed)
    websites_list = [
        "https://snapinsta.app/", "https://sssinstagram.com/", "https://saveig.app/en",
        "https://fastdl.app/", "https://indown.io/", "https://snapsave.app/en",
        "https://igram.world/", "https://instavideosave.net/", "https://igdownloader.app/en",
        "https://pocbi.com/", "https://saveinsta.app/en", "https://snapinsta.io/",
        "https://igram.io/", "https://toolzu.com/downloader/instagram/video/", "https://reelsaver.net/",
        "https://storysaver.net/", "https://downloadgram.org/", "https://viddig.com/",
        "https://instafinsta.com/", "https://reelsdownloader.io/", "https://instadownloader.co/",
        "https://save-insta.com/", "https://instasave.website/", "https://gramsave.com/",
        "https://instoffline.net/", "https://igsave.com/", "https://instawload.com/",
        "https://saveinsta.net/", "https://instadp.io/", "https://igtok.com/",
        "https://reelsaver.app/", "https://vidinsta.app/", "https://instasupersave.com/",
        "https://igram.online/", "https://reelsdownload.net/", "https://sssgram.com/",
        "https://igdownloader.com/", "https://savefrom.net/download-from-instagram", 
        "https://w3toys.com/instagram-video-downloader/", "https://givefastlink.com/instagram-video-downloader/",
        "https://savieo.com/", "https://downloadinstagramvideos.net/", "https://reelsdownloader.com/",
        "https://saveigtv.com/", "https://instasaved.net/", "https://igmin.com/",
        "https://igsaver.com/", "https://reelsave.app/", "https://instadown.com/",
        "https://gramvio.com/", "https://instasave.net/", "https://snapinsta.net/",
        "https://igdownloads.com/", "https://saveig.org/", "https://igdownload.io/"
    ]

    with sync_playwright() as p:
        # Headless=True for running in GitHub Actions server seamlessly
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for site_url in websites_list:
            print(f"\n[+] Trying website: {site_url}")
            page = context.new_page()
            
            try:
                # 1. Load the website
                page.goto(site_url, timeout=25000)
                page.wait_for_load_state("domcontentloaded")

                # -------------------------------------------------------------
                # SMART AUTO-DETECT LOGIC (Generic Locators)
                # -------------------------------------------------------------
                
                # A. Find Input box
                input_locator = page.locator("input[type='url'], input[name*='url'], input[name*='q'], input[id*='url'], input[id*='link'], input[placeholder*='Instagram']").first
                input_locator.wait_for(state="visible", timeout=10000)
                input_locator.fill(ig_url)
                time.sleep(1) 

                # B. Find and click Submit button
                submit_locator = page.locator("button[type='submit'], button[id*='submit'], button[class*='btn'], button:has-text('Download'), button:has-text('Get')").first
                submit_locator.click()

                # C. Wait for extraction and find .mp4 link
                print("    Waiting for extraction...")
                download_locator = page.locator("a[href*='.mp4'], a[href*='cdninstagram.com'], a[download], a:has-text('Download Video'), a:has-text('Download MP4')").first
                download_locator.wait_for(state="attached", timeout=20000)
                
                mp4_url = download_locator.get_attribute('href')

                if mp4_url and ('http' in mp4_url):
                    print(f"    [SUCCESS] Direct MP4 Link found on {site_url}!")
                    
                    # 2. File Download Logic
                    print("    Downloading file to disk...")
                    response = requests.get(mp4_url, stream=True)
                    if response.status_code == 200:
                        with open(output_filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=1024):
                                f.write(chunk)
                        print(f"    [COMPLETED] Video successfully saved as {output_filename}")
                        
                        page.close()
                        browser.close()
                        return True # Exit the function after successful download
                    else:
                        print("    [ERROR] Found link but file download failed.")

            except Exception as e:
                # Catch any errors (timeout, layout mismatch, ad blockers) and continue
                print(f"    [FAILED] Could not process {site_url}. Moving to next...")
            
            finally:
                page.close() # Free up RAM for the next iteration

        browser.close()
        print("\n[-] All 55+ fallback websites failed. The Instagram link might be private or all sites are down.")
        return False

# --- Run the Script ---
if __name__ == "__main__":
    # GitHub Action ke Environment Variable se link fetch karega
    insta_url = os.environ.get("INSTAGRAM_URL") 
    
    if insta_url:
        print(f"Target Instagram URL received: {insta_url}")
        # Run function and save the video
        download_instagram_video(insta_url, "facebook_ready.mp4")
    else:
        print("Error: No Instagram URL provided! Please check your GitHub Actions input.")
        # Local testing ke liye aap yahan hardcode URL daal sakte hain jaise:
        # download_instagram_video("https://www.instagram.com/p/DehahPxS57W/", "facebook_ready.mp4")
