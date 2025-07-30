"""
Database migration to add performance indexes for YouTube videos table.
"""
from sqlalchemy import text
from app.core.config import postgress_db
from logger import logger


def add_youtube_indexes():
    """Add indexes to improve YouTube video query performance."""
    
    indexes = [
        # Composite index for most common query pattern (channel_id + date)
        "CREATE INDEX IF NOT EXISTS idx_youtube_videos_channel_date ON youtube_videos (channel_id, date);",
        
        # Index for date-based queries
        "CREATE INDEX IF NOT EXISTS idx_youtube_videos_date ON youtube_videos (date DESC);",
        
        # Index for channel-based queries
        "CREATE INDEX IF NOT EXISTS idx_youtube_videos_channel ON youtube_videos (channel_id);",
        
        # Partial index for recent videos (last 30 days) - most frequently accessed
        "CREATE INDEX IF NOT EXISTS idx_youtube_videos_recent ON youtube_videos (channel_id, date DESC) WHERE date >= CURRENT_DATE - INTERVAL '30 days';",
    ]
    
    engine = postgress_db.ENGINE
    
    try:
        with engine.connect() as connection:
            for index_sql in indexes:
                logger.info(f"Creating index: {index_sql}")
                connection.execute(text(index_sql))
                connection.commit()
        
        logger.info("Successfully created all YouTube video indexes")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise


def add_report_indexes():
    """Add indexes to improve report table query performance."""
    
    indexes = [
        # Index for report date queries
        "CREATE INDEX IF NOT EXISTS idx_reports_date ON reports (date DESC);",
        
        # Index for report type queries
        "CREATE INDEX IF NOT EXISTS idx_reports_type ON reports (type);",
        
        # Composite index for type + date queries
        "CREATE INDEX IF NOT EXISTS idx_reports_type_date ON reports (type, date DESC);",
        
        # Indexes for daily tables
        "CREATE INDEX IF NOT EXISTS idx_daily_major_invest_date ON daily_major_invest (date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_daily_margin_date ON daily_margin (date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_daily_future_date ON daily_future (date DESC);",
    ]
    
    engine = postgress_db.ENGINE
    
    try:
        with engine.connect() as connection:
            for index_sql in indexes:
                logger.info(f"Creating index: {index_sql}")
                connection.execute(text(index_sql))
                connection.commit()
        
        logger.info("Successfully created all report indexes")
        
    except Exception as e:
        logger.error(f"Failed to create report indexes: {str(e)}")
        raise


def create_youtube_video_constraints():
    """Add constraints to ensure data integrity."""
    
    constraints = [
        # Unique constraint to prevent duplicate videos for same channel/date
        "ALTER TABLE youtube_videos ADD CONSTRAINT IF NOT EXISTS uk_youtube_videos_channel_date UNIQUE (channel_id, date);",
        
        # Check constraints for data validation
        "ALTER TABLE youtube_videos ADD CONSTRAINT IF NOT EXISTS chk_youtube_videos_url CHECK (vid_url ~ '^https://www\.youtube\.com/watch\\?v=.+$');",
        "ALTER TABLE youtube_videos ADD CONSTRAINT IF NOT EXISTS chk_youtube_videos_date CHECK (date <= CURRENT_DATE + INTERVAL '1 day');",
    ]
    
    engine = postgress_db.ENGINE
    
    try:
        with engine.connect() as connection:
            for constraint_sql in constraints:
                try:
                    logger.info(f"Adding constraint: {constraint_sql}")
                    connection.execute(text(constraint_sql))
                    connection.commit()
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"Constraint already exists, skipping: {constraint_sql}")
                    else:
                        logger.warning(f"Failed to add constraint: {str(e)}")
        
        logger.info("Finished processing YouTube video constraints")
        
    except Exception as e:
        logger.error(f"Failed to create constraints: {str(e)}")
        raise


def optimize_database_settings():
    """Optimize PostgreSQL settings for better performance."""
    
    # These are recommendations that should be applied by DBA
    optimizations = [
        # Enable auto-vacuum for better maintenance
        "ALTER TABLE youtube_videos SET (autovacuum_enabled = true);",
        "ALTER TABLE reports SET (autovacuum_enabled = true);",
        
        # Set fill factor for tables that have updates
        "ALTER TABLE youtube_videos SET (fillfactor = 90);",  # Leave room for updates
    ]
    
    engine = postgress_db.ENGINE
    
    try:
        with engine.connect() as connection:
            for opt_sql in optimizations:
                try:
                    logger.info(f"Applying optimization: {opt_sql}")
                    connection.execute(text(opt_sql))
                    connection.commit()
                except Exception as e:
                    logger.warning(f"Failed to apply optimization (may require admin privileges): {str(e)}")
        
        logger.info("Finished applying database optimizations")
        
    except Exception as e:
        logger.error(f"Failed to apply optimizations: {str(e)}")


def run_migration():
    """Run all database optimizations."""
    logger.info("Starting database optimization migration")
    
    try:
        add_youtube_indexes()
        add_report_indexes()
        create_youtube_video_constraints()
        optimize_database_settings()
        
        logger.info("Database optimization migration completed successfully")
        
    except Exception as e:
        logger.error(f"Database optimization migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_migration()