from numai.numai import Numai
from numai.config import get_settings
from numai.ai_provider import GeminiProvider


def bootstrap():
    settings = get_settings()
    ai = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        prompt=settings.prompt,
    )

    return Numai(ai, settings.data_dir, settings.results_dir)


if __name__ == "__main__":
    numai = bootstrap()
    print(numai.process_local_pdf("FY25 Air Force Working Capital Fund.pdf"))
