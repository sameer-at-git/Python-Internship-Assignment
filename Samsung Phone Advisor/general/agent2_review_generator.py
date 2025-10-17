import logging
import json
import time
import requests
from typing import Dict, Any, List
from config import OLLAMA_CONFIG

logger = logging.getLogger(__name__)

class Agent2ReviewGenerator:
    def __init__(self):
        self.ollama_url = OLLAMA_CONFIG['base_url']
        self.model_name = OLLAMA_CONFIG['model_name']
        self.temperature = OLLAMA_CONFIG['temperature']
        self.max_tokens = OLLAMA_CONFIG['max_tokens']
    
    def call_ollama(self, prompt: str, system_message: str = None) -> str:
        """Call Ollama API to generate response"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        if system_message:
            payload["system"] = system_message
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def create_single_phone_prompt(self, phone_data: Dict[str, Any], focus_area: str) -> str:
        """Create prompt for single phone specs"""
        prompt = f"""
Create a comprehensive and engaging review of the {phone_data['model_name']} smartphone.

PHONE SPECIFICATIONS:
{self.format_phone_specs(phone_data)}

WRITING REQUIREMENTS:
1. Start with an engaging introduction highlighting the phone's key selling points
2. Provide detailed analysis of the specifications in natural, conversational language
3. Focus particularly on {focus_area} aspects if relevant
4. Mention the target audience for this phone
5. Highlight standout features and any potential drawbacks
6. Keep the tone professional but accessible to general consumers
7. Use bullet points or structured paragraphs for readability
8. End with a concise summary

Format the response as a well-structured review that would be helpful for someone considering purchasing this phone.
"""
        return prompt
    
    def create_comparison_prompt(self, phones_data: List[Dict[str, Any]], focus_area: str, comparison_type: str) -> str:
        """Create prompt for phone comparison"""
        phones_specs = "\n\n".join([self.format_phone_specs(phone) for phone in phones_data])
        
        prompt = f"""
Compare these {len(phones_data)} Samsung smartphones with a focus on {focus_area}:

{phones_specs}

WRITING REQUIREMENTS:
1. Start with a brief introduction of both phones
2. Create a detailed comparison table or structured analysis of key differences
3. Focus particularly on {focus_area} performance and features
4. Highlight which phone excels in which areas
5. Discuss value for money and target audiences for each
6. Provide a clear recommendation based on different user needs
7. Use clear, objective language with specific data points
8. End with a summary of which phone might be better for different types of users

Make the comparison insightful and helpful for someone trying to decide between these phones.
"""
        return prompt
    
    def create_recommendation_prompt(self, phones_data: List[Dict[str, Any]], focus_area: str, criteria: List[str]) -> str:
        """Create prompt for recommendations"""
        phones_specs = "\n\n".join([self.format_phone_specs(phone) for phone in phones_data])
        
        prompt = f"""
Analyze these {len(phones_data)} Samsung smartphones and provide recommendations:

{phones_specs}

WRITING REQUIREMENTS:
1. Rank these phones based on {focus_area} and overall value
2. Focus on these criteria: {', '.join(criteria) if criteria else 'general performance'}
3. For each phone, highlight its strengths and ideal user profile
4. Provide clear recommendations for different budgets and needs
5. Mention any standout features or potential drawbacks
6. Use a structured format with clear rankings and justifications
7. Keep the tone helpful and informative for potential buyers
8. End with overall buying advice

