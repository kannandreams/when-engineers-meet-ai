import dis


class Animal:
    def speak(self):
        print("Animal sound")


class Dog(Animal):
    def speak(self):
        print("Woof!")


# Dynamic lookup at runtime
a = Dog()  # Declared type and actual type: Dog

# Lookup order:
# 1. Look in Dog.__dict__ → finds speak()
# 2. If not found, walks up MRO to Animal.__dict__
a.speak()


# Disassembling to see dynamic method resolution
def call_speak():
    a = Animal()
    a.speak()  # Base class call

    d = Dog()
    d.speak()  # Overridden method call


dis.dis(call_speak)
