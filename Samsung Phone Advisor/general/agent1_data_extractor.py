import logging
import json
from typing import Dict, Any, List, Optional
from rag_module import RAGModule

logger = logging.getLogger(__name__)

class Agent1DataExtractor:
    def __init__(self):
        self.rag = RAGModule()
        self.required_fields = {
            'single_phone': ['model_name', 'display_size_inches', 'battery_mah', 'main_camera_mp'],
            'comparison': ['model_name', 'display_size_inches', 'battery_mah', 'main_camera_mp'],
            'filter_search': ['model_name', 'battery_mah', 'price_usd', 'main_camera_mp'],
            'feature_query': ['model_name', 'main_camera_mp', 'battery_mah'],
            'use_case_recommendation': ['model_name', 'main_camera_mp', 'battery_mah', 'price_usd']
        }
    
    def validate_rag_data(self, rag_data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Validate that the RAG data contains required fields"""
        validation_result = {
            'is_valid': True,
            'missing_fields': {},
            'phones_with_issues': []
        }
        
        if not rag_data.get('matched_phones'):
            validation_result['is_valid'] = False
            validation_result['missing_fields']['global'] = 'No phones found'
            return validation_result
        
        required_fields = self.required_fields.get(intent, [])
        
        for i, phone in enumerate(rag_data['matched_phones']):
            phone_issues = []
            for field in required_fields:
                if field not in phone or phone[field] is None:
                    phone_issues.append(field)
            
            if phone_issues:
                validation_result['phones_with_issues'].append({
                    'model_name': phone.get('model_name', f'Phone_{i}'),
                    'missing_fields': phone_issues
                })
        
        if validation_result['phones_with_issues']:
            validation_result['is_valid'] = False
        
        return validation_result
    
    def handle_error_scenarios(self, rag_data: Dict[str, Any], intent: str, user_query: str) -> Optional[Dict[str, Any]]:
        """Handle various error scenarios"""
        
        # No phones found
        if not rag_data.get('matched_phones'):
            # Try to find similar phones
            similar_phones = self.rag.fuzzy_match_phone(user_query, threshold=60)
            suggestion = None
            if similar_phones:
                suggestion = f"Try '{similar_phones[0][0]}' or '{similar_phones[1][0]}'" if len(similar_phones) > 1 else f"Try '{similar_phones[0][0]}'"
            
            return {
                "status": "error",
                "error_type": "NO_MATCH",
                "message": f"No phones found matching your query",
                "suggestion": suggestion,
                "original_query": user_query
            }
        
        # Multiple matches for single phone query
        if intent == "single_phone" and len(rag_data['matched_phones']) > 1:
            phone_names = [phone['model_name'] for phone in rag_data['matched_phones'][:3]]
            return {
                "status": "error", 
                "error_type": "MULTIPLE_MATCHES",
                "message": f"Multiple phones found matching your query",
                "matches": phone_names,
                "suggestion": "Please specify which phone you meant",
                "original_query": user_query
            }
        
        # Data validation issues
        validation = self.validate_rag_data(rag_data, intent)
        if not validation['is_valid']:
            return {
                "status": "error",
                "error_type": "INCOMPLETE_DATA",
                "message": "Some phone data is incomplete",
                "validation_issues": validation,
                "original_query": user_query
            }
        
        return None
    
    def extract_additional_context(self, rag_data: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Extract additional context for Agent 2"""
        focus_area = rag_data.get('focus_area', 'general')
        
        # Determine comparison type
        comparison_type = None
        if rag_data['intent'] == 'comparison':
            if len(rag_data['matched_phones']) == 2:
                comparison_type = 'two_phones'
            else:
                comparison_type = 'multiple_phones'
        
        # Extract filters from query
        filters_applied = {}
        query_lower = user_query.lower()
        
        if 'under' in query_lower and '$' in query_lower:
            price_match = re.search(r'\$(\d+)', user_query)
            if price_match:
                filters_applied['max_price'] = int(price_match.group(1))
        
        if 'best' in query_lower:
            if 'battery' in query_lower:
                filters_applied['sort_by'] = 'battery'
            elif 'camera' in query_lower:
                filters_applied['sort_by'] = 'camera'
        
        return {
            "focus_area": focus_area,
            "comparison_type": comparison_type,
            "filters_applied": filters_applied,
            "user_criteria": self.extract_user_criteria(user_query)
        }
    
    def extract_user_criteria(self, user_query: str) -> List[str]:
        """Extract specific criteria mentioned by user"""
        criteria = []
        query_lower = user_query.lower()
        
        criteria_keywords = {
            'battery': ['battery', 'charge', 'power', 'endurance'],
            'camera': ['camera', 'photo', 'picture', 'megapixel', 'aperture'],
            'display': ['display', 'screen', 'resolution', 'refresh rate', 'amoled'],
            'performance': ['performance', 'speed', 'processor', 'ram', 'fast'],
            'price': ['price', 'cost', 'budget', 'cheap', 'expensive', 'affordable'],
            'design': ['design', 'look', 'build', 'weight', 'thin', 'sleek']
        }
        
        for criterion, keywords in criteria_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                criteria.append(criterion)
        
        return criteria
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Main method for Agent 1 - process user query and extract data"""
        logger.info(f"Agent 1 processing query: {user_query}")
        
        try:
            # Step 1: Call RAG module
            rag_data = self.rag.process_query(user_query)
            
            # Step 2: Handle error scenarios
            error_response = self.handle_error_scenarios(rag_data, rag_data['intent'], user_query)
            if error_response:
                logger.warning(f"Agent 1 error: {error_response['error_type']}")
                return error_response
            
            # Step 3: Extract additional context
            additional_context = self.extract_additional_context(rag_data, user_query)
            
            # Step 4: Prepare success response
            response = {
                "status": "success",
                "intent": rag_data['intent'],
                "rag_data": rag_data,
                "additional_context": additional_context,
                "processing_metadata": {
                    "phones_found": len(rag_data['matched_phones']),
                    "confidence": rag_data['confidence'],
                    "query_time_ms": rag_data['query_time_ms']
                }
            }
            
            logger.info(f"Agent 1 completed successfully. Found {len(rag_data['matched_phones'])} phones.")
            return response
            
        except Exception as e:
            logger.error(f"Agent 1 processing error: {e}")
            return {
                "status": "error",
                "error_type": "PROCESSING_ERROR",
                "message": f"Error processing query: {str(e)}",
                "original_query": user_query
            }

# Import required for error handling
import re