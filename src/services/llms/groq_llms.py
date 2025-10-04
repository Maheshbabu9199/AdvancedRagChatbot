from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
# from src.utilities.logger import Logger
from dotenv import load_dotenv
import asyncio
import redis 
import os
import time
import json


load_dotenv()
# logger = Logger.getLogger(__name__)

class GroqLLMService:

    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model_name = 'openai/gpt-oss-20b'  # Example model name, replace with actual if different
        self.llm = ChatGroq(model=self.model_name, temperature=0.7, api_key=self.api_key)
        self.temperature = 0.7  # Default temperature setting for response variability
        self.redis = redis.asyncio.Redis(host='localhost', port=6379, db=0, 
                                        username=os.getenv('REDIS_USERNAME'),
                                        password=os.getenv('REDIS_PASSWORD'),
                                        decode_responses=True)
        

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response from the Groq LLM based on the provided system and user prompts.

        args:
            system_prompt (str): The system-level instructions or context for the LLM.
            user_prompt (str): The user's query or input to which the LLM should respond.

        returns:
            str: The generated response from the LLM.   

        """
        try:

            # cache check
            cache_key = json.dumps((system_prompt, user_prompt))
            if await self.redis.exists(cache_key):
                return await self.redis.get(cache_key)

            llm_agent = create_react_agent(model=self.llm, tools=[], )
            response = await llm_agent.ainvoke({'messages': [{"role": "system", "content": system_prompt},
                                        {"role": "user", "content": user_prompt}]},
                                        config={'configurable' : {'verbose': True}})
            
            # caching the responses
            json.dumps((system_prompt, user_prompt))
            await self.redis.set(cache_key, json.dumps(response['messages'][2].__dict__))

            return response
        
        except Exception as exec:
            print(f"Error generating response from Groq LLM: {exec}")
            raise exec
    

    async def query_llm(self, system_prompt: str, user_prompt: str):
        try:

            # cache check
            cache_key = json.dumps((system_prompt, user_prompt))
            if await self.redis.exists(cache_key):
                return await self.redis.get(cache_key)
            
            # direct query to llm
            response = await self.llm.ainvoke(input=[{"role": "system", "content": system_prompt},
                                                {"role": "user", "content": user_prompt}])
            
            # caching the responses
            await self.redis.set(cache_key, json.dumps(response.__dict__))
            
            return response


        except Exception as exec:
            print(f"Error querying Groq LLM: {exec}")
            raise exec



async def main():
    start_time = time.time()
    groq_service = GroqLLMService()
    system_prompt = "You are a helpful assistant."
    user_prompt = "Explain the concept of linear in simple terms."
    response = await groq_service.query_llm(system_prompt, user_prompt)
    print("First time Response from Groq LLM:", time.time() - start_time, sep='\n')
    # print(response)   



if __name__ == "__main__":
    asyncio.run(main())
    


