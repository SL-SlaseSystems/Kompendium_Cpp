[← Spis treści](../README.md)

# Value semantics i type erasure

Typ ma value semantics, gdy jego kopia zachowuje się jak niezależna wartość, udostępnione porównanie opisuje znaczenie logiczne, a zasoby są szczegółem implementacji. `std::string` i `std::vector` są typowymi przykładami. Value semantics upraszcza lokalne rozumowanie, testy i współbieżność, bo ownership jest jasny.

~~~cpp
#include <cassert>
#include <functional>
#include <string>
#include <utility>

class Formatter {
public:
    template<class F>
    Formatter(F function) : function_{std::move(function)} {}

    std::string operator()(int value) const {
        return function_(value);
    }

private:
    std::function<std::string(int)> function_;
};

int main() {
    Formatter formatter{[](int value) { return std::to_string(value); }};
    assert(formatter(42) == "42");
}
~~~

`std::function` wykonuje type erasure: klient widzi jednolitą sygnaturę, a konkretny typ lambdy jest ukryty. Może używać small-buffer optimization, ale standard nie gwarantuje dokładnego progu ani braku alokacji. Type erasure daje runtime polymorphism bez wymagania wspólnej klasy bazowej.

Alternatywy mają inne koszty. Template parametr zachowuje typ statyczny i pozwala inline, ale rozprzestrzenia implementację do nagłówków. Wirtualna hierarchia współdzieli kontrakt przez dziedziczenie. `variant` ma zamknięty zbiór typów i wyczerpujący visitor. Ręczny erasure może obsługiwać move-only wartości, niestandardową alokację i konkretny ABI, lecz łatwo popełnić błąd lifetime.

Typ reprezentujący pojedynczy uchwyt może celowo być move-only i mieć jasną semantykę własności, choć nie oferuje pełnej semantyki regularnej wartości obejmującej kopiowanie. Ważne, by operacje odpowiadały znaczeniu domenowemu i nie ujawniały przypadkowego współdzielenia.

## Jak to działa krok po kroku

Przy type erasure konkretny obiekt trafia do wrappera, który zachowuje sposób wykonania ustalonego zestawu operacji. Klient widzi sygnaturę, na przykład `string(int)`, a ukryta implementacja wie, jak wywołać dany typ lambdy, przenieść go, skopiować i zniszczyć. Nie trzeba modyfikować klasy lambdy ani dodawać jej wspólnej bazy.

Gdy kopiujesz `std::function`, kopiowany jest przechowywany cel zgodnie z jego konstruktorem kopiującym. Jeśli cel zawiera `int`, dostajesz kopię liczby. Jeśli zawiera `shared_ptr`, kopiujesz współwłasność tego samego obiektu. Sam fakt, że wrapper jest kopiowalny, nie dowodzi niezależności wszystkich danych osiągalnych przez kopię.

## Pogłębienie mechanizmu

Value semantics opisuje zachowanie logiczne, a nie konkretny layout. Dwie wartości mogą współdzielić niemodyfikowalne dane implementacji i nadal zachowywać się niezależnie z perspektywy klienta. Odwrotnie, dwa różne obiekty posiadające wskaźniki do jednego modyfikowalnego stanu mogą wzajemnie wpływać na swoje wyniki. W analizie kopii pytaj, co może zaobserwować użytkownik po zmianie jednej wartości.

Type erasure może być realizowane za pomocą wskaźników do funkcji, wirtualnej hierarchii pomocniczej albo innego mechanizmu. Standard określa kontrakt `std::function`, a nie jeden obowiązkowy układ tablicy operacji. Small-buffer optimization ogranicza część alokacji, lecz jej próg i warunki są zależne od implementacji. Utrzymywanie stabilnego ABI ręcznego wrappera wymaga kontroli nad znacznie większą liczbą szczegółów niż tylko rozmiar bufora.

Pusty `std::function` jest legalnym stanem, ale jego wywołanie zgłasza `bad_function_call`. `std::move_only_function` z C++23 obsługuje niekopiowalne cele i bogatsze kwalifikacje sygnatury; ma też własny kontrakt wywołania pustego stanu, którego nie należy utożsamiać z `std::function`. Wrapper powinien precyzyjnie określać, czy pustość jest dozwolona i jak klient ma ją sprawdzać.

## Drugi przykład

~~~cpp
#include <cassert>
#include <functional>
#include <memory>

int main() {
    std::function<int()> shared = [state = std::make_shared<int>(0)] {
        return ++*state;
    };
    auto shared_copy = shared;
    const int first = shared();
    const int second = shared_copy();
    assert(first == 1 && second == 2);

    std::function<int()> independent = [state = 0]() mutable {
        return ++state;
    };
    auto independent_copy = independent;
    const int left = independent();
    const int right = independent_copy();
    assert(left == 1 && right == 1);
}
~~~

W obu przypadkach wrapper i lambda zostały skopiowane. Różnica wynika z pola zamknięcia: współdzielony wskaźnik wskazuje ten sam licznik, a zwykły `int` przechowuje osobną wartość. Współdzielenie wpływa także na wymagania synchronizacji, gdy kopie są używane w różnych wątkach. Licznik referencji `shared_ptr` nie zabezpiecza inkrementacji samego `int`.

## Porównanie i decyzje

| Mechanizm | Kiedy pasuje | Najważniejsza konsekwencja |
|---|---|---|
| Parametr szablonu | Konkretny typ znany w kompilacji | Dobre możliwości inline, większy zasięg implementacji w nagłówkach. |
| Funkcja wirtualna | Otwarta hierarchia ze wspólnym interfejsem | Jawna tożsamość obiektów i kontrakt dziedziczenia. |
| `variant` | Znany, zamknięty zbiór alternatyw | Dodanie typu zmienia zbiór obsługiwanych przypadków. |
| Type erasure | Jednolity interfejs dla niezależnych typów | Koszt pośrednictwa i własna polityka przechowywania. |

Przy pojedynczym wywołaniu nie zawsze trzeba przechowywać callback w `std::function`. Szablon przyjmujący callable może uniknąć konwersji i zachować jego typ. Erasure jest przydatne, gdy callback musi przejść przez stabilną granicę albo różne typy operacji mają być przechowywane w jednym kontenerze.

## Ćwiczenie z odpowiedzią

Czy `const std::function<int()>` gwarantuje niezmienność ukrytego stanu? Nie: kwalifikacja wrappera nie jest obietnicą czystości celu; przechowywana operacja może modyfikować własny lub współdzielony stan. Jeśli API wymaga braku skutków ubocznych, potrzebuje kontraktu semantycznego, którego sama nazwa typu nie zapewnia.

Źródło kontraktów wrapperów: [C++23, polymorphic function wrappers](https://timsong-cpp.github.io/cppwp/n4950/func.wrap).

## Powiązane tematy

- [Smart pointery](../03_pamiec_i_czas_zycia/05_smart_pointery.md)
- [Dziedziczenie i polimorfizm](../04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)
- [Type erasure, vtables i ABI](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)
