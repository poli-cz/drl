import os

# load .env if present
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from openai import AzureOpenAI


class GPTReasoner:
    """
    Minimal Azure OpenAI reasoner.

    Requires env vars (or pass explicitly):
      - AZURE_OPENAI_API_KEY
      - AZURE_OPENAI_ENDPOINT   (e.g. https://lakmoosgpt.openai.azure.com/)
      - AZURE_OPENAI_API_VERSION (e.g. 2024-12-01-preview)
      - AZURE_OPENAI_DEPLOYMENT  (e.g. Lakmoos-gpt4-o)
    """

    def __init__(
        self,
        model: str = None,  # kept for compatibility; ignored by Azure (deployment is used)
        api_key: str = None,
        endpoint: str = None,
        api_version: str = None,
        deployment: str = None,
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
        )
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if not self.api_key:
            raise ValueError("Missing AZURE_OPENAI_API_KEY")
        if not self.endpoint:
            raise ValueError(
                "Missing AZURE_OPENAI_ENDPOINT (e.g. https://lakmoosgpt.openai.azure.com/)"
            )
        if not self.deployment:
            raise ValueError("Missing AZURE_OPENAI_DEPLOYMENT (e.g. Lakmoos-gpt4-o)")

        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
        )

    def reason(
        self, prompt: str, system: str = "You are a cybersecurity reasoning engine."
    ) -> str:
        resp = self.client.chat.completions.create(
            model=self.deployment,  # Azure uses deployment name here
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        return resp.choices[0].message.content
