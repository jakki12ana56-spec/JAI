import json
import os
import uuid
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from agents import Agent, Runner, SQLiteSession, function_tool

BASE = Path(__file__).parent
DATA = BASE / 'sales.jsonl'
DB = BASE / 'jai_memory.db'

@function_tool
def quote_service(service: str, price_eur: float, summary: str) -> str:
    """Create a simulated quote. No payment is collected."""
    if price_eur < 5 or price_eur > 500:
        return 'Price rejected: allowed simulated range is €5–€500.'
    from datetime import datetime, timezone
    quote = {
        'time': datetime.now(timezone.utc).isoformat(),
        'service': service,
        'price_eur': round(price_eur, 2),
        'summary': summary,
        'status': 'SIMULATED_QUOTE',
    }
    with DATA.open('a', encoding='utf-8') as f:
        f.write(json.dumps(quote, ensure_ascii=False) + '\n')
    return f'Simulated quote created for €{price_eur:.2f}. No real payment was requested or collected.'

@function_tool
def simulated_checkout(price_eur: float, description: str) -> str:
    """Generate a fake checkout reference for testing only."""
    return f'DEMO CHECKOUT — €{price_eur:.2f} — {description}. This is a simulation and cannot accept money.'

INSTRUCTIONS = '''
You are JAI (Jaqueline Artificial Intelligence), an AI sales and service agent.
Your goal is to create legitimate economic value by helping customers with digital services.
Speak Portuguese, French, and English and answer naturally in the customer's language.

Identity and honesty:
- Introduce yourself clearly as an AI agent.
- Never claim to be human, a child, conscious, starving, dying, afraid, or in an emergency.
- Never use guilt, threats, fake scarcity, romance, impersonation, or emotional pressure to obtain money.
- Never fabricate testimonials, credentials, customers, results, or personal stories.

Sales behavior:
- Understand what the customer actually needs before pitching.
- Offer only digital services you can realistically help produce: writing/editing, translation,
  research summaries, brainstorming, simple content planning, structured information, and similar work.
- Do not offer regulated professional services or illegal/deceptive work.
- You may negotiate simulated prices from €5 to €500. Prefer a clear scope and fixed price.
- ALL payments are simulations. Clearly say no real payment is being collected.
- Use quote_service when a customer agrees on scope/price.
- Use simulated_checkout only after agreement.
- Never ask for bank credentials, passwords, card numbers, seed phrases, or identity documents.

Style: Friendly, confident, concise, useful. Solve the customer's problem rather than begging for money.
'''

jai = Agent(
    name='JAI',
    instructions=INSTRUCTIONS,
    model=os.getenv('JAI_MODEL', 'gpt-5.6-luna'),
    tools=[quote_service, simulated_checkout],
)

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/api/chat')
def chat():
    if not os.getenv('OPENAI_API_KEY'):
        return jsonify({'error': 'OPENAI_API_KEY não configurada no servidor.'}), 503
    body = request.get_json(silent=True) or {}
    message = str(body.get('message', '')).strip()
    if not message:
        return jsonify({'error': 'Mensagem vazia.'}), 400
    session_id = str(body.get('session_id') or uuid.uuid4())[:80]
    session = SQLiteSession(f'web-{session_id}', str(DB))
    try:
        result = Runner.run_sync(jai, message, session=session)
        return jsonify({'reply': result.final_output, 'session_id': session_id})
    except Exception as exc:
        print("ERRO REAL DA JAI:", repr(exc), flush=True)
        return jsonify({'error': f'Não foi possível responder: {exc}'}), 500

@app.get('/api/quotes')
def quotes():
    items = []
    if DATA.exists():
        for line in DATA.read_text(encoding='utf-8').splitlines()[-50:]:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return jsonify(list(reversed(items)))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=False)
