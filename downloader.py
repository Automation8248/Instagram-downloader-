import os
import sys
import argparse
import cloudinary
import cloudinary.uploader
import yt_dlp

# Configure Cloudinary credentials from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_to_cloudinary(file_path):
    """Uploads downloaded video file to Cloudinary using chunked upload for large assets."""
    filename = os.path.basename(file_path)
    public_id = os.path.splitext(filename)[0]
    
    print(f"🔄 Uploading {filename} to Cloudinary...")
    try:
        response = cloudinary.uploader.upload_large(
            file_path,
            resource_type="video",
            public_id=f"social_downloads/{public_id}",
            overwrite=True
        )
        print(f"✅ Successfully Uploaded: {filename}")
        print(f"🔗 Cloudinary URL: {response.get('secure_url')}\n")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {filename} to Cloudinary. Error: {e}\n")
        return False

def hard_download_profile(profile_url):
    """Force-downloads all profile videos using aggressive extraction rules."""
    # Ensure a local download folder exists
    download_dir = "downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Aggressive configuration to enforce "hard download" bypassing non-fatal blocks
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{download_dir}/%(title).50s_%(id)s.%(ext)s',
        'ignoreerrors': True,          # Keep going even if a video is private/deleted
        'no_warnings': True,
        'extract_flat': False,         # Force full evaluation of playlists/profiles
        'concurrent_fragment_downloads': 5,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        'retries': 10,                 # Retry connection drops aggressively
        'fragment_retries': 10,
    }

    print(f"🚀 Initializing hard-download sequence for profile: {profile_url}")
    
    # Run download phase
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([profile_url])
        except Exception as e:
            print(f"⚠️ Initial extraction notice: {e}. Continuing with successfully resolved files.")

    # Run processing and upload phase
    downloaded_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
    
    if not downloaded_files:
        print("❌ No videos could be successfully extracted from this profile URL.")
        return

    print(f"\n📦 Found {len(downloaded_files)} downloaded file(s) locally. Starting Cloudinary migration...")
    
    success_count = 0
    for file_path in downloaded_files:
        if upload_to_cloudinary(file_path):
            success_count += 1
            # Clean up local storage immediately to prevent GitHub Action disk space saturation
            try:
                os.remove(file_path)
            except OSError:
                pass

    print("==================================================")
    print(f"🎉 Process Finished: {success_count}/{len(downloaded_files)} videos successfully pushed to Cloudinary.")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile Video Bulk Downloader & Cloudinary Uploader")
    parser.add_argument("--url", required=True, help="The target social media profile link")
    args = parser.parse_args()
    
    hard_download_profile(args.url)
