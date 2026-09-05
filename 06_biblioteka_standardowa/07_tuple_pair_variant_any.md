[← Spis treści](../README.md)

# tuple, pair, variant i any

`std::pair<T, U>` i `std::tuple<Ts...>` są typami produktowymi: przechowują wszystkie składowe naraz. `std::variant<Ts...>` jest typem sumy: przechowuje dokładnie jedną alternatywę. `std::any` przechowuje jedną wartość dowolnego kopiowalnego typu i odzyskuje ją przez kontrolowany rzut runtime.

~~~cpp
#include <any>
#include <cassert>
#include <string>
#include <tuple>
#include <variant>

int main() {
    const auto record = std::tuple{7, std::string{"Ada"}, true};
    const auto& [id, name, active] = record;

    std::variant<int, std::string> answer = std::string{"ok"};
    std::any payload = 42;

    assert(id == 7 && name == "Ada" && active);
    assert(std::get<std::string>(answer) == "ok");
    assert(std::any_cast<int>(payload) == 42);
}
~~~

Structured bindings mogą rozpakować pair, tuple, tablicę i typy o odpowiednim protokole. Użycie `auto` kopiuje składowe, a `auto&` lub `const auto&` wiąże referencje. Typy referencji ukryte pod structured binding mają szczegółowe reguły; przy lifetime-sensitive kodzie sprawdzaj rzeczywisty typ inicjalizatora.

Tuple jest dobry dla lokalnego, oczywistego zestawu danych lub generycznej infrastruktury. Gdy pola mają trwałe znaczenie domenowe, nazwana struktura daje lepszy kontrakt. Variant najlepiej reprezentuje zamknięty zbiór przypadków; visitor powinien być wyczerpujący. Any jest bardziej dynamiczny, ale traci compile-time exhaustiveness i wymaga znajomości dokładnego typu przy `any_cast`.

`std::optional<T>` opisuje obecność lub brak jednego `T`, więc jest prostszy niż `variant<monostate, T>`. `expected<T, E>` opisuje sukces albo błąd i również powinien być preferowany nad anonimową tuple flagi z wartością.

## Jak to działa krok po kroku

Pierwszy przykład tworzy tuple zawierającą trzy różne pola. Deklaracja `const auto& [id, name, active]` wiąże ukryty obiekt referencyjny z istniejącą tuple, a nazwy odnoszą się do jej składowych. Zapis `auto [id, name, active] = record` najpierw utworzyłby ukrytą kopię tuple. To ma znaczenie dla kosztu napisu i dla tego, czy późniejsze modyfikacje dotyczą oryginału. Tuple referencji wymaga dodatkowej uwagi: skopiowanie tuple nie musi kopiować wskazywanych obiektów.

Variant konstruuje aktualnie wybraną alternatywę we własnej pamięci. Przypisanie napisu do wariantu, który przechowywał liczbę, kończy życie jednej alternatywy i rozpoczyna życie drugiej. `index()` identyfikuje alternatywę, `holds_alternative<T>` sprawdza typ, a `get<T>` rzuca `bad_variant_access`, gdy wybrano inny typ. `get_if<T>` zwraca wskaźnik lub null, co pasuje do opcjonalnego sprawdzenia bez wyjątku.

`any_cast<int>(payload)` wymaga dokładnie odpowiedniego przechowywanego typu; nie wykonuje ogólnej konwersji liczbowej. Jeśli w `any` zapisano `long`, próba odczytu jako `int` nie skorzysta z konwersji long-to-int. Wariant wskaźnikowy `any_cast<int>(&payload)` daje null zamiast rzucać. Referencyjny cast pozwala uniknąć kopiowania zawartości, ale po zniszczeniu albo zmianie `any` uzyskana referencja może przestać być ważna.

## Pogłębienie mechanizmu

`std::visit` wybiera funkcję zgodnie z aktywną alternatywą. Visitor musi obsługiwać wszystkie kombinacje alternatyw podanych wariantów, nawet jeśli w aktualnym teście występuje tylko jedna z nich. Odmiana bez jawnego typu wyniku wymaga zgodności typów i kategorii wyników wszystkich wywołań. Można użyć zestawu przeciążonych lambd albo jednej lambdy generycznej z `if constexpr`; warto dążyć do błędu kompilacji po dodaniu nowego przypadku bez jego obsługi.