Provide practical, actionable recommendations that help users make informed decisions.
"""
        return prompt
    
    def format_phone_specs(self, phone: Dict[str, Any]) -> str:
        """Format phone specifications for the prompt"""
        specs = []
        specs.append(f"MODEL: {phone.get('model_name', 'N/A')}")
        
        if phone.get('release_date'):
            specs.append(f"Release Date: {phone['release_date']}")
        
        # Display specs
        display_parts = []
        if phone.get('display_size_inches'):
            display_parts.append(f"{phone['display_size_inches']}''")
        if phone.get('display_type'):
            display_parts.append(phone['display_type'])
        if phone.get('display_resolution'):
            display_parts.append(phone['display_resolution'])
        if phone.get('display_refresh_rate_hz'):
            display_parts.append(f"{phone['display_refresh_rate_hz']}Hz")
        if display_parts:
            specs.append(f"Display: {', '.join(display_parts)}")
        
        # Performance specs
        if phone.get('processor'):
            specs.append(f"Processor: {phone['processor']}")
        if phone.get('ram_options_gb'):
            specs.append(f"RAM: {phone['ram_options_gb']} GB")
        if phone.get('storage_options_gb'):
            specs.append(f"Storage: {phone['storage_options_gb']} GB")
        
        # Camera specs
        camera_parts = []
        if phone.get('main_camera_mp'):
            camera_parts.append(f"Main: {phone['main_camera_mp']}MP")
            if phone.get('main_camera_aperture'):
                camera_parts[-1] += f" {phone['main_camera_aperture']}"
        if phone.get('ultrawide_camera_mp'):
            camera_parts.append(f"Ultra-wide: {phone['ultrawide_camera_mp']}MP")
        if phone.get('telephoto_camera_mp'):
            camera_parts.append(f"Telephoto: {phone['telephoto_camera_mp']}MP")
        if camera_parts:
            specs.append(f"Cameras: {', '.join(camera_parts)}")
        
        # Battery and other specs
        if phone.get('battery_mah'):
            specs.append(f"Battery: {phone['battery_mah']} mAh")
        if phone.get('has_5g') is not None:
            specs.append(f"5G: {'Yes' if phone['has_5g'] else 'No'}")
        if phone.get('ip_rating'):
            specs.append(f"IP Rating: {phone['ip_rating']}")
        if phone.get('android_version'):
            specs.append(f"Android: {phone['android_version']}")
        if phone.get('price_usd'):
            specs.append(f"Price: ${phone['price_usd']}")
        
        return "\n".join(specs)
    
    def get_system_message(self, intent: str) -> str:
        """Get appropriate system message for different intents"""
        base_message = "You are a professional smartphone reviewer with deep technical knowledge. You provide accurate, objective, and helpful information about mobile devices."
        
        intent_messages = {
            "single_phone": "Focus on providing comprehensive, detailed analysis of a single phone's features and performance.",
            "comparison": "Focus on objective comparison, highlighting differences and helping users understand which phone better suits specific needs.",
            "filter_search": "Focus on ranking and recommending phones based on specific criteria and value propositions.",
            "feature_query": "Focus on analyzing specific features across multiple phones and providing targeted recommendations.",
            "use_case_recommendation": "Focus on matching phones to specific user needs and use cases."
        }
        
        return f"{base_message} {intent_messages.get(intent, '')}"
    
    def generate_response(self, agent1_output: Dict[str, Any]) -> Dict[str, Any]:
        """Main method for Agent 2 - generate natural language response"""
        start_time = time.time()
        
        logger.info(f"Agent 2 generating response for intent: {agent1_output['intent']}")
        
        try:
            # Extract data from Agent 1 output
            rag_data = agent1_output['rag_data']
            intent = agent1_output['intent']
            additional_context = agent1_output['additional_context']
            phones_data = rag_data['matched_phones']
            
            # Create appropriate prompt based on intent
            if intent == "single_phone" and phones_data:
                prompt = self.create_single_phone_prompt(phones_data[0], additional_context['focus_area'])
            elif intent == "comparison" and len(phones_data) >= 2:
                prompt = self.create_comparison_prompt(phones_data, additional_context['focus_area'], additional_context['comparison_type'])
            else:
                prompt = self.create_recommendation_prompt(phones_data, additional_context['focus_area'], additional_context.get('user_criteria', []))
            
            # Get system message
            system_message = self.get_system_message(intent)
            
            # Call Ollama
            logger.info(f"Calling Ollama with {len(phones_data)} phones for {intent} intent")
            answer = self.call_ollama(prompt, system_message)
            
            # Calculate processing time
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            # Prepare response
            response = {
                "status": "success",
                "answer": answer,
                "query_type": intent,
                "phones_involved": [phone['model_name'] for phone in phones_data],
                "focus_area": additional_context['focus_area'],
                "confidence_score": rag_data['confidence'],
                "processing_time_ms": processing_time_ms,
                "metadata": {
                    "phones_analyzed": len(phones_data),
                    "llm_model": self.model_name,
                    "response_length": len(answer)
                }
            }
            
            logger.info(f"Agent 2 completed successfully. Generated {len(answer)} characters.")
            return response
            
        except Exception as e:
            logger.error(f"Agent 2 generation error: {e}")
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": "error",
                "error_type": "GENERATION_ERROR",
                "message": f"Error generating response: {str(e)}",
                "processing_time_ms": processing_time_ms,
                "fallback_data": self.create_fallback_response(agent1_output)
            }
    
    def create_fallback_response(self, agent1_output: Dict[str, Any]) -> str:
        """Create a fallback response if LLM fails"""
        phones_data = agent1_output['rag_data']['matched_phones']
        intent = agent1_output['intent']
        
        if intent == "single_phone" and phones_data:
            phone = phones_data[0]
            return f"The {phone['model_name']} features a {phone.get('display_size_inches', 'N/A')}-inch display, {phone.get('battery_mah', 'N/A')}mAh battery, and {phone.get('main_camera_mp', 'N/A')}MP main camera."
        
        elif intent == "comparison" and len(phones_data) >= 2:
            phone1, phone2 = phones_data[0], phones_data[1]
            return f"Comparing {phone1['model_name']} and {phone2['model_name']}: {phone1['model_name']} has {phone1.get('main_camera_mp', 'N/A')}MP camera vs {phone2.get('main_camera_mp', 'N/A')}MP, and {phone1.get('battery_mah', 'N/A')}mAh battery vs {phone2.get('battery_mah', 'N/A')}mAh."
        
        else:
            phone_names = [phone['model_name'] for phone in phones_data[:3]]
            return f"Based on your criteria, I found these phones: {', '.join(phone_names)}. Each offers different strengths in camera, battery, and performance."