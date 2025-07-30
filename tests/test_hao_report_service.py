"""
Unit tests for the optimized Hao Report Service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
import time

from app.service.hao_report_service import HaoReportService, HaoReportMetrics
from app.util.exceptions import YouTubeWorkflowError, VideoNotFoundError, OpenAIAPIError


class TestHaoReportMetrics:
    """Test cases for HaoReportMetrics class."""
    
    def test_metrics_initialization(self):
        """Test that metrics are properly initialized."""
        metrics = HaoReportMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.average_processing_time == 0.0
        assert metrics.consecutive_failures == 0
    
    def test_record_success(self):
        """Test recording successful requests."""
        metrics = HaoReportMetrics()
        start_time = time.time() - 1.5  # Simulate 1.5 second processing time
        
        # Record request start
        actual_start = metrics.record_request_start()
        assert metrics.total_requests == 1
        
        # Record success
        metrics.record_success(start_time, from_cache=False)
        
        assert metrics.successful_requests == 1
        assert metrics.cache_misses == 1
        assert metrics.cache_hits == 0
        assert metrics.consecutive_failures == 0
        assert metrics.average_processing_time > 0
    
    def test_record_failure(self):
        """Test recording failed requests."""
        metrics = HaoReportMetrics()
        start_time = time.time()
        error = Exception("Test error")
        
        metrics.record_request_start()
        metrics.record_failure(start_time, error)
        
        assert metrics.failed_requests == 1
        assert metrics.consecutive_failures == 1
    
    def test_get_metrics(self):
        """Test getting metrics summary."""
        metrics = HaoReportMetrics()
        
        # Record some activity
        start_time = time.time() - 1.0
        metrics.record_request_start()
        metrics.record_success(start_time, from_cache=True)
        
        start_time = time.time() - 0.5
        metrics.record_request_start()
        metrics.record_failure(start_time, Exception("Test"))
        
        result = metrics.get_metrics()
        
        assert result["total_requests"] == 2
        assert result["successful_requests"] == 1
        assert result["failed_requests"] == 1
        assert result["success_rate"] == 50.0
        assert result["cache_hit_rate"] == 100.0  # Only one success was from cache


class TestHaoReportService:
    """Test cases for HaoReportService class."""
    
    @pytest.fixture
    def service(self):
        """Create a HaoReportService instance for testing."""
        return HaoReportService()
    
    @patch('app.service.hao_report_service.get_today_hao_report')
    @patch('app.service.hao_report_service.push_message')
    def test_get_and_send_hao_report_success(self, mock_push_message, mock_get_report, service):
        """Test successful report generation and sending."""
        # Mock successful report data
        mock_data = Mock()
        mock_data.vid_name = "Test Video"
        mock_data.vid_summary = "### 重點摘要：Test summary ### 個人看法：Test opinion"
        mock_data.vid_img = "http://example.com/image.jpg"
        mock_data.vid_url = "http://youtube.com/watch?v=test"
        
        mock_get_report.return_value = (True, mock_data, None)
        
        # Test the method
        result = service.get_and_send_hao_report("test_event_id", cron_mode=True)
        
        # Verify results
        assert result["status"] == "success"
        assert result["video_title"] == "Test Video"
        assert "metrics" in result
        
        # Verify that push_message was called
        mock_push_message.assert_called_once()
    
    @patch('app.service.hao_report_service.get_today_hao_report')
    def test_get_and_send_hao_report_no_video(self, mock_get_report, service):
        """Test handling when no video is available."""
        mock_get_report.return_value = (False, None, "今日無直播")
        
        result = service.get_and_send_hao_report("test_event_id", cron_mode=True)
        
        assert result["status"] == "no_content"
        assert result["message"] == "今日無直播"
    
    @patch('app.service.hao_report_service.get_today_hao_report')
    def test_get_and_send_hao_report_error(self, mock_get_report, service):
        """Test handling of errors during report generation."""
        mock_get_report.return_value = (False, None, "API Error")
        
        # This should raise an exception that gets caught by retry decorator
        with pytest.raises(YouTubeWorkflowError):
            service.get_and_send_hao_report("test_event_id", cron_mode=True)
    
    def test_health_check(self, service):
        """Test service health check functionality."""
        # Initially should be healthy
        health = service.health_check()
        
        assert health["is_healthy"] is True
        assert "metrics" in health
        assert "circuit_breaker_state" in health
        assert "last_health_check" in health
    
    def test_health_check_with_failures(self, service):
        """Test health check with consecutive failures."""
        # Simulate multiple failures
        start_time = time.time()
        for _ in range(6):  # More than threshold
            service.metrics.record_failure(start_time, Exception("Test error"))
        
        health = service.health_check()
        
        # Should still be healthy initially due to time-based logic
        # Real unhealthy state would require 24 hours without success
        assert "is_healthy" in health
        assert health["metrics"]["consecutive_failures"] == 6


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Set up mocks for all external dependencies."""
        with patch('app.service.youtube.get_youtube_vid') as mock_get_vid, \
             patch('app.service.youtube.get_latest_live_stream') as mock_get_stream, \
             patch('app.service.youtube.process_youtube_data') as mock_process, \
             patch('app.util.llm.llm_create') as mock_llm, \
             patch('app.service.line.push_message') as mock_push:
            
            yield {
                'get_vid': mock_get_vid,
                'get_stream': mock_get_stream,
                'process': mock_process,
                'llm': mock_llm,
                'push': mock_push
            }
    
    def test_complete_workflow_with_new_video(self, mock_dependencies):
        """Test the complete workflow when processing a new video."""
        # Setup mocks
        mock_dependencies['get_vid'].return_value = None  # No existing data
        mock_dependencies['get_stream'].return_value = ("Test Video", "http://youtube.com/test", date.today())
        
        mock_data = Mock()
        mock_data.vid_name = "Test Video"
        mock_data.vid_summary = "### 重點摘要：Test ### 個人看法：Opinion"
        mock_dependencies['process'].return_value = (mock_data, None)
        
        # Test the service
        service = HaoReportService()
        result = service.get_and_send_hao_report("test_event", cron_mode=True)
        
        # Verify the workflow
        assert result["status"] == "success"
        mock_dependencies['get_vid'].assert_called_once()
        mock_dependencies['get_stream'].assert_called_once()
        mock_dependencies['process'].assert_called_once()
        mock_dependencies['push'].assert_called_once()
    
    def test_error_recovery_and_metrics(self, mock_dependencies):
        """Test error recovery and metrics collection."""
        service = HaoReportService()
        
        # First call fails
        mock_dependencies['get_vid'].side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            service.get_and_send_hao_report("test_event")
        
        # Verify metrics recorded the failure
        metrics = service.metrics.get_metrics()
        assert metrics["failed_requests"] > 0
        assert metrics["consecutive_failures"] > 0
        
        # Second call succeeds
        mock_dependencies['get_vid'].side_effect = None
        mock_dependencies['get_vid'].return_value = None
        mock_dependencies['get_stream'].return_value = ("Video", "url", date.today())
        
        mock_data = Mock()
        mock_data.vid_name = "Video"
        mock_data.vid_summary = "Summary"
        mock_dependencies['process'].return_value = (mock_data, None)
        
        result = service.get_and_send_hao_report("test_event")
        
        # Verify recovery
        assert result["status"] == "success"
        final_metrics = service.metrics.get_metrics()
        assert final_metrics["consecutive_failures"] == 0  # Reset on success


if __name__ == "__main__":
    pytest.main([__file__])