from num_extract.numai import Numai
from num_extract.config import get_settings
from num_extract.ai_provider import GeminiProvider
from num_extract.numinternal import process_local_pdf
import typer


def bootstrap():
    settings = get_settings()
    ai = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        prompt=settings.prompt,
    )

    return Numai(
        ai,
        settings.data_dir,
        settings.results_dir
    )


def main(filename: str, mode: str = "internal"):
    """
    Process a PDF and get the max number from the file.

    Args:
        filename (str): name of the file to process
        mode (str, optional): The mode to run in internal or ai. Defaults to internal Can Also use ai.
    """
    # "FY25 Air Force Working Capital Fund.pdf"
    numai = bootstrap()

    if mode == "internal":
        print(process_local_pdf(filename))
    elif mode == "ai":
        print(numai.process_local_pdf(filename))

if __name__ == "__main__":
    typer.run(main)
