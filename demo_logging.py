"""
Demo script to demonstrate the logging system functionality
"""

from logging_system.logger import Logger
from models.config_models import LoggingConfig


def main():
    """Demonstrate logging system features"""
    
    # Create logging configuration
    config = LoggingConfig(
        log_level='DEBUG',
        log_file='logs/demo.log',
        max_log_size=10485760,  # 10MB
        backup_count=5
    )
    
    # Create logger
    logger = Logger(config, name="DemoLogger")
    
    print("=" * 60)
    print("Logging System Demo")
    print("=" * 60)
    print()
    
    # Demonstrate different log levels
    print("1. Logging at different levels:")
    logger.debug("This is a DEBUG message - detailed information for debugging")
    logger.info("This is an INFO message - general information")
    logger.warning("This is a WARNING message - something to be aware of")
    logger.error("This is an ERROR message - something went wrong")
    logger.critical("This is a CRITICAL message - serious problem")
    print()
    
    # Demonstrate error logging with exception
    print("2. Logging an error with exception information:")
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError:
        logger.error("Division by zero error occurred", exc_info=True)
    print()
    
    # Demonstrate structured logging
    print("3. Logging structured information:")
    logger.info("Processing declaration: tax_code=2300782217, declaration_number=308010891440")
    logger.info("Barcode retrieved successfully for declaration 308010891440")
    logger.warning("Duplicate file detected: 2300782217_308010891440.pdf")
    print()
    
    print("=" * 60)
    print("Check logs/demo.log to see the logged messages")
    print("=" * 60)
    
    # Close handlers
    for handler in logger.get_logger().handlers[:]:
        handler.close()
        logger.get_logger().removeHandler(handler)


if __name__ == "__main__":
    main()
