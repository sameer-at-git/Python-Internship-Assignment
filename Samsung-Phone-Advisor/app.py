from agent_1 import call_logic
from agent_2 import LLMResponseAgent

if __name__ == "__main__":
    user_query = input("Ask about Samsung phones: ")
    logic_result = call_logic(user_query)  
    llm_agent = LLMResponseAgent()         
    response = llm_agent.get_response(user_query, logic_result)
    print(response)