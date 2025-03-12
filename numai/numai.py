from numai.ai_provider import  GenAIProvider
import json

class Numai:
    def __init__(self, ai: GenAIProvider, data_path: str, results_dir: str):
       self.ai = ai
       self.data_path = data_path
       self.results_dir = results_dir

    def process_local_pdf(self, filename: str):
        full_path = self._generate_local_file_path(filename)
        response = self.ai.pdf_numbers_local(full_path)
        resp = json.loads(response)
        self._save_response("results.json", resp)
        return response
        
    def _generate_local_file_path(self, filename: str) -> str:
        return f"{self.data_path}/{filename}"
    
    def _save_response(self, filename: str, response: dict):
        filepath = f"{self.results_dir}/{filename}"
        with open(filepath, 'w') as f:
            f.write(json.dumps(response))
