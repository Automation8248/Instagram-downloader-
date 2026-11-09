import requests
import re
import os
import sys

def download_ig_video(reel_url):
    try:
        # URL se shortcode extract karna
        if '/reel/' in reel_url:
            shortcode = reel_url.split('/reel/')[1].split('/')[0]
        elif '/p/' in reel_url:
            shortcode = reel_url.split('/p/')[1].split('/')[0]
        else:
            print("❌ Invalid URL format.")
            sys.exit(1)

        print(f"🔍 Shortcode extract ho gaya: {shortcode}")
        
        # Embed page URL generate karna
        embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        print("🌐 Instagram se connect kar rahe hain...")
        response = requests.get(embed_url, headers=headers, timeout=15)
        
        # Source code se video link nikalna
        match = re.search(r'"video_url":"(.*?)"', response.text)
        
        if match:
            raw_url = match.group(1)
            clean_url = raw_url.encode('utf-8').decode('unicode_escape')
            print("✅ Direct CDN Link mil gaya. Download shuru ho raha hai...")
            
            vid_response = requests.get(clean_url, stream=True, headers=headers)
            vid_response.raise_for_status()
            
            filename = f"{shortcode}.mp4"
            with open(filename, 'wb') as f:
                for chunk in vid_response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            
            print(f"🎉 Download Complete: {filename}")
            
            # GitHub Actions ko file ka naam batane ke liye environment variable set karna
            env_file = os.getenv('GITHUB_ENV')
            if env_file:
                with open(env_file, 'a') as f:
                    f.write(f"VIDEO_FILENAME={filename}\n")
        else:
            print("❌ Video link nahi mila. Ho sakta hai video private ho ya Instagram block kar raha ho.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error aaya: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # GitHub Action se input URL lena
    url = os.getenv("IG_URL")
    if not url:
        print("❌ URL provide nahi kiya gaya!")
        sys.exit(1)
    
    print(f"🔗 Processing URL: {url}")
    download_ig_video(url)
