"""
Optimized Hao Report Service with improved error handling, monitoring, and performance.
"""
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import time

from app.service.youtube import get_today_hao_report, HAO_CHANNEL_ID
from app.service.line import push_message, hao_report_flex_msg
from app.util.exceptions import YouTubeWorkflowError, VideoNotFoundError
from app.util.resource_manager import CircuitBreaker, circuit_breaker
from app.util.retry import retry_with_backoff
from logger import logger


class HaoReportMetrics:
    """Metrics collection for Hao Report operations."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.average_processing_time = 0.0
        self.last_success_time = None
        self.last_failure_time = None
        self.consecutive_failures = 0
    
    def record_request_start(self) -> float:
        """Record the start of a request and return start time."""
        self.total_requests += 1
        return time.time()
    
    def record_success(self, start_time: float, from_cache: bool = False):
        """Record a successful request."""
        processing_time = time.time() - start_time
        self.successful_requests += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        
        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        # Update rolling average
        if self.successful_requests == 1:
            self.average_processing_time = processing_time
        else:
            self.average_processing_time = (
                (self.average_processing_time * (self.successful_requests - 1) + processing_time) 
                / self.successful_requests
            )
    
    def record_failure(self, start_time: float, error: Exception):
        """Record a failed request."""
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        logger.error(f"Request failed after {time.time() - start_time:.2f}s: {str(error)}")
    
    def get_metrics(self) -> Dict:
        """Get current metrics as a dictionary."""
        success_rate = (self.successful_requests / self.total_requests) if self.total_requests > 0 else 0
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses)) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(success_rate * 100, 2),
            "cache_hit_rate": round(cache_hit_rate * 100, 2),
            "average_processing_time": round(self.average_processing_time, 2),
            "consecutive_failures": self.consecutive_failures,
            "last_success_time": self.last_success_time,
            "last_failure_time": self.last_failure_time
        }


class HaoReportService:
    """
    Optimized service for handling Hao Report operations with monitoring and resilience.
    """
    
    def __init__(self):
        self.metrics = HaoReportMetrics()
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)
        self.is_healthy = True
        self.last_health_check = time.time()
    
    @retry_with_backoff(max_retries=2, backoff_factor=1.5)
    @circuit_breaker
    def get_and_send_hao_report(self, event_id: str, cron_mode: bool = True) -> Dict[str, any]:
        """
        Get today's Hao report and send via LINE with comprehensive error handling.
        
        Args:
            event_id: LINE event ID for message delivery
            cron_mode: Whether this is called from cron job
            
        Returns:
            Dict containing operation result and metrics
        """
        start_time = self.metrics.record_request_start()
        
        try:
            logger.info(f"Processing Hao report request for event_id: {event_id}, cron_mode: {cron_mode}")
            
            # Get report data
            success, data, error_msg = get_today_hao_report()
            
            if not success:
                if error_msg == "今日無直播":
                    logger.info("No live stream today - this is normal")
                    self.metrics.record_success(start_time, from_cache=False)
                    return {
                        "status": "no_content",
                        "message": "今日無直播",
                        "metrics": self.metrics.get_metrics()
                    }
                else:
                    raise YouTubeWorkflowError(f"Failed to get Hao report: {error_msg}")
            
            # Process and send the report
            self._send_report_message(event_id, data, cron_mode)
            
            self.metrics.record_success(start_time, from_cache=bool(data))
            logger.info(f"Successfully processed and sent Hao report for {event_id}")
            
            return {
                "status": "success",
                "message": "Report sent successfully",
                "video_title": data.vid_name if data else None,
                "metrics": self.metrics.get_metrics()
            }
            
        except Exception as e:
            self.metrics.record_failure(start_time, e)
            
            if isinstance(e, VideoNotFoundError):
                # Don't retry for video not found
                return {
                    "status": "no_content",
                    "message": str(e),
                    "metrics": self.metrics.get_metrics()
                }
            
            # For other errors, let retry decorator handle it
            logger.error(f"Error in get_and_send_hao_report: {str(e)}")
            raise
    
    def _send_report_message(self, event_id: str, data, cron_mode: bool):
        """
        Send the formatted report message via LINE.
        
        Args:
            event_id: LINE event ID
            data: Video data object
            cron_mode: Whether this is a cron job
        """
        import re
        import copy
        from datetime import datetime
        
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
            
            # Parse summary content
            if data.vid_summary:
                sections = re.split(r'### .+?：', data.vid_summary)
                contents = [section.strip() for section in sections if section.strip()]
            else:
                contents = ["摘要處理中...", ""]
            
            # Create flex message
            flex_copy = copy.deepcopy(hao_report_flex_msg)
            flex_copy["header"]["contents"][0]["text"] = f"【游庭皓的財經皓角】 {today} 報告"
            
            if data.vid_img:
                flex_copy["hero"]["url"] = data.vid_img
                flex_copy["hero"]["action"]["uri"] = data.vid_url
            
            # Safely set content with length checks
            if len(contents) > 0 and len(contents[0]) > 0:
                flex_copy["body"]["contents"][1]["text"] = contents[0][:1000]  # Limit length
            
            if len(contents) > 1 and len(contents[1]) > 0:
                flex_copy["body"]["contents"][4]["text"] = contents[1][:1000]  # Limit length
            
            # Send message
            push_message(to=event_id, flex_msg=flex_copy, alt_text=f"【游庭皓的財經皓角】報告")
            logger.info(f"Sent Hao report message to {event_id}")
            
        except Exception as e:
            logger.error(f"Failed to send report message: {str(e)}")
            if not cron_mode:
                # Send error message for manual requests
                push_message(to=event_id, message="報告發送失敗，請稍後再試")
            raise
    
    def health_check(self) -> Dict[str, any]:
        """
        Perform health check on the service.
        
        Returns:
            Dict containing health status and metrics
        """
        current_time = time.time()
        
        # Check if we've had recent successful operations
        time_since_last_success = (
            current_time - self.metrics.last_success_time 
            if self.metrics.last_success_time else float('inf')
        )
        
        # Consider unhealthy if no success in last 24 hours and we have failures
        max_time_without_success = 24 * 3600  # 24 hours
        is_healthy = (
            time_since_last_success < max_time_without_success or 
            self.metrics.consecutive_failures < 5
        )
        
        self.is_healthy = is_healthy
        self.last_health_check = current_time
        
        health_status = {
            "is_healthy": is_healthy,
            "circuit_breaker_state": self.circuit_breaker.state,
            "time_since_last_success": round(time_since_last_success, 2),
            "last_health_check": current_time,
            "metrics": self.metrics.get_metrics()
        }
        
        logger.info(f"Health check completed: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
        return health_status
    
    async def batch_health_check(self, services: List['HaoReportService']) -> Dict[str, any]:
        """
        Perform health checks on multiple service instances.
        
        Args:
            services: List of service instances to check
            
        Returns:
            Aggregated health status
        """
        health_checks = await asyncio.gather(
            *[asyncio.create_task(asyncio.to_thread(service.health_check)) for service in services],
            return_exceptions=True
        )
        
        healthy_count = sum(1 for check in health_checks if isinstance(check, dict) and check.get("is_healthy"))
        total_count = len(services)
        
        return {
            "overall_health": healthy_count / total_count if total_count > 0 else 0,
            "healthy_instances": healthy_count,
            "total_instances": total_count,
            "individual_health": health_checks
        }


# Global service instance
hao_report_service = HaoReportService()