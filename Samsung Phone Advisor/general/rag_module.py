import psycopg2
import psycopg2.extras
import logging
import re
import time
from typing import List, Dict, Any, Tuple, Optional
from fuzzywuzzy import fuzz, process
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class RAGModule:
    def __init__(self):
        self.conn = None
        self.all_phone_models = []
        self.load_phone_models()
    
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
    
    def load_phone_models(self):
        """Load all phone model names for fuzzy matching"""
        if not self.connect():
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT model_name FROM phones")
            self.all_phone_models = [row[0] for row in cursor.fetchall()]
            logger.info(f"Loaded {len(self.all_phone_models)} phone models for fuzzy matching")
        except Exception as e:
            logger.error(f"Error loading phone models: {e}")
        finally:
            if self.conn:
                self.conn.close()
    
    def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """Classify user intent from natural language query"""
        query = user_query.lower().strip()
        
        # Intent patterns
        single_phone_patterns = [
            r'specs? of (.+)',
            r'details? of (.+)',
            r'what is (.+)',
            r'information about (.+)',
            r'tell me about (.+)'
        ]
        
        comparison_patterns = [
            r'compare (.+) and (.+)',
            r'comparison between (.+) and (.+)',
            r'difference between (.+) and (.+)',
            r'(.+) vs (.+)',
            r'(.+) versus (.+)'
        ]
        
        filter_patterns = [
            r'best.*battery.*under.*\$?(\d+)',
            r'phones?.*battery.*under.*\$?(\d+)',
            r'best.*camera',
            r'best.*display',
            r'best.*performance',
            r'cheap.*samsung',
            r'budget.*samsung'
        ]
        
        feature_query_patterns = [
            r'which.*best.*camera',
            r'which.*has.*best.*camera',
            r'best.*camera.*samsung',
            r'highest.*camera.*megapixel',
            r'best.*battery.*life',
            r'longest.*battery'
        ]
        
        use_case_patterns = [
            r'best.*for.*photography',
            r'best.*for.*gaming',
            r'best.*for.*business',
            r'best.*for.*students',
            r'recommend.*phone.*for',
            r'which.*should.*i.*buy.*for'
        ]
        
        # Check for single phone intent
        for pattern in single_phone_patterns:
            match = re.search(pattern, query)
            if match:
                return {
                    "intent": "single_phone",
                    "confidence": 0.9,
                    "extracted_entities": [match.group(1).strip()]
                }
        
        # Check for comparison intent
        for pattern in comparison_patterns:
            match = re.search(pattern, query)
            if match:
                return {
                    "intent": "comparison",
                    "confidence": 0.9,
                    "extracted_entities": [match.group(1).strip(), match.group(2).strip()]
                }
        
        # Check for filter-based search
        for pattern in filter_patterns:
            if re.search(pattern, query):
                return {
                    "intent": "filter_search",
                    "confidence": 0.8,
                    "extracted_entities": []
                }
        
        # Check for feature query
        for pattern in feature_query_patterns:
            if re.search(pattern, query):
                return {
                    "intent": "feature_query",
                    "confidence": 0.8,
                    "extracted_entities": []
                }
        
        # Check for use case recommendation
        for pattern in use_case_patterns:
            if re.search(pattern, query):
                return {
                    "intent": "use_case_recommendation",
                    "confidence": 0.8,
                    "extracted_entities": []
                }
        
        # Default to single phone if we can extract a phone name
        phone_models = self.extract_phone_models(query)
        if phone_models:
            return {
                "intent": "single_phone",
                "confidence": 0.7,
                "extracted_entities": phone_models
            }
        
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "extracted_entities": []
        }
    
    def extract_focus_area(self, user_query: str) -> str:
        """Extract the focus area from user query"""
        query = user_query.lower()
        
        focus_areas = {
            'photography': ['camera', 'photo', 'photography', 'picture', 'megapixel', 'aperture'],
            'battery': ['battery', 'charge', 'power', 'endurance', 'battery life'],
            'display': ['display', 'screen', 'resolution', 'refresh rate', 'amoled', 'lcd'],
            'performance': ['performance', 'speed', 'processor', 'chipset', 'ram', 'gaming'],
            'price': ['price', 'cost', 'budget', 'cheap', 'expensive', 'affordable'],
            'design': ['design', 'look', 'build', 'weight', 'dimensions', 'thin']
        }
        
        for area, keywords in focus_areas.items():
            if any(keyword in query for keyword in keywords):
                return area
        
        return "general"
    
    def fuzzy_match_phone(self, user_input: str, threshold: int = 80) -> List[Tuple[str, int]]:
        """Fuzzy match phone model names"""
        if not self.all_phone_models:
            return []
        
        # Preprocess user input
        user_input = user_input.strip().lower()
        
        # Try different matching strategies
        matches = []
        
        # Exact substring match
        for model in self.all_phone_models:
            if user_input in model.lower():
                matches.append((model, 100))
        
        # Fuzzy matching
        fuzzy_matches = process.extract(user_input, self.all_phone_models, 
                                      scorer=fuzz.partial_ratio, limit=10)
        
        # Combine and deduplicate
        for match, score in fuzzy_matches:
            if score >= threshold and not any(m[0] == match for m in matches):
                matches.append((match, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def extract_phone_models(self, user_query: str) -> List[str]:
        """Extract phone models from user query using fuzzy matching"""
        # Common phone patterns in user queries
        phone_patterns = [
            r's\d+\s*ultra',
            r's\d+\s*plus',
            r's\d+',
            r'galaxy\s*s\d+\s*ultra',
            r'galaxy\s*s\d+\s*plus',
            r'galaxy\s*s\d+',
            r'note\s*\d+',
            r'galaxy\s*note\s*\d+',
            r'z\s*flip',
            r'z\s*fold',
            r'galaxy\s*z\s*flip',
            r'galaxy\s*z\s*fold',
            r'a\d+\s*series',
            r'galaxy\s*a\d+'
        ]
        
        extracted_models = []
        
        # Find patterns in query
        for pattern in phone_patterns:
            matches = re.findall(pattern, user_query.lower())
            for match in matches:
                # Fuzzy match the found pattern
                fuzzy_matches = self.fuzzy_match_phone(match)
                if fuzzy_matches:
                    best_match = fuzzy_matches[0][0]
                    if best_match not in extracted_models:
                        extracted_models.append(best_match)
        
        # If no patterns found, try fuzzy matching the entire query
        if not extracted_models:
            fuzzy_matches = self.fuzzy_match_phone(user_query)
            if fuzzy_matches:
                extracted_models.append(fuzzy_matches[0][0])
        
        return extracted_models
    
    def build_sql_query(self, intent: str, entities: List[str], focus_area: str = "general") -> Tuple[str, List[Any]]:
        """Build SQL query based on intent and entities"""
        
        if intent == "single_phone":
            if entities:
                return "SELECT * FROM phones WHERE model_name = %s", [entities[0]]
        
        elif intent == "comparison":
            if len(entities) >= 2:
                placeholders = ', '.join(['%s'] * len(entities))
                return f"SELECT * FROM phones WHERE model_name IN ({placeholders})", entities
        
        elif intent == "filter_search":
            # Default query for best battery under budget
            return """
                SELECT * FROM phones 
                WHERE price_usd <= 1000 
                ORDER BY battery_mah DESC 
                LIMIT 10
            ", []
        
        elif intent == "feature_query":
            focus_area = focus_area.lower()
            if focus_area == "camera":
                return """
                    SELECT * FROM phones 
                    WHERE main_camera_mp IS NOT NULL 
                    ORDER BY main_camera_mp DESC 
                    LIMIT 5
                ", []
            elif focus_area == "battery":
                return """
                    SELECT * FROM phones 
                    WHERE battery_mah IS NOT NULL 
                    ORDER BY battery_mah DESC 
                    LIMIT 5
                ", []
            elif focus_area == "performance":
                return """
                    SELECT * FROM phones 
                    WHERE processor IS NOT NULL 
                    ORDER BY 
                        CASE 
                            WHEN processor LIKE '%Snapdragon 8%' THEN 1
                            WHEN processor LIKE '%Exynos%' THEN 2
                            ELSE 3
                        END,
                    battery_mah DESC 
                    LIMIT 5
                ", []
            else:
                return "SELECT * FROM phones ORDER BY price_usd DESC LIMIT 5", []
        
        elif intent == "use_case_recommendation":
            focus_area = focus_area.lower()
            if focus_area == "photography":
                return """
                    SELECT * FROM phones 
                    WHERE main_camera_mp IS NOT NULL AND ultrawide_camera_mp IS NOT NULL
                    ORDER BY main_camera_mp DESC, ultrawide_camera_mp DESC 
                    LIMIT 5
                ", []
            elif focus_area == "gaming":
                return """
                    SELECT * FROM phones 
                    WHERE display_refresh_rate_hz >= 120 AND battery_mah >= 4000
                    ORDER BY display_refresh_rate_hz DESC, battery_mah DESC 
                    LIMIT 5
                ", []
            elif focus_area == "business":
                return """
                    SELECT * FROM phones 
                    WHERE ram_options_gb @> ARRAY[8] OR ram_options_gb @> ARRAY[12]
                    ORDER BY array_length(ram_options_gb, 1) DESC, battery_mah DESC 
                    LIMIT 5
                ", []
            elif focus_area == "students":
                return """
                    SELECT * FROM phones 
                    WHERE price_usd <= 500 AND battery_mah >= 4000
                    ORDER BY price_usd ASC, battery_mah DESC 
                    LIMIT 5
                ", []
            else:
                return "SELECT * FROM phones ORDER BY price_usd DESC LIMIT 5", []
        
        # Default fallback query
        return "SELECT * FROM phones LIMIT 5", []
    
    def execute_query(self, query: str, params: List[Any]) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        if not self.connect():
            return []
        
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
        finally:
            if self.conn:
                self.conn.close()
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Main method to process user query and return structured data"""
        start_time = time.time()
        
        logger.info(f"Processing user query: {user_query}")
        
        # Step 1: Classify intent
        intent_result = self.classify_intent(user_query)
        intent = intent_result["intent"]
        entities = intent_result["extracted_entities"]
        confidence = intent_result["confidence"]
        
        logger.info(f"Detected intent: {intent} (confidence: {confidence})")
        logger.info(f"Extracted entities: {entities}")
        
        # Step 2: Extract focus area
        focus_area = self.extract_focus_area(user_query)
        logger.info(f"Focus area: {focus_area}")
        
        # Step 3: Handle fuzzy matching for phone models
        matched_phones = []
        if entities and intent in ["single_phone", "comparison"]:
            for entity in entities:
                fuzzy_matches = self.fuzzy_match_phone(entity)
                if fuzzy_matches:
                    best_match = fuzzy_matches[0][0]
                    matched_phones.append(best_match)
                    logger.info(f"Fuzzy matched '{entity}' -> '{best_match}'")
                else:
                    logger.warning(f"No fuzzy match found for '{entity}'")
        
        # Step 4: Build and execute SQL query
        if intent in ["single_phone", "comparison"] and matched_phones:
            query, params = self.build_sql_query(intent, matched_phones, focus_area)
        else:
            query, params = self.build_sql_query(intent, entities, focus_area)
        
        logger.info(f"Executing SQL query: {query} with params: {params}")
        results = self.execute_query(query, params)
        
        # Step 5: Prepare response
        query_time_ms = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "intent": intent,
            "matched_phones": results,
            "total_results": len(results),
            "focus_area": focus_area,
            "query_time_ms": query_time_ms,
            "confidence": confidence,
            "original_query": user_query
        }
        
        logger.info(f"Query completed in {query_time_ms}ms. Found {len(results)} results.")
        
        return response

# Example usage and testing
def test_rag_module():
    """Test the RAG module with sample queries"""
    rag = RAGModule()
    
    test_queries = [
        "What are the specs of Samsung Galaxy S23 Ultra?",
        "Compare Galaxy S23 Ultra and S22 Ultra for photography",
        "Which Samsung phone has the best battery under $1000?",
        "Which Samsung has best camera?",
        "Best Samsung for photography?",
        "Tell me about S23",
        "S23 vs S22 battery life",
        "Best gaming Samsung phone"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        result = rag.process_query(query)
        print(f"Intent: {result['intent']}")
        print(f"Focus Area: {result['focus_area']}")
        print(f"Results: {result['total_results']}")
        print(f"Confidence: {result['confidence']}")
        
        if result['matched_phones']:
            for phone in result['matched_phones'][:2]:  # Show first 2 phones
                print(f"  - {phone['model_name']}")

if __name__ == "__main__":
    test_rag_module()