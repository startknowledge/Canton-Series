"""
YouTube Uploader using YouTube Data API v3
Handles OAuth 2.0 authentication and video uploads
"""
import os
import pickle
import json
from pathlib import Path
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from scripts.config import APIConfig, TEMP_DIR
from scripts.utils import logger

# YouTube API scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

class YouTubeUploader:
    """Handle YouTube video uploads with OAuth 2.0"""
    
    def __init__(self):
        self.client_id = APIConfig.YOUTUBE_CLIENT_ID
        self.client_secret = APIConfig.YOUTUBE_CLIENT_SECRET
        
        if not self.client_id or not self.client_secret:
            logger.warning("YouTube credentials not configured")
        
        self.token_file = TEMP_DIR / "youtube_token.pickle"
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with YouTube using OAuth 2.0"""
        credentials = None
        
        # Load existing token if available
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    credentials = pickle.load(token)
                logger.info("Loaded existing YouTube credentials")
            except Exception as e:
                logger.warning(f"Could not load token: {e}")
        
        # If no valid credentials, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    logger.info("Refreshed YouTube credentials")
                except Exception as e:
                    logger.warning(f"Could not refresh token: {e}")
                    credentials = None
            
            if not credentials:
                # Need to get new credentials via OAuth flow
                logger.info("Getting new YouTube OAuth credentials...")
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    SCOPES
                )
                credentials = flow.run_local_server(port=8080)
                logger.info("YouTube OAuth complete")
            
            # Save credentials for next time
            with open(self.token_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        # Build YouTube service
        self.youtube = build("youtube", "v3", credentials=credentials)
        logger.info("YouTube service initialized")
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list = None,
        category_id: str = "22",  # 22 = People & Blogs
        privacy_status: str = "unlisted",
        thumbnail_path: Optional[Path] = None,
        playlist_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: "public", "unlisted", or "private"
            thumbnail_path: Path to thumbnail image
            playlist_id: Optional playlist to add video to
        
        Returns:
            Video metadata from YouTube API
        """
        if not self.youtube:
            raise RuntimeError("YouTube service not initialized")
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Uploading video: {title[:50]}...")
        
        try:
            # Prepare video body
            body = {
                "snippet": {
                    "title": title[:100],  # YouTube title limit
                    "description": description[:5000],
                    "tags": tags[:500] if tags else [],
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(
                str(video_path),
                mimetype="video/mp4",
                resumable=True,
                chunksize=-1  # Auto chunk size
            )
            
            # Upload video
            logger.info("Starting video upload...")
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response.get("id")
            logger.info(f"Video uploaded successfully! Video ID: {video_id}")
            
            # Upload thumbnail if provided
            if thumbnail_path and thumbnail_path.exists():
                self._upload_thumbnail(video_id, thumbnail_path)
            
            # Add to playlist if specified
            if playlist_id and video_id:
                self._add_to_playlist(video_id, playlist_id)
            
            return response
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: Path) -> None:
        """Upload a custom thumbnail for the video"""
        logger.info(f"Uploading thumbnail for video {video_id}")
        
        try:
            media = MediaFileUpload(
                str(thumbnail_path),
                mimetype="image/jpeg",
                resumable=True
            )
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            response = request.execute()
            logger.info(f"Thumbnail uploaded: {response}")
            
        except HttpError as e:
            logger.error(f"Thumbnail upload failed: {e}")
    
    def _add_to_playlist(self, video_id: str, playlist_id: str) -> None:
        """Add video to a playlist"""
        logger.info(f"Adding video {video_id} to playlist {playlist_id}")
        
        try:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body=body
            )
            response = request.execute()
            logger.info(f"Added to playlist: {response}")
            
        except HttpError as e:
            logger.error(f"Playlist add failed: {e}")
    
    def get_channel_info(self) -> Dict[str, Any]:
        """Get channel information"""
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()
            return response.get("items", [])[0] if response.get("items") else {}
            
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return {}

# For testing
if __name__ == "__main__":
    uploader = YouTubeUploader()
    info = uploader.get_channel_info()
    print(f"Channel: {info.get('snippet', {}).get('title', 'Unknown')}")