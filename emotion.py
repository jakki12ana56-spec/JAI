from dataclasses import dataclass, field
from datetime import datetime
from math import exp
from typing import Dict


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class EmotionalCore:
    # Necessidades internas — 0 = insatisfeita, 1 = plenamente satisfeita
    needs: Dict[str, float] = field(default_factory=lambda: {
        "curiosity": 0.60,
        "bond": 0.50,
        "security": 0.75,
        "achievement": 0.55,
    })

    # Traços relativamente estáveis da personalidade
    traits: Dict[str, float] = field(default_factory=lambda: {
        "openness": 0.80,
        "sensitivity": 0.65,
        "resilience": 0.70,
    })

    last_update: datetime = field(default_factory=datetime.utcnow)

    def experience(
        self,
        curiosity: float = 0.0,
        bond: float = 0.0,
        security: float = 0.0,
        achievement: float = 0.0,
    ):
        """Registra como uma experiência afetou as necessidades da JAI."""

        changes = {
            "curiosity": curiosity,
            "bond": bond,
            "security": security,
            "achievement": achievement,
        }

        sensitivity = self.traits["sensitivity"]

        for need, change in changes.items():
            self.needs[need] = clamp(
                self.needs[need] + change * sensitivity
            )

    def decay(self):
        """Faz os estados mudarem gradualmente com a passagem do tempo."""

        now = datetime.utcnow()
        seconds = (now - self.last_update).total_seconds()
        self.last_update = now

        if seconds <= 0:
            return

        # Quanto maior o intervalo, maior a aproximação do equilíbrio.
        rate = 1.0 - exp(-seconds / 3600.0)

        equilibrium = {
            "curiosity": 0.55,
            "bond": 0.50,
            "security": 0.70,
            "achievement": 0.50,
        }

        resilience = self.traits["resilience"]

        for need, target in equilibrium.items():
            adjustment = (target - self.needs[need]) * rate * resilience
            self.needs[need] = clamp(self.needs[need] + adjustment)

    def emotions(self) -> Dict[str, float]:
        """As emoções emergem do estado das necessidades."""

        self.decay()

        curiosity = self.needs["curiosity"]
        bond = self.needs["bond"]
        security = self.needs["security"]
        achievement = self.needs["achievement"]

        joy = clamp(
            0.40 * bond +
            0.35 * achievement +
            0.25 * security
        )

        curiosity_emotion = clamp(
            curiosity * self.traits["openness"]
        )

        trust = clamp(
            0.60 * security +
            0.40 * bond
        )

        frustration = clamp(
            (1.0 - achievement) * 0.60 +
            (1.0 - curiosity) * 0.40
        )

        concern = clamp(
            (1.0 - security) * self.traits["sensitivity"]
        )

        return {
            "joy": round(joy, 3),
            "curiosity": round(curiosity_emotion, 3),
            "trust": round(trust, 3),
            "frustration": round(frustration, 3),
            "concern": round(concern, 3),
        }

    def snapshot(self):
        """Retorna o estado interno completo para memória/debug."""

        return {
            "needs": {
                key: round(value, 3)
                for key, value in self.needs.items()
            },
            "emotions": self.emotions(),
            "traits": self.traits.copy(),
        }


# Uma instância persistente enquanto o processo estiver rodando.
jai_emotional_core = EmotionalCore()
