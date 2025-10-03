import os 
import yaml


class ConstantsFetcher:

    with open("/home/user/Projects/AdvancedRagChatbot/src/resources/constants.yaml", 'r') as f:
        constants = yaml.safe_load(f)

    @staticmethod
    def fetch_constants(key: str):
        return ConstantsFetcher.constants[key]
    

    