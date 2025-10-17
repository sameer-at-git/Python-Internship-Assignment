import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.processed_data = []
    
    def validate_phone_data(self, phone_data: Dict[str, Any]) -> bool:
        """Validate phone data for required fields"""
        # Critical fields that must be present
        critical_fields = ['model_name', 'chipset', 'battery_capacity']
        
        for field in critical_fields:
            if not phone_data.get(field):
                logger.warning(f"Missing critical field '{field}' for {phone_data.get('model_name', 'Unknown')}")
                return False
        
        # Validate model name format
        model_name = phone_data.get('model_name', '')
        if not model_name or model_name == 'Unknown':
            logger.warning(f"Invalid model name: {model_name}")
            return False
        
        return True
    
    def clean_data_types(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and convert data types for PostgreSQL"""
        cleaned_data = phone_data.copy()
        
        # Convert numeric fields
        if cleaned_data.get('battery_capacity'):
            try:
                cleaned_data['battery_capacity'] = int(cleaned_data['battery_capacity'])
            except (ValueError, TypeError):
                cleaned_data['battery_capacity'] = None
        
        if cleaned_data.get('display_size'):
            try:
                cleaned_data['display_size'] = float(cleaned_data['display_size'])
            except (ValueError, TypeError):
                cleaned_data['display_size'] = None
        
        # Clean RAM and storage options
        if cleaned_data.get('ram_options'):
            cleaned_data['ram_options'] = [ram for ram in cleaned_data['ram_options'] if ram]
        
        if cleaned_data.get('storage_options'):
            cleaned_data['storage_options'] = [storage for storage in cleaned_data['storage_options'] if storage]
        
        # Convert 5G support to boolean
        if '5g_support' in cleaned_data:
            cleaned_data['5g_support'] = bool(cleaned_data['5g_support'])
        
        # Clean camera data
        for camera_type in ['main', 'ultra_wide', 'telephoto']:
            if camera_type in cleaned_data:
                if cleaned_data[camera_type].get('megapixels'):
                    try:
                        cleaned_data[camera_type]['megapixels'] = float(cleaned_data[camera_type]['megapixels'])
                    except (ValueError, TypeError):
                        cleaned_data[camera_type]['megapixels'] = None
        
        return cleaned_data
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate all phone data"""
        logger.info("Processing and validating scraped data...")
        
        valid_count = 0
        invalid_count = 0
        
        for phone in raw_data:
            if self.validate_phone_data(phone):
                cleaned_phone = self.clean_data_types(phone)
                self.processed_data.append(cleaned_phone)
                valid_count += 1
            else:
                invalid_count += 1
                logger.warning(f"Skipping invalid data for {phone.get('model_name', 'Unknown')}")
        
        logger.info(f"Processing completed. {valid_count} valid records, {invalid_count} invalid records")
        return self.processed_data
    
    def save_processed_data(self, filename="samsung_phones_processed.json"):
        """Save processed data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Processed data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")