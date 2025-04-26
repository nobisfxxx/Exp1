import os
import logging
import sys

# ===== BASIC CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Immediate startup log
        logger.info("🚀 Container started - Beginning initialization")
        
        # Check critical environment variables
        logger.info("🔍 Checking environment variables")
        assert os.getenv("INSTA_USERNAME"), "INSTA_USERNAME not set"
        assert os.getenv("INSTA_PASSWORD"), "INSTA_PASSWORD not set"
        logger.info("✅ Environment variables verified")
        
        # Test dependencies
        logger.info("🔍 Testing dependencies")
        from instagrapi import Client
        logger.info("✅ Dependencies loaded successfully")
        
        # Basic Instagram connection
        logger.info("Attempting Instagram connection")
        cl = Client()
        cl.login(os.getenv("INSTA_USERNAME"), os.getenv("INSTA_PASSWORD"))
        logger.info("✅ Instagram connection successful")
        
        # Main loop
        while True:
            logger.info("🤖 Bot operational - Listening for messages")
            time.sleep(10)
            
    except Exception as e:
        logger.critical(f"💀 Critical failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
