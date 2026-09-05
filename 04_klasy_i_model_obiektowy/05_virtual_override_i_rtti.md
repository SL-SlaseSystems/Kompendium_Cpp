[← Spis treści](../README.md)

# virtual, override i RTTI

Wirtualna funkcja składowa umożliwia dynamic dispatch. Standard opisuje zachowanie semantycznie; typowy vtable i ukryty vptr są detalem ABI, nie obowiązkową reprezentacją języka. Koszt obejmuje zwykle pośrednie wywołanie i możliwość utrudnienia inline, ale decyzję wydajnościową należy oprzeć na profilu.

~~~cpp
#include <cassert>
#include <string_view>

struct Event {
    virtual ~Event() = default;
    [[nodiscard]] virtual std::string_view kind() const noexcept = 0;
};

struct Click final : Event {
    [[nodiscard]] std::string_view kind() const noexcept override {
        return "click";
    }
};

int main() {
    Click click;
    Event& event = click;
    assert(event.kind() == "click");
    assert(dynamic_cast<Click*>(&event) != nullptr);
}
~~~

`dynamic_cast` może bezpiecznie wykonać downcast w polimorficznej hierarchii. Dla wskaźnika niepowodzenie daje `nullptr`, dla referencji rzuca `std::bad_cast`. Częste downcasty mogą sugerować, że brakuje operacji w interfejsie albo lepszy byłby `variant`.

`typeid` i `dynamic_cast` tworzą RTTI. Niektóre projekty wyłączają RTTI flagą implementacji, ale wtedy nie jest to już standardowy, niezmieniony model C++. Nie zastępuj systemu typów ręcznymi liczbowymi identyfikatorami bez konkretnej potrzeby ABI lub serializacji.

Domyślny argument funkcji wirtualnej jest wybierany statycznie na podstawie typu wyrażenia, podczas gdy ciało funkcji — dynamicznie. To zaskakujące połączenie, dlatego unikaj domyślnych argumentów w wirtualnym API. Private virtual jest dozwolone i wspiera idiom NVI, w którym publiczna niewirtualna metoda pilnuje kontraktu.

## Jak to działa krok po kroku

Wywołanie `event.kind()` najpierw podlega zwykłym regułom wyszukiwania i sprawdzania dostępności. Kompilator widzi interfejs typu statycznego `Event&`, znajduje funkcję wirtualną, a wykonanie wybiera jej final overrider dla faktycznego obiektu. Nie ma obowiązku istnienia tablicy o określonym układzie. Optymalizator może nawet ustalić typ i usunąć pośrednie wywołanie, zachowując tę samą semantykę.

`override` każe sprawdzić, czy deklaracja rzeczywiście nadpisuje odziedziczoną funkcję. Różnica w końcowym `const`, kwalifikatorze referencyjnym lub typach parametrów może zamiast tego stworzyć inną funkcję. Bez `override` literówka potrafi przejść kompilację i zostawić aktywną implementację bazy. `final` na funkcji zabrania dalszego nadpisywania, a na klasie zabrania dalszego dziedziczenia.

Przy `dynamic_cast<Click*>(&event)` sprawdzany jest rzeczywisty układ publicznych, jednoznacznych relacji w obiekcie. Sukces daje poprawnie dostosowany wskaźnik do żądanej części. Niepowodzenie sprawdzanego rzutowania wskaźnikowego daje `nullptr`, dlatego dostęp musi być uzależniony od wyniku. Rzutowanie referencyjne wyraża silniejsze oczekiwanie i sygnalizuje brak dopasowania wyjątkiem `std::bad_cast`.

## Pogłębienie mechanizmu

Sprawdzany downcast i crosscast wymagają polimorficznego typu źródłowego, czyli klasy z co najmniej jedną funkcją wirtualną. Prosty upcast może być poprawny bez RTTI. Crosscast pozwala przejść między dwiema bazami tego samego najbardziej pochodnego obiektu, jeżeli spełnione są reguły dostępu i jednoznaczności. `static_cast` w dół hierarchii nie wykonuje tej kontroli; wymaga, aby obiekt rzeczywiście spełniał założenie.

