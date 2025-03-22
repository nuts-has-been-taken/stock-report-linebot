from app.core.config import postgress_db
from app.model.model import YouTubeVideo

import datetime

Session = postgress_db.SESSION

def get_today_youtube_vid(channel_id:str):
    """Get today report from database
    
    Args:
        channel_id (str): channel id
    
    Returns:
        dict: YouTubeVideo data
    """
    session = Session()
    today = datetime.date.today()
    results = session.query(YouTubeVideo).filter(YouTubeVideo.date == today, YouTubeVideo.channel_id==channel_id).all()
    session.close()
    if results:
        return results[0]
    else:
        return None

def save_youtube_vid(channel_name: str, channel_id: str, date: datetime.date, vid_name: str, vid_url: str, vid_summary: str = None):
    """Save a YouTube video record to the database.

    Args:
        channel_name (str): The name of the YouTube channel.
        channel_id (str): The ID of the YouTube channel.
        date (datetime.date): The date of the video.
        vid_name (str): The name of the video.
        vid_url (str): The URL of the video.
        vid_summary (str, optional): A summary of the video. Defaults to None.

    Returns:
        YouTubeVideo: The saved YouTubeVideo object.
    """
    session = Session()
    try:
        new_video = YouTubeVideo(
            channel_name=channel_name,
            channel_id=channel_id,
            date=date,
            vid_name=vid_name,
            vid_url=vid_url,
            vid_summary=vid_summary
        )
        session.add(new_video)
        session.commit()
        return new_video
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()