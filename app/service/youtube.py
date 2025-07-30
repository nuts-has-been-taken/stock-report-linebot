from app.db.youtube import save_youtube_vid, get_youtube_vid
from app.util.youtube import get_latest_live_stream, get_live_stream, get_youtube_subtitles, get_youtube_img, get_youtube_audio
from app.util.llm import create_summary, create_summary_audio, audio_transcript_subtitle
from app.util.exceptions import (
    YouTubeAPIError, AudioProcessingError, OpenAIAPIError, 
    DatabaseError, VideoNotFoundError, ContentExtractionError
)
from app.util.retry import retry_with_backoff, is_retryable_error
from app.core.config import openai_client
from logger import logger

from datetime import date, timedelta
import os
from typing import Tuple, Optional

AUDIO_MODE = openai_client.AUDIO_MODE
TRANS_FIRST = openai_client.TRANS_FIRST

# 財經皓角頻道
HAO_CHANNEL_ID = 'UC0lbAQVpenvfA2QqzsRtL_g'

@retry_with_backoff(
    max_retries=3, 
    backoff_factor=2.0,
    exceptions=(YouTubeAPIError, AudioProcessingError, OpenAIAPIError)
)
def process_youtube_data(channel_id: str, current_date: date) -> Tuple[Optional[object], Optional[str]]:
    """
    Process YouTube video data for a given channel and date.
    
    Args:
        channel_id: YouTube channel ID
        current_date: Target date for video processing
        
    Returns:
        Tuple of (video_data, error_message)
        
    Raises:
        YouTubeAPIError: When YouTube API operations fail
        AudioProcessingError: When audio processing fails
        OpenAIAPIError: When OpenAI API operations fail
        DatabaseError: When database operations fail
    """
    try:
        # Get video information
        title, url, vid_date = get_live_stream(channel_id, current_date)
        
        if not url:
            raise VideoNotFoundError(f"No video found for channel {channel_id} on {current_date}")

        logger.info(f"Processing video: {title} from {vid_date}")
        
        # Extract content and generate summary
        summary = _extract_and_summarize_content(url)
        
        # Get video thumbnail
        try:
            img_url = get_youtube_img(url)
        except Exception as e:
            logger.warning(f"Failed to get video thumbnail: {e}")
            img_url = None
        
        # Save to database
        try:
            data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary, img_url)
            logger.info(f"Successfully saved video data for {vid_date}")
            return data, None
        except Exception as e:
            raise DatabaseError(f"Failed to save video data: {str(e)}", cause=e)
            
    except VideoNotFoundError as e:
        logger.warning(str(e))
        return None, "無法取得影片"
    except (YouTubeAPIError, AudioProcessingError, OpenAIAPIError, DatabaseError) as e:
        logger.error(f"Error processing YouTube data: {str(e)}")
        if is_retryable_error(e):
            raise  # Will be caught by retry decorator
        return None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in process_youtube_data: {str(e)}")
        return None, "處理影片時發生未知錯誤"


def _extract_and_summarize_content(video_url: str) -> str:
    """
    Extract content from video and generate summary.
    
    Args:
        video_url: YouTube video URL
        
    Returns:
        Generated summary text
        
    Raises:
        ContentExtractionError: When content extraction fails
        OpenAIAPIError: When OpenAI API operations fail
    """
    audio_file_path = None
    
    try:
        # Try to get subtitles first
        subtitle = get_youtube_subtitles(video_url)
        
        if subtitle:
            logger.info("使用字幕進行 summary")
            return create_summary(subtitle)
        
        # If no subtitles, try audio processing
        if TRANS_FIRST:
            # Transcribe audio first, then summarize
            logger.info("字幕不可用，使用音訊進行轉錄")
            audio_file_path = get_youtube_audio(youtube_url=video_url, encode_string=False)
            
            if not audio_file_path or not os.path.exists(audio_file_path):
                raise AudioProcessingError("Failed to download audio file")
            
            transcript = audio_transcript_subtitle(audio_file_path)
            
            if not transcript:
                raise AudioProcessingError("Failed to transcribe audio")
            
            logger.info("轉錄完成，開始進行 summary")
            return create_summary(transcript)
            
        elif AUDIO_MODE:
            # Direct audio summarization
            logger.info("使用音訊進行直接 summary")
            audio_data = get_youtube_audio(youtube_url=video_url, encode_string=True)
            
            if not audio_data:
                raise AudioProcessingError("Failed to encode audio data")
            
            return create_summary_audio(audio_data)
        
        else:
            raise ContentExtractionError("字幕未上傳且音訊處理未啟用")
            
    except (AudioProcessingError, OpenAIAPIError):
        raise  # Re-raise specific errors
    except Exception as e:
        raise ContentExtractionError(f"Failed to extract content: {str(e)}", cause=e)
    finally:
        # Clean up audio file if it exists
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                logger.info(f"Cleaned up audio file: {audio_file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove audio file {audio_file_path}: {e}")

@retry_with_backoff(
    max_retries=2,
    backoff_factor=1.5,
    exceptions=(DatabaseError, YouTubeAPIError)
)
def get_today_hao_report() -> Tuple[bool, Optional[object], Optional[str]]:
    """
    Get today's Hao report, either from database or by processing new video.
    
    Returns:
        Tuple of (success, data, error_message)
    """
    today = date.today()
    
    try:
        # First, try to get from database
        logger.info(f"Checking database for Hao report on {today}")
        data = get_youtube_vid(HAO_CHANNEL_ID, today)
        
        if data:
            logger.info(f"Found existing Hao report for {today}")
            return True, data, None
        
        # If not in database, check for new video
        logger.info(f"No existing report found, checking for new video on {today}")
        
        try:
            title, url, vid_date = get_latest_live_stream(HAO_CHANNEL_ID)
        except Exception as e:
            raise YouTubeAPIError(f"Failed to get latest live stream: {str(e)}", cause=e)
        
        if vid_date != today:
            logger.info(f"Latest video is from {vid_date}, not today ({today})")
            return False, None, "今日無直播"
        
        # Process the new video
        logger.info(f"Processing new video: {title}")
        data, error = process_youtube_data(HAO_CHANNEL_ID, today)
        
        if error:
            logger.error(f"Failed to process video: {error}")
            return False, None, error
        
        logger.info(f"Successfully processed new Hao report for {today}")
        return True, data, None
        
    except (DatabaseError, YouTubeAPIError) as e:
        logger.error(f"Error in get_today_hao_report: {str(e)}")
        if is_retryable_error(e):
            raise  # Will be caught by retry decorator
        return False, None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in get_today_hao_report: {str(e)}")
        return False, None, "取得報告時發生未知錯誤"

# 下載指定時間區間內的報告
def generate_hao_report(start_date:date, end_date:date):
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        data = get_youtube_vid(HAO_CHANNEL_ID, current_date)
        if not data:
            data, error = process_youtube_data(HAO_CHANNEL_ID, current_date)
            if error:
                current_date += timedelta(days=1)
                continue
        if data:
            all_data.append(data)
        current_date += timedelta(days=1)

    if not all_data:
        return "指定時間區間內無報告"
    else:
        return all_data