`typeid` dla glvalue typu polimorficznego informuje o typie dynamicznym. Dla niepolimorficznego obiektu daje typ statyczny. Gdy argument jest polimorficznym dereferencjonowaniem pustego wskaźnika, `typeid(*p)` ma szczególną regułę zgłoszenia `std::bad_typeid`. Nie należy z tego wyprowadzać ogólnego pozwolenia na dereferencję `nullptr` w innych wyrażeniach.

Wynik `type_info::name()` jest zależny od implementacji i nie jest stabilnym identyfikatorem do pliku, protokołu ani bazy danych. Nazwa może być zakodowana zgodnie z ABI i zmienić się po przebudowaniu. Porównanie `typeid(a) == typeid(b)` bada równość informacji o typach, ale nie zastępuje relacji „ten typ da się użyć jako wskazany interfejs”. Do tej relacji pasuje odpowiedni `dynamic_cast`.

Nadpisywana funkcja może mieć kowariantny wynik będący wskaźnikiem lub referencją do odpowiednio powiązanej klasy. Ta reguła nie obejmuje automatycznie `unique_ptr<Derived>` jako zamiennika `unique_ptr<Base>`. Szablony smart pointerów są różnymi klasami, więc typ wyniku wirtualnej fabryki zwykle musi pozostać dokładnie wspólnym typem właściciela.

Wywołanie kwalifikowane, na przykład `object.Base::operation()`, celowo pomija dispatch wirtualny i wskazuje implementację bazy. Zwykłe wywołanie w konstruktorze bazy również nie dociera do części pochodnej, lecz z innego powodu: obowiązuje etap konstrukcji. Nie używaj wirtualnej metody jako sposobu wymuszenia zachowania gotowej klasy pochodnej przed zakończeniem jej tworzenia.

## Drugi przykład

Argument domyślny jest wybierany w miejscu wywołania, natomiast ciało funkcji może zależeć od typu dynamicznego. Program pokazuje oba wybory osobno oraz sprawdzony dostęp do dodatkowego typu.

~~~cpp
#include <cassert>
#include <typeinfo>

struct Base {
    virtual ~Base() = default;
    virtual int calculate(int value = 1) const { return value; }
};
struct Derived final : Base {
    int calculate(int value = 7) const override { return value * 10; }
};
struct Other final : Base {};

int main() {
    Derived object;
    Base& base = object;
    assert(base.calculate() == 10);
    assert(object.calculate() == 70);
    assert(typeid(base) == typeid(Derived));
    assert(dynamic_cast<Derived*>(&base) == &object);
    assert(dynamic_cast<Other*>(&base) == nullptr);
}
~~~

W obu pierwszych wywołaniach działa ciało `Derived::calculate`. Różnią się argumenty dołączone z deklaracji widocznej przez typ statyczny. To poprawne zachowanie języka, lecz zwykle niepotrzebnie zaskakujące API. Publiczna niewirtualna metoda z jedną polityką argumentów może delegować do prywatnej metody wirtualnej.

## Porównanie i decyzje

Używaj `override` przy każdym świadomym nadpisaniu. `final` stosuj, gdy zamknięcie rozszerzania jest częścią projektu, nie jako obietnicę konkretnego przyspieszenia. RTTI jest użyteczne przy opcjonalnych możliwościach obiektu i integracji z istniejącą hierarchią. Jeśli każda operacja zaczyna się od długiej listy downcastów, rozważ wspólną funkcję wirtualną, visitor albo zamknięty wariant.

**Ćwiczenie.** Baza deklaruje `virtual int value() const;`, a pochodna `int value();`. Czy druga funkcja nadpisuje pierwszą?

**Odpowiedź.** Nie, ponieważ różni się kwalifikacją obiektu. Dodanie `override` ujawni błąd. Jeśli intencją było nadpisanie, należy dopisać `const` w pochodnej; jeśli nowa operacja, trzeba świadomie rozważyć również przesłonięcie nazw z bazy.

Źródła: [reguły override](https://timsong-cpp.github.io/cppwp/n4950/class.virtual), [dynamic_cast](https://timsong-cpp.github.io/cppwp/n4950/expr.dynamic.cast), [typeid](https://timsong-cpp.github.io/cppwp/n4950/expr.typeid).

## Powiązane tematy

- [Dziedziczenie i polimorfizm](04_dziedziczenie_i_polimorfizm.md)
- [NVI](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)
- [ABI i visibility](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

