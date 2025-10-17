import logging
import time
from typing import Dict, Any
from agent1_data_extractor import Agent1DataExtractor
from agent2_review_generator import Agent2ReviewGenerator

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.agent1 = Agent1DataExtractor()
        self.agent2 = Agent2ReviewGenerator()
    
    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """Orchestrate the complete flow from user query to final response"""
        start_time = time.time()
        
        logger.info(f"Orchestrator processing query: {user_query}")
        
        try:
            # Step 1: Agent 1 - Data Extraction
            agent1_start = time.time()
            agent1_result = self.agent1.process_query(user_query)
            agent1_time = round((time.time() - agent1_start) * 1000, 2)
            
            # If Agent 1 encountered an error, return early
            if agent1_result['status'] == 'error':
                total_time = round((time.time() - start_time) * 1000, 2)
                return {
                    "status": "error",
                    "error_details": agent1_result,
                    "total_processing_time_ms": total_time,
                    "agent1_time_ms": agent1_time,
                    "agent2_time_ms": 0
                }
            
            # Step 2: Agent 2 - Review Generation
            agent2_start = time.time()
            agent2_result = self.agent2.generate_response(agent1_result)
            agent2_time = round((time.time() - agent2_start) * 1000, 2)
            
            # Calculate total time
            total_time = round((time.time() - start_time) * 1000, 2)
            
            # Extract phone names for response
            phone_names = [phone['model_name'] for phone in agent1_result['rag_data']['matched_phones']]
            
            # Prepare final response
            response = {
                "status": "success",
                "response": agent2_result.get('answer', ''),
                "metadata": {
                    "intent": agent1_result['intent'],
                    "focus_area": agent1_result['additional_context']['focus_area'],
                    "phones_analyzed": len(agent1_result['rag_data']['matched_phones']),
                    "phones_analyzed_names": phone_names,
                    "confidence": agent1_result['rag_data']['confidence'],
                    "processing_times": {
                        "total_ms": total_time,
                        "agent1_ms": agent1_time,
                        "agent2_ms": agent2_time,
                        "rag_ms": agent1_result['rag_data']['query_time_ms']
                    }
                }
            }
            
            logger.info(f"Orchestrator completed successfully. Total time: {total_time}ms")
            return response
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            total_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": "error",
                "error_type": "ORCHESTRATION_ERROR",
                "message": f"System error: {str(e)}",
                "total_processing_time_ms": total_time
            }