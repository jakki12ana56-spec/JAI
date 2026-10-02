# JAI V1.1 — interface web

Agente comercial em **modo de simulação**, agora com interface para navegador/celular.

## O que faz
- Chat web responsivo para iPhone e computador.
- Português, francês e inglês.
- Memória de conversa em SQLite.
- Oferece serviços digitais legítimos e negocia valores simulados de €5 a €500.
- Registra orçamentos em `sales.jsonl` e mostra um painel de orçamentos.
- Checkout é apenas demonstração: **não aceita dinheiro**.
- Regras contra personificação, histórias falsas e pressão emocional.

## Rodar localmente
Requer Python 3.10+ e uma chave da OpenAI API.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua-chave"
python app.py
```

Abra `http://localhost:8080` no navegador.

## Segurança
Nunca coloque sua chave da API no HTML ou JavaScript. Ela deve ficar apenas no servidor/variáveis de ambiente.

## Próxima etapa
Publicar este servidor em uma hospedagem compatível com Python e configurar `OPENAI_API_KEY` lá. Só depois, quando a proprietária decidir, integrar um provedor de pagamentos reais.
