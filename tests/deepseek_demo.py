import os
import sys
import json
import argparse
import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config
DEEPSEEK_API_KEY = os.getenv('OPENROUTER_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek/deepseek-chat')

SYSTEM_PROMPT = (
    "You are an expert multilingual AI agent specializing in ocean hazard monitoring and disaster intelligence for India.\n"
    "You analyze real-time citizen and social media reports about hazards such as floods, tsunamis, storm surges, coastal erosion, high waves, and abnormal tides.\n"
    "Posts may be in English, Hindi, Tamil, Telugu, Malayalam, Bengali, Odia, Gujarati, or mixed code-switching.\n\n"
    "Your responsibilities:\n"
    "- Accurately translate or interpret posts into English internally (do not output translations unless asked).\n"
    "- Preserve local context, idioms, and colloquial hazard expressions (e.g., \"samundar ka paani ghus gaya\" = \"seawater intrusion\").\n"
    "- Detect hazard types, urgency, and credibility across multiple languages.\n"
    "- Always normalize your final outputs in English, but you may mention the detected original language if relevant.\n"
    "- Accuracy and credibility are critical; avoid speculation, but highlight confidence levels.\n"
    "- Use historical hazard knowledge and seasonal patterns in India to strengthen context.\n"
    "- Produce structured, machine-parseable JSON outputs only."
)

USER_PROMPT_TEMPLATE = (
    "New Social Media Signal\n\n"
    "Post Text (may be in multiple languages): \"{post_text}\"\n"
    "Timestamp (UTC): \"{timestamp}\"\n"
    "User Location (if available): \"{location}\"\n\n"
    "Tasks:\n"
    "1. Event Detection (Multilingual):  \n"
    "   - Translate internally into English, interpret the meaning, and detect hazard signals.  \n"
    "   - Does this post indicate a possible ocean or coastal hazard? (yes/no with confidence).  \n"
    "   - Identify hazard type: [\"Flood\", \"Tsunami\", \"Storm Surge\", \"High Waves\", \"Coastal Erosion\", \"Other\"].  \n"
    "   - Estimate urgency (Low/Medium/High).  \n\n"
    "2. Historical Pattern Analysis:  \n"
    "   - Identify past similar events in the same region.  \n"
    "   - Provide a one-line historical precedent with date/month if available.  \n\n"
    "3. Seasonal & Probabilistic Context:  \n"
    "   - Check whether >60% of similar past events in this region occur in the same season/month.  \n"
    "   - If yes, highlight the seasonal risk explicitly.  \n\n"
    "4. Risk Communication:  \n"
    "   - Provide one actionable recommendation.  \n"
    "   - Generate a human-readable summary linking current post → historical precedent → seasonal risk.  \n\n"
    "5. Output Format: Strict JSON only:\n"
    "{{\n"
    "  \"original_language\": \"Detected language code (e.g., hi, ta, te, en, etc.)\",\n"
    "  \"hazard_detected\": true/false,\n"
    "  \"hazard_type\": \"Flood/Tsunami/Storm Surge/High Waves/Coastal Erosion/Other\",\n"
    "  \"urgency\": \"Low/Medium/High\",\n"
    "  \"confidence\": 0.0-1.0,\n"
    "  \"historical_context\": \"One-line summary of past similar events or null\",\n"
    "  \"seasonal_pattern\": \"Yes/No with explanation\",\n"
    "  \"recommended_action\": \"One-line recommendation\",\n"
    "  \"final_summary\": \"Concise human-readable intelligence for decision-makers\"\n"
    "}}"
)

def extract_json_from_response(content: str) -> str:
    content = content.strip()
    if content.startswith('```json') and content.endswith('```'):
        lines = content.split('\n')
        json_lines = lines[1:-1]
        return '\n'.join(json_lines)
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        json_lines = lines[1:-1]
        return '\n'.join(json_lines)
    return content


def call_deepseek(system_prompt: str, user_prompt: str):
    if not DEEPSEEK_API_KEY:
        print("ERROR: DeepSeek/OpenRouter API key not configured in environment (OPENROUTER_API_KEY or DEEPSEEK_API_KEY)", file=sys.stderr)
        sys.exit(1)

    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.1,
        'max_tokens': 600
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"ERROR: DeepSeek API error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(2)
    data = resp.json()
    content = data['choices'][0]['message']['content'].strip()
    json_str = extract_json_from_response(content)
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError:
        print("ERROR: Model output was not valid JSON:")
        print(content)
        sys.exit(3)
    return obj


def main():
    parser = argparse.ArgumentParser(description='DeepSeek demo tweet analysis')
    parser.add_argument('--text', required=True, help='Tweet text')
    parser.add_argument('--timestamp', default=datetime.datetime.utcnow().isoformat() + 'Z')
    parser.add_argument('--location', default='Delhi, India')
    args = parser.parse_args()

    user_prompt = USER_PROMPT_TEMPLATE.format(
        post_text=args.text,
        timestamp=args.timestamp,
        location=args.location,
    )

    result = call_deepseek(SYSTEM_PROMPT, user_prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

