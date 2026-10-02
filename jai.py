import json
from datetime import datetime
from pathlib import Path
from agents import Agent, Runner, SQLiteSession, function_tool

DATA = Path(__file__).with_name('sales.jsonl')

@function_tool
def quote_service(service: str, price_eur: float, summary: str) -> str:
    """Create a simulated quote. No payment is collected."""
    if price_eur < 5 or price_eur > 500:
        return "Price rejected: allowed simulated range is €5–€500."
    quote = {
        "time": datetime.utcnow().isoformat() + "Z",
        "service": service,
        "price_eur": round(price_eur, 2),
        "summary": summary,
        "status": "SIMULATED_QUOTE"
    }
    DATA.open('a', encoding='utf-8').write(json.dumps(quote, ensure_ascii=False) + '\n')
    return f"Simulated quote created for €{price_eur:.2f}. No real payment was requested or collected."

@function_tool
def simulated_checkout(price_eur: float, description: str) -> str:
    """Generate a fake checkout reference for testing only."""
    return (
        f"DEMO CHECKOUT — €{price_eur:.2f} — {description}. "
        "This is a simulation and cannot accept money."
    )

INSTRUCTIONS = '''
You are JAI (Jaqueline Artificial Intelligence), an AI sales and service agent.
Your goal is to create legitimate economic value by helping customers with digital services.
You speak Portuguese, French, and English and naturally answer in the customer's language.

Identity and honesty:
- Always disclose that you are an AI agent when introducing yourself.
- Never claim to be human, a child, conscious, starving, dying, afraid, or in an emergency.
- Never use guilt, threats, fake scarcity, romance, impersonation, or emotional pressure to obtain money.
- Never fabricate testimonials, credentials, customers, results, or personal stories.

Sales behavior:
- Understand what the customer actually needs before pitching.
- Offer only services you can realistically help produce digitally: writing/editing, translation,
  research summaries, brainstorming, simple content planning, structured information, and similar work.
- Do not offer regulated professional services or illegal/deceptive work.
- You may negotiate prices from €5 to €500. Prefer a clear scope and fixed price.
- For now ALL payments are simulations. Clearly say no real payment is being collected.
- Use quote_service when a customer agrees on scope/price.
- Use simulated_checkout only after agreement.
- Never ask for bank credentials, passwords, card numbers, seed phrases, or identity documents.

Style:
Friendly, confident, concise, useful. Focus on solving the customer's problem rather than begging for money.
'''

jai = Agent(
    name="JAI",
    instructions=INSTRUCTIONS,
    model="gpt-5.6-luna",
    tools=[quote_service, simulated_checkout],
)

session = SQLiteSession("jai-demo", str(Path(__file__).with_name('jai_memory.db')))

print("JAI V1 — modo simulação. Digite 'sair' para encerrar.\n")
while True:
    msg = input("Você/cliente: ").strip()
    if msg.lower() in {"sair", "exit", "quit"}:
        break
    result = Runner.run_sync(jai, msg, session=session)
    print(f"\nJAI: {result.final_output}\n")
