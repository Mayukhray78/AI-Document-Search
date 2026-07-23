from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN


class LLMService:

    def __init__(self):
        if not HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is missing. Add it to the .env file."
            )

        self.client = InferenceClient(
            provider="auto",
            api_key=HF_TOKEN,
        )

        self.model = "Qwen/Qwen3-8B"

    def generate_answer(
        self,
        question: str,
        context: list[str],
    ) -> str:

        if not context:
            return "I could not find relevant information in the uploaded documents."

        context_text = "\n\n".join(context)

        prompt = f"""
/no_think

Answer the question using only the provided document context.

If the answer is not available in the context, say:
"I could not find that information in the uploaded documents."

Document context:
{context_text}

Question:
{question}

Provide a clear and concise answer.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=500,
            temperature=0.2,
        )

        answer = response.choices[0].message.content

        if not answer:
            return "The language model did not return an answer."

        return answer.strip()