Variant może wyjątkowo wejść w stan `valueless_by_exception`, gdy wymiana alternatywy nie powiedzie się i nie da się zachować starej wartości. Nie jest to zwykła alternatywa „brak”. `monostate` świadomie modeluje taki przypadek domenowy, a `valueless_by_exception` opisuje konsekwencję niepowodzenia konstrukcji. Wizytacja bez wartości rzuca. Bezpieczne operacje przenoszące alternatyw ograniczają sytuacje, w których trzeba analizować taki stan.

`any` opiera się na wymazaniu typu i przechowuje tylko typy spełniające wymaganie kopiowalności. Nie pomieści więc bezpośrednio `unique_ptr<T>`. Implementacja może używać małego bufora dla niektórych typów, ale nie zakładaj określonego progu ani braku alokacji. Variant ma zamknięty zestaw typów ustalony podczas kompilacji; any pozwala go rozszerzać bez zmiany listy alternatyw kosztem utraty statycznej kontroli przypadków.

`std::tie(a, b)` tworzy tuple referencji do istniejących zmiennych, więc przypisanie innej pary wartości zmienia te zmienne. `std::make_tuple` zwykle tworzy wartości z przekształconych argumentów, natomiast `forward_as_tuple` zachowuje referencje i kategorie argumentów. Ten ostatni jest narzędziem do natychmiastowego przekazania, nie bezpiecznym magazynem argumentów tymczasowych na później. Tuple zawierająca referencję do zniszczonego napisu nadal może wyglądać poprawnie typowo, lecz jej użycie narusza czas życia danych.

## Drugi przykład

Zamknięty zestaw poleceń lepiej opisuje variant niż para tekstowego znacznika i dowolnego payloadu. Każda alternatywa zawiera tylko własne dane.

~~~cpp
#include <cassert>
#include <string>
#include <variant>

struct Rename { std::string name; };
struct Reset { };

template<class... Fs>
struct Overload : Fs... { using Fs::operator()...; };

int main() {
    using Command = std::variant<Rename, Reset>;
    std::string current = "old";
    const auto apply = [&](const Command& command) {
        std::visit(Overload{
            [&](const Rename& rename) { current = rename.name; },
            [&](const Reset&) { current.clear(); }
        }, command);
    };
    apply(Rename{"new"});
    assert(current == "new");
    apply(Reset{});
    assert(current.empty());
}
~~~

Dopisanie `struct Save` do wariantu bez rozszerzenia visitora powoduje błąd kompilacji. Nie istnieje stan „Reset z przypadkowym napisem”, bo typ Reset nie ma pola. Warto zauważyć, że visitor przechwytuje `current` przez referencję i jest używany tylko podczas życia tej zmiennej. Zapisanie go na później wymagałoby osobnego uzasadnienia czasu życia.

## Porównanie i decyzje

Nazwana struktura daje najlepszy interfejs dla rekordu domenowego z trwałymi nazwami pól. Pair pasuje do par narzuconych protokołem biblioteki, np. iteratora i flagi wstawienia. Tuple jest użyteczna w szablonach, `apply` i pakietach argumentów. Variant wyraża zamknięte alternatywy, a polimorfizm dynamiczny pasuje do hierarchii rozszerzanej poza miejscem definicji. Any wybieraj na granicach, gdzie dynamiczna zawartość jest rzeczywistym wymaganiem.

**Ćwiczenie.** Dlaczego `variant<int, int>` jest mało wygodny? **Odpowiedź:** dwie alternatywy mają ten sam typ, więc operacje identyfikujące alternatywę samym typem nie rozstrzygają wyboru. Można użyć indeksów, lecz dwa nazwane typy, np. `UserId` i `OrderId`, lepiej opisują znaczenie i zapobiegają pomyleniu wartości.

Źródła reguł: [C++23: variant](https://timsong-cpp.github.io/cppwp/n4950/variant), [any](https://timsong-cpp.github.io/cppwp/n4950/any), [structured bindings](https://timsong-cpp.github.io/cppwp/n4950/dcl.struct.bind).

## Powiązane tematy

- [enum, union i variant](../04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)
- [optional i expected](../07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)
- [Type erasure](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
