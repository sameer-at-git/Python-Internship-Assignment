import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from urllib.parse import urljoin
import re
from config import *

logger = logging.getLogger(__name__)

class GSMArenaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_data = []
    
    def make_request_with_retry(self, url, max_retries=MAX_RETRIES):
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Request attempt {attempt + 1} for {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {max_retries} attempts failed for {url}")
                    raise
    
    def get_phone_links(self):
        """Extract links to individual phone pages from Samsung listing"""
        logger.info("Fetching Samsung phones listing...")
        
        try:
            response = self.make_request_with_retry(SAMSUNG_URL)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main phones listing
            phones_section = soup.find('div', class_='makers')
            if not phones_section:
                logger.error("Could not find phones section")
                return []
            
            phone_links = []
            for link in phones_section.find_all('a', href=True):
                phone_url = urljoin(BASE_URL, link['href'])
                phone_links.append(phone_url)
                
                if len(phone_links) >= MAX_PHONES:
                    break
            
            logger.info(f"Found {len(phone_links)} phone links")
            return phone_links
            
        except Exception as e:
            logger.error(f"Error fetching phone links: {e}")
            return []
    
    def extract_spec_value(self, soup, spec_name):
        """Helper function to extract specification values"""
        try:
            # Find the spec row by name
            spec_row = soup.find('td', string=re.compile(f'^{spec_name}$', re.IGNORECASE))
            if spec_row:
                value_cell = spec_row.find_next_sibling('td')
                if value_cell:
                    return value_cell.get_text(strip=True)
            return None
        except Exception as e:
            logger.debug(f"Error extracting {spec_name}: {e}")
            return None
    
    def parse_ram_storage(self, text):
        """Parse RAM and storage options from text"""
        if not text:
            return [], []
        
        ram_options = []
        storage_options = []
        
        # Common patterns for RAM and storage
        ram_pattern = r'(\d+)\s*GB\s*RAM'
        storage_pattern = r'(\d+)\s*GB\s*storage'
        
        ram_matches = re.findall(ram_pattern, text, re.IGNORECASE)
        storage_matches = re.findall(storage_pattern, text, re.IGNORECASE)
        
        ram_options = [f"{ram}GB" for ram in ram_matches]
        storage_options = [f"{storage}GB" for storage in storage_matches]
        
        return ram_options, storage_options
    
    def parse_camera_specs(self, soup):
        """Extract camera specifications"""
        cameras = {
            'main': {'megapixels': None, 'aperture': None},
            'ultra_wide': {'megapixels': None},
            'telephoto': {'megapixels': None}
        }
        
        try:
            # Find camera section
            camera_section = soup.find('span', string=re.compile('MAIN CAMERA', re.IGNORECASE))
            if camera_section:
                camera_table = camera_section.find_parent('table')
                if camera_table:
                    rows = camera_table.find_all('tr')
                    
                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')
                        if th and td:
                            camera_text = td.get_text()
                            
                            # Main camera
                            if 'main' in th.get_text().lower() or 'wide' in th.get_text().lower():
                                # Extract megapixels
                                mp_match = re.search(r'(\d+(?:\.\d+)?)\s*MP', camera_text)
                                if mp_match:
                                    cameras['main']['megapixels'] = mp_match.group(1)
                                
                                # Extract aperture
                                aperture_match = re.search(r'f/(\d+(?:\.\d+)?)', camera_text)
                                if aperture_match:
                                    cameras['main']['aperture'] = f"f/{aperture_match.group(1)}"
                            
                            # Ultra-wide camera
                            elif 'ultra' in th.get_text().lower() or 'wide' in th.get_text().lower():
                                mp_match = re.search(r'(\d+(?:\.\d+)?)\s*MP', camera_text)
                                if mp_match:
                                    cameras['ultra_wide']['megapixels'] = mp_match.group(1)
                            
                            # Telephoto camera
                            elif 'tele' in th.get_text().lower() or 'zoom' in th.get_text().lower():
                                mp_match = re.search(r'(\d+(?:\.\d+)?)\s*MP', camera_text)
                                if mp_match:
                                    cameras['telephoto']['megapixels'] = mp_match.group(1)
        
        except Exception as e:
            logger.debug(f"Error parsing camera specs: {e}")
        
        return cameras
    
    def parse_display_info(self, soup):
        """Extract display information"""
        display = {
            'size': None,
            'type': None,
            'resolution': None,
            'refresh_rate': None
        }
        
        try:
            display_text = self.extract_spec_value(soup, 'Display')
            if display_text:
                # Size
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*inches', display_text)
                if size_match:
                    display['size'] = size_match.group(1)
                
                # Type
                if 'AMOLED' in display_text.upper():
                    display['type'] = 'AMOLED'
                elif 'OLED' in display_text.upper():
                    display['type'] = 'OLED'
                elif 'LCD' in display_text.upper():
                    display['type'] = 'LCD'
                
                # Resolution
                resolution_match = re.search(r'(\d+\s*x\s*\d+)', display_text)
                if resolution_match:
                    display['resolution'] = resolution_match.group(1)
                
                # Refresh rate
                refresh_match = re.search(r'(\d+)\s*Hz', display_text)
                if refresh_match:
                    display['refresh_rate'] = refresh_match.group(1)
        
        except Exception as e:
            logger.debug(f"Error parsing display info: {e}")
        
        return display
    
    def parse_phone_specs(self, soup, phone_url):
        """Parse all specifications from a phone page"""
        specs = {}
        
        try:
            # Model name
            title_section = soup.find('h1', class_='specs-phone-name-title')
            if title_section:
                specs['model_name'] = title_section.get_text(strip=True)
            else:
                specs['model_name'] = "Unknown"
            
            # Release date
            specs['release_date'] = self.extract_spec_value(soup, 'Announced')
            
            # Display information
            display_info = self.parse_display_info(soup)
            specs.update(display_info)
            
            # Chipset/Processor
            specs['chipset'] = self.extract_spec_value(soup, 'Chipset')
            
            # RAM and Storage
            internal_storage = self.extract_spec_value(soup, 'Internal')
            ram_options, storage_options = self.parse_ram_storage(internal_storage)
            specs['ram_options'] = ram_options
            specs['storage_options'] = storage_options
            
            # Battery
            battery_text = self.extract_spec_value(soup, 'Battery')
            if battery_text:
                battery_match = re.search(r'(\d+)\s*mAh', battery_text)
                if battery_match:
                    specs['battery_capacity'] = int(battery_match.group(1))
            
            # Camera specifications
            camera_specs = self.parse_camera_specs(soup)
            specs.update(camera_specs)
            
            # 5G support
            technology_text = self.extract_spec_value(soup, 'Technology')
            specs['5g_support'] = '5G' in technology_text if technology_text else False
            
            # IP rating
            body_text = self.extract_spec_value(soup, 'Body')
            if body_text:
                ip_match = re.search(r'IP(\d+)', body_text)
                if ip_match:
                    specs['ip_rating'] = f"IP{ip_match.group(1)}"
            
            # Dimensions and weight
            specs['dimensions'] = self.extract_spec_value(soup, 'Dimensions')
            specs['weight'] = self.extract_spec_value(soup, 'Weight')
            
            # Android version
            os_text = self.extract_spec_value(soup, 'OS')
            if os_text:
                android_match = re.search(r'Android\s*(\d+(?:\.\d+)*)', os_text)
                if android_match:
                    specs['android_version'] = android_match.group(1)
            
            # URL for reference
            specs['source_url'] = phone_url
            
            logger.info(f"Successfully parsed: {specs['model_name']}")
            return specs
            
        except Exception as e:
            logger.error(f"Error parsing phone specs: {e}")
            return None
    
    def has_critical_data(self, phone_specs):
        """Check if phone has critical data"""
        critical_fields = ['model_name', 'chipset', 'battery_capacity']
        return all(phone_specs.get(field) for field in critical_fields)
    
    def scrape_phones(self):
        """Main method to scrape all phones"""
        logger.info("Starting GSMArena scraper...")
        
        phone_links = self.get_phone_links()
        if not phone_links:
            logger.error("No phone links found")
            return []
        
        successful_scrapes = 0
        skipped_phones = 0
        
        for i, phone_url in enumerate(phone_links, 1):
            try:
                logger.info(f"Scraping phone {i}/{len(phone_links)}: {phone_url}")
                
                response = self.make_request_with_retry(phone_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                phone_specs = self.parse_phone_specs(soup, phone_url)
                
                if phone_specs:
                    if self.has_critical_data(phone_specs):
                        self.scraped_data.append(phone_specs)
                        successful_scrapes += 1
                        logger.info(f"✓ Successfully scraped: {phone_specs['model_name']}")
                    else:
                        skipped_phones += 1
                        logger.warning(f"⚠ Skipping {phone_specs.get('model_name', 'Unknown')} - missing critical data")
                else:
                    skipped_phones += 1
                    logger.warning(f"✗ Failed to parse phone: {phone_url}")
                
                # Rate limiting
                if i < len(phone_links):
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                skipped_phones += 1
                logger.error(f"❌ Error scraping {phone_url}: {e}")
                continue
        
        logger.info(f"Scraping completed. Successfully scraped {successful_scrapes} phones, skipped {skipped_phones} phones")
        return self.scraped_data
    
    def save_to_json(self, filename="samsung_phones_raw.json"):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")