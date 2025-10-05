from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
# from src.utilities.logger import Logger
# from src.utilities.redis_cache import RedisHandler
from dotenv import load_dotenv
from opik import configure
from opik.integrations.langchain import OpikTracer
from opik import track
import asyncio
import redis 
import os
import time
import json
import opik



load_dotenv()
configure(api_key=os.getenv('OPIK_API_KEY'))
# logger = Logger.getLogger(__name__)

class GroqLLMService:

    def __init__(self):
        self.opik_tracer = OpikTracer(project_name='Wikipedia_QA', metadata={'service_provider': 'groq_llms'})
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model_name = 'openai/gpt-oss-20b'  # Example model name, replace with actual if different
        self.llm = ChatGroq(model=self.model_name, temperature=0.7, api_key=self.api_key)
        self.temperature = 0.7  # Default temperature setting for response variability
        self.redis = redis.asyncio.Redis(host='localhost', port=6379, db=0, 
                                        username=os.getenv('REDIS_USERNAME'),
                                        password=os.getenv('REDIS_PASSWORD'),
                                        decode_responses=True)
        
        # self.redis = RedisHandler().getRedis()
        self.redis = redis.asyncio.Redis(host='localhost', port=6379, db=0, 
                                        username=os.getenv('REDIS_USERNAME'),
                                        password=os.getenv('REDIS_PASSWORD'),
                                        decode_responses=True)
        
    # @opik.track(name='generate_response', metadata={"used_for": "generating response"})
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

            # direct query to llm
            llm_agent = create_react_agent(model=self.llm, tools=[])
            response = await llm_agent.ainvoke(input={'messages': [{"role": "system", "content": system_prompt},
                                                                {"role": "user", "content": user_prompt}]},
                                                config={'configurable' : {'verbose': True},
                                                         "callbacks": [self.opik_tracer]})
            
            # caching the responses
            json.dumps((system_prompt, user_prompt))
            await self.redis.set(cache_key, json.dumps(response['messages'][2].__dict__))
            return response
        
        except Exception as exec:
            print(f"Error generating response from Groq LLM: {exec}")
            raise exec
    


    async def getStreaming(self, user_prompt:str):
        try:
            stream = self.llm.astream(input=[{"role":"system", "content": self.system_prompt, 
                                              "role": "user", "content": user_prompt}],
                                            stream=True)
            
            return stream


        except Exception as exec:
            print(f"error while getting streaming object: {exec}")
            raise exec 


    # @opik.track(project_name="Wikipedia_QA", name='querying_llm', metadata={"used_for": "querying llms"})
    async def query_llm(self, system_prompt: str, user_prompt: str):
        try:
            
            prompt = ChatPromptTemplate(messages=[("system", system_prompt),
                                                  ("user", user_prompt)])
            
            chain = prompt | self.llm

            # cache check
            cache_key = json.dumps((system_prompt, user_prompt))
            if await self.redis.exists(cache_key):
                return await self.redis.get(cache_key)
            
            # direct query to llm
            response = await self.llm.ainvoke(input=[{"role": "system", "content": system_prompt},
                                                {"role": "user", "content": user_prompt}],)
                                                # config={'callbacks': [self.opik_tracer]})

            response = chain.ainvoke({}, config={"callbacks": [self.opik_tracer]})

            
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
    


