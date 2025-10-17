#!/usr/bin/env python3
"""
Main script to run the GSMArena Samsung phone scraper
"""

import logging
from scraper import GSMArenaScraper
from data_processor import DataProcessor
from database import DatabaseManager
import json
import os

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Samsung Phone Scraper...")
    
    try:
        # Step 1: Scrape data from GSMArena
        logger.info("Step 1: Scraping data from GSMArena...")
        scraper = GSMArenaScraper()
        raw_data = scraper.scrape_phones()
        
        if not raw_data:
            logger.error("No data scraped. Exiting.")
            return
        
        # Save raw data
        scraper.save_to_json("samsung_phones_raw.json")
        
        # Step 2: Process and validate data
        logger.info("Step 2: Processing and validating data...")
        processor = DataProcessor()
        processed_data = processor.process_data(raw_data)
        
        if not processed_data:
            logger.error("No valid data after processing. Exiting.")
            return
        
        # Save processed data
        processor.save_processed_data("samsung_phones_processed.json")
        
        # Step 3: Store in database
        logger.info("Step 3: Storing data in database...")
        db_manager = DatabaseManager()
        
        successful_inserts = 0
        for phone_data in processed_data:
            if db_manager.insert_phone_data(phone_data):
                successful_inserts += 1
        
        logger.info(f"Successfully stored {successful_inserts} phones in database")
        
        # Step 4: Display summary
        logger.info("Step 4: Generating summary...")
        all_phones = db_manager.get_all_phones()
        logger.info(f"Total phones in database: {len(all_phones)}")
        
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Phones scraped: {len(raw_data)}")
        print(f"Valid phones processed: {len(processed_data)}")
        print(f"Successfully stored in DB: {successful_inserts}")
        print(f"Raw data saved to: samsung_phones_raw.json")
        print(f"Processed data saved to: samsung_phones_processed.json")
        print(f"Database file: samsung_phones.db")
        
        # Display first few phones as sample
        if all_phones:
            print("\nSample of scraped phones:")
            for i, phone in enumerate(all_phones[:3], 1):
                print(f"{i}. {phone['model_name']}")
        
        print("\nScraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()