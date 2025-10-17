import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Any
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"]
            )
            return True
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL database: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables in PostgreSQL"""
        if not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Create phones table with the specified schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phones (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(255) NOT NULL UNIQUE,
                    release_date DATE,
                    display_size_inches FLOAT,
                    display_type VARCHAR(50),
                    display_resolution VARCHAR(100),
                    display_refresh_rate_hz INTEGER,
                    processor VARCHAR(100),
                    ram_options_gb INTEGER[],
                    storage_options_gb INTEGER[],
                    battery_mah INTEGER,
                    main_camera_mp FLOAT,
                    main_camera_aperture VARCHAR(10),
                    ultrawide_camera_mp FLOAT,
                    telephoto_camera_mp FLOAT,
                    price_usd FLOAT,
                    has_5g BOOLEAN,
                    ip_rating VARCHAR(10),
                    dimensions_mm VARCHAR(50),
                    weight_g FLOAT,
                    android_version VARCHAR(20),
                    source_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_name ON phones (model_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_battery_mah ON phones (battery_mah)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_usd ON phones (price_usd)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_main_camera_mp ON phones (main_camera_mp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_battery ON phones (price_usd, battery_mah)')
            
            self.conn.commit()
            logger.info("PostgreSQL tables and indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    def insert_phone_data(self, phone_data: Dict[str, Any]) -> bool:
        """Insert phone data into PostgreSQL database"""
        if not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Convert data types for PostgreSQL
            ram_options = [int(ram.replace('GB', '').strip()) for ram in phone_data.get('ram_options', []) if ram.replace('GB', '').strip().isdigit()]
            storage_options = [int(storage.replace('GB', '').strip()) for storage in phone_data.get('storage_options', []) if storage.replace('GB', '').strip().isdigit()]
            
            # Convert camera megapixels to float
            main_camera_mp = float(phone_data.get('main', {}).get('megapixels')) if phone_data.get('main', {}).get('megapixels') else None
            ultrawide_camera_mp = float(phone_data.get('ultra_wide', {}).get('megapixels')) if phone_data.get('ultra_wide', {}).get('megapixels') else None
            telephoto_camera_mp = float(phone_data.get('telephoto', {}).get('megapixels')) if phone_data.get('telephoto', {}).get('megapixels') else None
            
            # Convert display size to float
            display_size = float(phone_data.get('display_size')) if phone_data.get('display_size') else None
            
            # Convert battery to integer
            battery_mah = int(phone_data.get('battery_capacity')) if phone_data.get('battery_capacity') else None
            
            # Extract weight in grams
            weight_g = None
            if phone_data.get('weight'):
                weight_match = re.search(r'(\d+)\s*g', phone_data.get('weight'))
                if weight_match:
                    weight_g = float(weight_match.group(1))
            
            # Insert data
            cursor.execute('''
                INSERT INTO phones (
                    model_name, release_date, display_size_inches, display_type,
                    display_resolution, display_refresh_rate_hz, processor,
                    ram_options_gb, storage_options_gb, battery_mah,
                    main_camera_mp, main_camera_aperture, ultrawide_camera_mp,
                    telephoto_camera_mp, has_5g, ip_rating, dimensions_mm,
                    weight_g, android_version, source_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (model_name) DO UPDATE SET
                    release_date = EXCLUDED.release_date,
                    display_size_inches = EXCLUDED.display_size_inches,
                    display_type = EXCLUDED.display_type,
                    display_resolution = EXCLUDED.display_resolution,
                    display_refresh_rate_hz = EXCLUDED.display_refresh_rate_hz,
                    processor = EXCLUDED.processor,
                    ram_options_gb = EXCLUDED.ram_options_gb,
                    storage_options_gb = EXCLUDED.storage_options_gb,
                    battery_mah = EXCLUDED.battery_mah,
                    main_camera_mp = EXCLUDED.main_camera_mp,
                    main_camera_aperture = EXCLUDED.main_camera_aperture,
                    ultrawide_camera_mp = EXCLUDED.ultrawide_camera_mp,
                    telephoto_camera_mp = EXCLUDED.telephoto_camera_mp,
                    has_5g = EXCLUDED.has_5g,
                    ip_rating = EXCLUDED.ip_rating,
                    dimensions_mm = EXCLUDED.dimensions_mm,
                    weight_g = EXCLUDED.weight_g,
                    android_version = EXCLUDED.android_version,
                    source_url = EXCLUDED.source_url,
                    updated_at = NOW()
            ''', (
                phone_data.get('model_name'),
                phone_data.get('release_date'),
                display_size,
                phone_data.get('display_type'),
                phone_data.get('display_resolution'),
                phone_data.get('display_refresh_rate'),
                phone_data.get('chipset'),
                ram_options,
                storage_options,
                battery_mah,
                main_camera_mp,
                phone_data.get('main', {}).get('aperture'),
                ultrawide_camera_mp,
                telephoto_camera_mp,
                phone_data.get('5g_support'),
                phone_data.get('ip_rating'),
                phone_data.get('dimensions'),
                weight_g,
                phone_data.get('android_version'),
                phone_data.get('source_url')
            ))
            
            self.conn.commit()
            logger.info(f"Inserted/Updated data for: {phone_data['model_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting phone data: {e}")
            self.conn.rollback()
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    # Add this method to the DatabaseManager class

    def get_phone_count(self) -> int:
        if not self.connect():
            return 0
    
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM phones")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error getting phone count: {e}")
            return 0
        finally:
            if self.conn:
                self.conn.close()

    def get_all_phones(self) -> List[Dict[str, Any]]:
        """Retrieve all phones from database"""
        if not self.connect():
            return []
        
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cursor.execute('''
                SELECT * FROM phones ORDER BY model_name
            ''')
            
            phones = []
            for row in cursor.fetchall():
                phones.append(dict(row))
            
            return phones
            
        except Exception as e:
            logger.error(f"Error retrieving phones: {e}")
            return []
        finally:
            if self.conn:
                self.conn.close()