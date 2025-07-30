from app.core.config import postgress_db
from app.model.postgresql import YouTubeVideo
from app.util.resource_manager import with_db_session, DatabaseConnectionManager
from app.util.exceptions import DatabaseError
from logger import logger

import datetime
from typing import Optional

Session = postgress_db.SESSION

@with_db_session
def get_youtube_vid(channel_id: str, date: datetime.date, session=None) -> Optional[YouTubeVideo]:
    """Get report from database for a specific date.
    
    Args:
        channel_id (str): Channel ID.
        date (datetime.date): The date for which to retrieve the data.
        session: Database session (injected by decorator)
    
    Returns:
        YouTubeVideo: Video data if found, None otherwise
        
    Raises:
        DatabaseError: When database operation fails
    """
    try:
        logger.debug(f"Querying YouTube video for channel {channel_id} on {date}")
        
        result = session.query(YouTubeVideo).filter(
            YouTubeVideo.date == date, 
            YouTubeVideo.channel_id == channel_id
        ).first()
        
        if result:
            logger.debug(f"Found YouTube video: {result.vid_name}")
            return YouTubeVideo(
                channel_name=result.channel_name,
                channel_id=result.channel_id,
                date=result.date,
                vid_name=result.vid_name,
                vid_url=result.vid_url,
                vid_summary=result.vid_summary,
                vid_img=result.vid_img
            )
        
        logger.debug(f"No YouTube video found for channel {channel_id} on {date}")
        return None
        
    except Exception as e:
        logger.error(f"Error querying YouTube video: {str(e)}")
        raise DatabaseError(f"Failed to get YouTube video: {str(e)}", cause=e)

@with_db_session
def save_youtube_vid(
    channel_name: str, 
    channel_id: str, 
    date: datetime.date, 
    vid_name: str, 
    vid_url: str, 
    vid_summary: Optional[str] = None, 
    vid_img: Optional[str] = None,
    session=None
) -> YouTubeVideo:
    """Save a YouTube video record to the database.

    Args:
        channel_name (str): The name of the YouTube channel.
        channel_id (str): The ID of the YouTube channel.
        date (datetime.date): The date of the video.
        vid_name (str): The name of the video.
        vid_url (str): The URL of the video.
        vid_summary (str, optional): A summary of the video. Defaults to None.
        vid_img (str, optional): The URL of the video thumbnail. Defaults to None.
        session: Database session (injected by decorator)

    Returns:
        YouTubeVideo: The saved YouTubeVideo object.
        
    Raises:
        DatabaseError: When database operation fails
    """
    try:
        logger.debug(f"Saving YouTube video: {vid_name} for channel {channel_id} on {date}")
        
        # Check if video already exists
        existing = session.query(YouTubeVideo).filter(
            YouTubeVideo.channel_id == channel_id,
            YouTubeVideo.date == date
        ).first()
        
        if existing:
            # Update existing record
            logger.info(f"Updating existing YouTube video record for {channel_id} on {date}")
            existing.channel_name = channel_name
            existing.vid_name = vid_name
            existing.vid_url = vid_url
            existing.vid_summary = vid_summary
            existing.vid_img = vid_img
            session.flush()
            return existing
        else:
            # Create new record
            logger.info(f"Creating new YouTube video record for {channel_id} on {date}")
            new_video = YouTubeVideo(
                channel_name=channel_name,
                channel_id=channel_id,
                date=date,
                vid_name=vid_name,
                vid_url=vid_url,
                vid_summary=vid_summary,
                vid_img=vid_img
            )
            session.add(new_video)
            session.flush()
            session.refresh(new_video)
            return new_video
            
    except Exception as e:
        logger.error(f"Error saving YouTube video: {str(e)}")
        raise DatabaseError(f"Failed to save YouTube video: {str(e)}", cause=e)