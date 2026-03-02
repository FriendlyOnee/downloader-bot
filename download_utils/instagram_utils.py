from instagrapi import Client
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class InstagramHandler:
    SESSION_FILE = "instagrapi_session.json"

    def __init__(self):
        self.client = Client()
        self.logged_in = False
        self._configure_client()

        username = os.getenv("INSTAGRAM_USERNAME")
        password = os.getenv("INSTAGRAM_PASSWORD")

        # Try to reuse existing session without calling login()
        if os.path.exists(self.SESSION_FILE):
            try:
                self.client.load_settings(self.SESSION_FILE)
                self._configure_client()
                self.client.login(username, password)
                # Test the session with a lightweight request
                self.client.user_info_by_username(username)
                self.logged_in = True
                print("Instagram: session is valid")
                return
            except Exception as e:
                print(f"Instagram: session invalid ({e}), trying fresh login")
                # Reset client for a clean login attempt
                self.client = Client()
                self._configure_client()

        # Fresh login only if session didn't work
        if username and password:
            try:
                self.client.login(username, password)
                self.client.dump_settings(self.SESSION_FILE)
                self.logged_in = True
                print("Instagram: fresh login successful")
            except Exception as e:
                print(f"Instagram login failed: {e}")

    def _configure_client(self):
        """Configure client with updated Instagram app version to avoid checkpoint."""
        self.client.set_settings({
            "app_version": "410.0.0.30.115",
            "android_version": 34,
            "android_release": "14.0.0",
            "version_code": "640000000"
        })
        self.client.set_user_agent(
            "Instagram 410.0.0.30.115 Android (34/14.0.0; 640dpi; 1440x3040; samsung; SM-G998B; p3s; exynos2100; en_US; 640000000)"
        )

    def download_post(self, shortcode):
        media_pk = self.client.media_pk_from_code(shortcode)
        result = self.client.private_request(f"media/{media_pk}/info/")

        if result and "items" in result and len(result["items"]) > 0:
            item = result["items"][0]

            # Handle video (reel or video post)
            if "video_versions" in item and len(item["video_versions"]) > 0:
                video_url = item["video_versions"][0]["url"]
                self._download_file(video_url, f"{shortcode}.mp4")

            # Handle image
            elif "image_versions2" in item:
                candidates = item["image_versions2"].get("candidates", [])
                if candidates:
                    image_url = candidates[0]["url"]
                    self._download_file(image_url, f"{shortcode}.jpg")

            # Handle carousel (multiple images/videos)
            if "carousel_media" in item:
                for idx, media in enumerate(item["carousel_media"]):
                    if "video_versions" in media:
                        url = media["video_versions"][0]["url"]
                        self._download_file(url, f"{shortcode}_{idx + 1}.mp4")
                    elif "image_versions2" in media:
                        url = media["image_versions2"]["candidates"][0]["url"]
                        self._download_file(url, f"{shortcode}_{idx + 1}.jpg")

    def _download_file(self, url, filename):
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    handler = InstagramHandler()
    # https://www.instagram.com/reel/DRSErcyjOKX/?igsh=dWJxcHltZ2JtNjRl
    shortcode = "DRSErcyjOKX"
    handler.download_post(shortcode)
