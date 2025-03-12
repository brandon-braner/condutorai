from abc import ABC, abstractmethod
from google import genai
from google.genai import types

from numextract.schemas.response import ResponseModel


class GenAIProvider(ABC):
    def __init__(self, api_key: str, model: str, prompt: str):
        self.model = model
        self.client = genai.Client(api_key=api_key)
        self.prompt = prompt

    @abstractmethod
    def pdf_numbers_local(self, pdf_path: str) -> str:
        pass


class GeminiProvider(GenAIProvider):
    def __init__(self, api_key: str, model: str, prompt: str):
        self.model = model
        self.client = genai.Client(api_key=api_key)
        self.prompt = prompt

    def pdf_numbers_local(self, file_path: str) -> str:
        file = self.client.files.upload(file=file_path)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[file, self.prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': ResponseModel,
            },
        )
        
        return response.text
