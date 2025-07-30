"""
Unit tests for optimized YouTube service functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from app.service.youtube import get_today_hao_report, process_youtube_data, _extract_and_summarize_content
from app.util.exceptions import YouTubeAPIError, VideoNotFoundError, AudioProcessingError, OpenAIAPIError


class TestGetTodayHaoReport:
    """Test cases for get_today_hao_report function."""
    
    @patch('app.service.youtube.get_youtube_vid')
    def test_existing_report_in_database(self, mock_get_vid):
        """Test retrieving existing report from database."""
        # Mock existing data
        mock_data = Mock()
        mock_data.vid_name = "Existing Video"
        mock_get_vid.return_value = mock_data
        
        success, data, error = get_today_hao_report()
        
        assert success is True
        assert data == mock_data
        assert error is None
        mock_get_vid.assert_called_once()
    
    @patch('app.service.youtube.process_youtube_data')
    @patch('app.service.youtube.get_latest_live_stream')
    @patch('app.service.youtube.get_youtube_vid')
    def test_new_video_processing(self, mock_get_vid, mock_get_stream, mock_process):
        """Test processing new video when not in database."""
        # Setup mocks
        mock_get_vid.return_value = None  # No existing data
        mock_get_stream.return_value = ("New Video", "http://youtube.com/new", date.today())
        
        mock_data = Mock()
        mock_data.vid_name = "New Video"
        mock_process.return_value = (mock_data, None)
        
        success, data, error = get_today_hao_report()
        
        assert success is True
        assert data == mock_data
        assert error is None
        
        mock_get_vid.assert_called_once()
        mock_get_stream.assert_called_once()
        mock_process.assert_called_once()
    
    @patch('app.service.youtube.get_latest_live_stream')
    @patch('app.service.youtube.get_youtube_vid')
    def test_no_video_today(self, mock_get_vid, mock_get_stream):
        """Test handling when no video is available today."""
        mock_get_vid.return_value = None
        yesterday = date.today().replace(day=date.today().day - 1)
        mock_get_stream.return_value = ("Old Video", "url", yesterday)
        
        success, data, error = get_today_hao_report()
        
        assert success is False
        assert data is None
        assert error == "今日無直播"
    
    @patch('app.service.youtube.process_youtube_data')
    @patch('app.service.youtube.get_latest_live_stream')
    @patch('app.service.youtube.get_youtube_vid')
    def test_processing_error(self, mock_get_vid, mock_get_stream, mock_process):
        """Test handling of processing errors."""
        mock_get_vid.return_value = None
        mock_get_stream.return_value = ("Video", "url", date.today())
        mock_process.return_value = (None, "Processing failed")
        
        success, data, error = get_today_hao_report()
        
        assert success is False
        assert data is None
        assert error == "Processing failed"


class TestProcessYouTubeData:
    """Test cases for process_youtube_data function."""
    
    @patch('app.service.youtube.save_youtube_vid')
    @patch('app.service.youtube.get_youtube_img')
    @patch('app.service.youtube._extract_and_summarize_content')
    @patch('app.service.youtube.get_live_stream')
    def test_successful_processing(self, mock_get_stream, mock_extract, mock_get_img, mock_save):
        """Test successful video data processing."""
        # Setup mocks
        test_date = date.today()
        mock_get_stream.return_value = ("Test Video", "http://youtube.com/test", test_date)
        mock_extract.return_value = "Generated summary"
        mock_get_img.return_value = "http://img.youtube.com/test.jpg"
        
        mock_saved_data = Mock()
        mock_save.return_value = mock_saved_data
        
        result, error = process_youtube_data("test_channel", test_date)
        
        assert result == mock_saved_data
        assert error is None
        
        mock_get_stream.assert_called_once_with("test_channel", test_date)
        mock_extract.assert_called_once_with("http://youtube.com/test")
        mock_get_img.assert_called_once_with("http://youtube.com/test")
        mock_save.assert_called_once()
    
    @patch('app.service.youtube.get_live_stream')
    def test_no_video_found(self, mock_get_stream):
        """Test handling when no video is found."""
        mock_get_stream.return_value = (None, None, None)
        
        result, error = process_youtube_data("test_channel", date.today())
        
        assert result is None
        assert error == "無法取得影片"
    
    @patch('app.service.youtube.get_live_stream')
    def test_video_not_found_error(self, mock_get_stream):
        """Test handling VideoNotFoundError."""
        mock_get_stream.side_effect = VideoNotFoundError("No video found")
        
        result, error = process_youtube_data("test_channel", date.today())
        
        assert result is None
        assert error == "無法取得影片"


class TestExtractAndSummarizeContent:
    """Test cases for _extract_and_summarize_content function."""
    
    @patch('app.service.youtube.create_summary')
    @patch('app.service.youtube.get_youtube_subtitles')
    def test_subtitle_extraction(self, mock_get_subtitles, mock_create_summary):
        """Test content extraction using subtitles."""
        mock_get_subtitles.return_value = "Video subtitle content"
        mock_create_summary.return_value = "Generated summary"
        
        result = _extract_and_summarize_content("http://youtube.com/test")
        
        assert result == "Generated summary"
        mock_get_subtitles.assert_called_once_with("http://youtube.com/test")
        mock_create_summary.assert_called_once_with("Video subtitle content")
    
    @patch('app.service.youtube.create_summary')
    @patch('app.service.youtube.audio_transcript_subtitle')
    @patch('app.service.youtube.get_youtube_audio')
    @patch('app.service.youtube.get_youtube_subtitles')
    @patch('app.service.youtube.TRANS_FIRST', True)
    def test_audio_transcription_mode(self, mock_get_subtitles, mock_get_audio, 
                                    mock_transcript, mock_create_summary):
        """Test content extraction using audio transcription."""
        mock_get_subtitles.return_value = None  # No subtitles available
        mock_get_audio.return_value = "/tmp/audio.mp3"
        mock_transcript.return_value = "Transcribed content"
        mock_create_summary.return_value = "Generated summary"
        
        with patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove:
            
            result = _extract_and_summarize_content("http://youtube.com/test")
            
            assert result == "Generated summary"
            mock_get_audio.assert_called_once()
            mock_transcript.assert_called_once_with("/tmp/audio.mp3")
            mock_create_summary.assert_called_once_with("Transcribed content")
            mock_remove.assert_called_once_with("/tmp/audio.mp3")
    
    @patch('app.service.youtube.get_youtube_subtitles')
    @patch('app.service.youtube.TRANS_FIRST', False)
    @patch('app.service.youtube.AUDIO_MODE', False)
    def test_no_content_extraction_method(self, mock_get_subtitles):
        """Test error when no content extraction method is available."""
        mock_get_subtitles.return_value = None
        
        with pytest.raises(Exception):  # Should raise ContentExtractionError
            _extract_and_summarize_content("http://youtube.com/test")


class TestErrorHandling:
    """Test error handling and retry mechanisms."""
    
    @patch('app.service.youtube.get_live_stream')
    def test_youtube_api_error_handling(self, mock_get_stream):
        """Test YouTube API error handling."""
        mock_get_stream.side_effect = YouTubeAPIError("API quota exceeded", error_code="QUOTA_EXCEEDED")
        
        result, error = process_youtube_data("test_channel", date.today())
        
        assert result is None
        assert "quota exceeded" in error.lower() or "api" in error.lower()
    
    @patch('app.service.youtube._extract_and_summarize_content')
    @patch('app.service.youtube.get_live_stream')
    def test_openai_api_error_handling(self, mock_get_stream, mock_extract):
        """Test OpenAI API error handling."""
        mock_get_stream.return_value = ("Video", "url", date.today())
        mock_extract.side_effect = OpenAIAPIError("OpenAI timeout")
        
        result, error = process_youtube_data("test_channel", date.today())
        
        assert result is None
        assert error is not None
    
    @patch('app.service.youtube.get_youtube_audio')
    @patch('app.service.youtube.get_youtube_subtitles')
    @patch('app.service.youtube.TRANS_FIRST', True)
    def test_audio_processing_error_handling(self, mock_get_subtitles, mock_get_audio):
        """Test audio processing error handling."""
        mock_get_subtitles.return_value = None
        mock_get_audio.side_effect = AudioProcessingError("Failed to download audio")
        
        with pytest.raises(Exception):  # Should raise AudioProcessingError
            _extract_and_summarize_content("http://youtube.com/test")


class TestRetryMechanism:
    """Test retry mechanisms for API calls."""
    
    @patch('app.service.youtube.get_live_stream')
    def test_retry_on_transient_error(self, mock_get_stream):
        """Test that transient errors trigger retries."""
        # First two calls fail, third succeeds
        mock_get_stream.side_effect = [
            YouTubeAPIError("Temporary error"),
            YouTubeAPIError("Another temporary error"),
            ("Success Video", "url", date.today())
        ]
        
        with patch('app.service.youtube._extract_and_summarize_content') as mock_extract, \
             patch('app.service.youtube.save_youtube_vid') as mock_save:
            
            mock_extract.return_value = "Summary"
            mock_save.return_value = Mock()
            
            result, error = process_youtube_data("test_channel", date.today())
            
            # Should eventually succeed after retries
            assert result is not None
            assert error is None
            assert mock_get_stream.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])