import os
import getpass
from dotenv import load_dotenv  # Add this import
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq



class LLMResponseAgent:
    def __init__(self):
        load_dotenv()
        if "GROQ_API_KEY" not in os.environ:
            os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")
        self.llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
    
    def get_response(self, user_query, agent_1_result):
        prompt_template = PromptTemplate(
            input_variables=["user_query", "agent_1_result"],
            template=(
                "You are a helpful assistant specializing in mobile phone specifications. "
                "A user asked: {user_query}\n\n"
                "Here is the data from the database: {agent_1_result}\n\n"
                "Please provide a helpful response in natural language using this information. "
                "If the data doesn't contain the information needed, kindly inform the user."
            )
        )
        
        formatted_prompt = prompt_template.format(
            user_query=user_query, 
            agent_1_result=str(agent_1_result)  # Convert to string to avoid serialization issues
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content