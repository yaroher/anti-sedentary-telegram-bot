from __future__ import annotations

from pydantic import BaseModel


class FlavorLocale(BaseModel):
    title: str
    description: str
    phrases: list[str]


class Flavor(BaseModel):
    key: str
    locales: dict[str, FlavorLocale]

    def for_locale(self, locale: str, fallback: str = "en") -> FlavorLocale:
        return self.locales.get(locale) or self.locales[fallback]


FLAVORS: dict[str, Flavor] = {
    "soft": Flavor(
        key="soft",
        locales={
            "ru": FlavorLocale(
                title="Мягкий",
                description="Поддерживающий тон без токсичности.",
                phrases=[
                    "Пора немного оживить тело. Маленький шаг лучше нуля.",
                    "Давай короткую разминку. Твоей спине понравится.",
                    "Встань на пару минут. Это инвестиция в нормальное самочувствие.",
                ],
            ),
            "en": FlavorLocale(
                title="Soft",
                description="Supportive tone, no toxicity.",
                phrases=[
                    "Time to wake the body up. A small step beats zero.",
                    "Quick warm-up — your back will thank you.",
                    "Stand for a couple of minutes. Investment in feeling normal.",
                ],
            ),
        },
    ),
    "normal": Flavor(
        key="normal",
        locales={
            "ru": FlavorLocale(
                title="Нормальный",
                description="Настойчивый, но дружелюбный.",
                phrases=[
                    "Стул опять пытается тебя усыновить. Встаём.",
                    "Перерыв на движение. Не обсуждается, просто делаем.",
                    "Тело не мебель. У тебя короткое задание.",
                ],
            ),
            "en": FlavorLocale(
                title="Normal",
                description="Persistent but friendly.",
                phrases=[
                    "The chair is trying to adopt you again. Stand up.",
                    "Movement break. Not negotiable, just do it.",
                    "Body isn't furniture. Short task incoming.",
                ],
            ),
        },
    ),
    "warden": Flavor(
        key="warden",
        locales={
            "ru": FlavorLocale(
                title="Надзиратель",
                description="Наглый, смешной, давящий, но без оскорблений.",
                phrases=[
                    "Офисный гриб, подъём. У тебя миссия.",
                    "Ты не статуя. Выполняй задание, потом спорь.",
                    "Командование объявляет анти-стуловую операцию. Пошёл.",
                ],
            ),
            "en": FlavorLocale(
                title="Warden",
                description="Cheeky, pushy, no insults.",
                phrases=[
                    "Office mushroom, on your feet. Mission time.",
                    "You're not a statue. Do the task, argue later.",
                    "Anti-chair operation commencing. Move.",
                ],
            ),
        },
    ),
}

DEFAULT_FLAVOR = "normal"
