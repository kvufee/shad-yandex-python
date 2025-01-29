class Cat:
    def say(self) -> str:
        return "meow"


class Dog:
    def say(self, what: str = "woof") -> str:
        return what


class Cow:
    def talk(self) -> str:
        return "moo"
