[← Spis treści](../README.md)

# Linkowanie, ODR i inline

Linkage określa, czy deklaracje w różnych zakresach i jednostkach odnoszą się do tej samej encji. Nazwa może mieć external, internal albo no linkage. Anonimowa przestrzeń nazw nadaje elementom namespace scope internal linkage i jest preferowana nad `static` dla pomocniczych nazw w pliku `.cpp`.

One Definition Rule wymaga jednej definicji odr-used funkcji lub zmiennej nieinline w całym programie. Typy, szablony, funkcje inline i inline variables mogą mieć definicje w wielu jednostkach, lecz muszą spełniać szczegółowe wymagania równoważności. Naruszenie ODR nie zawsze wymaga diagnostyki, więc program może linkować i nadal być niepoprawny.

~~~cpp
#include <cassert>

inline constexpr int protocol_version = 3;

inline int square(int value) {
    return value * value;
}

int main() {
    static_assert(protocol_version == 3);
    assert(square(5) == 25);
}
~~~

`inline` nie nakazuje kompilatorowi wstawienia ciała w miejscu wywołania. To właściwość ODR i linkage. Optymalizator podejmuje decyzję o inline niezależnie, zwłaszcza przy link-time optimization.

Błędy „undefined symbol/reference” wynikają zwykle z braku definicji, niewłaściwej biblioteki, różnicy sygnatury albo visibility. „Duplicate symbol” wskazuje wiele niedozwolonych definicji. Name mangling koduje sygnatury i zależy od ABI, dlatego C++ API nie jest bezpośrednio stabilnym C ABI.

## Jak to działa krok po kroku

Kompilator generuje symbole dla definicji i odniesienia do symboli używanych z innych jednostek. Linker zestawia te informacje, wybiera potrzebne obiekty z bibliotek i rozstrzyga odniesienia. Komunikat o brakującym symbolu oznacza, że wymaganej definicji nie dostarczono w oczekiwanej postaci. Może istnieć podobna funkcja o innej przestrzeni nazw, kwalifikatorze const lub typie parametru; dla ABI są to różne symbole.

Gdy zwykła funkcja z external linkage zostanie zdefiniowana w dwóch jednostkach, linker często zgłasza konflikt. Dla `inline` dopuszczone są odpowiadające sobie definicje w wielu jednostkach, jeśli spełniają wymagania ODR. Funkcja nadal reprezentuje jedną encję, a jej adres jest taki sam w jednostkach odnoszących się do tej encji. Lokalny obiekt statyczny w takiej funkcji także jest współdzielony, a nie osobny dla każdego klienta.

Nie myl linkage z okresem przechowywania. `static` przy funkcji na poziomie przestrzeni nazw nadaje internal linkage, a `static` przy zmiennej lokalnej daje statyczny czas przechowywania. Lokalna zmienna nie staje się przez to eksportowanym symbolem publicznego interfejsu. Z kolei namespace-scope `const` ma często internal linkage bez słowa `static`, z wyjątkami wynikającymi z pozostałych specyfikatorów i wcześniejszych deklaracji.

## Pogłębienie mechanizmu

Wielokrotne definicje dozwolone przez ODR muszą między innymi składać się z tej samej sekwencji tokenów oraz spełniać wymagania dotyczące rozwiązywania nazw. Identyczny tekst nie wystarczy, jeśli nazwa w definicji oznacza różne obiekty lub funkcje. Istnieją szczegółowe wyjątki, ale praktyczna zasada brzmi: publiczną definicję generuj z jednego nagłówka przy zgodnej konfiguracji. Makro zmieniające pola klasy w różnych jednostkach może zmienić jej układ bez obowiązkowej diagnostyki.

`inline constexpr` na zmiennej od C++17 pozwala udostępnić w nagłówku jedną encję stałej z external linkage. Zwykłe namespace-scope `constexpr` zwykle tworzy odrębną stałą z internal linkage w każdej jednostce. Różnica może być istotna, gdy przekazujesz adres albo używasz tożsamości obiektu. Funkcja `constexpr` jest niejawnie inline; nie oznacza to, że każde wywołanie wykona się podczas kompilacji.

Definicja metody wewnątrz klasy jest zwykle niejawnie inline. C++20 wprowadza istotny wyjątek dla funkcji dołączonych do nazwanego modułu, więc przy migracji nie należy stosować nagłówkowej reguły mechanicznie. Moduły dodają również module linkage. Klasyfikacja trzech tradycyjnych rodzajów linkage nie wyczerpuje więc całego C++23.

Biblioteka statyczna jest archiwum plików obiektowych; zwykle do programu trafiają tylko obiekty potrzebne do rozwiązania symboli. Kolejność bibliotek może mieć znaczenie dla konkretnego linkera. Biblioteka współdzielona pozostaje oddzielnym artefaktem ładowanym przez system. Visibility i eksport określają, które symbole udostępnia, ale nie zastępują reguł ODR. Nie zakładaj zgodności binarnej C++ między dowolnymi kompilatorami tylko dlatego, że oba obsługują C++23.

## Drugi przykład

Funkcja inline z lokalnym statycznym licznikiem demonstruje wspólną tożsamość w dwóch jednostkach. Przykład jest wieloplikowy, ponieważ kompilowanie tylko jednego pliku nie sprawdzi tej własności.

~~~text
// state.hpp
#ifndef GUIDE_STATE_HPP
#define GUIDE_STATE_HPP
inline int& shared_counter() {
    static int value = 0;
    return value;
}
void increment_from_worker();
#endif

// worker.cpp
#include "state.hpp"
void increment_from_worker() { ++shared_counter(); }

// main.cpp
#include "state.hpp"
int main() {
    increment_from_worker();
    return shared_counter() == 1 ? 0 : 1;
}

clang++ -std=c++23 worker.cpp main.cpp -o shared_state
./shared_state
~~~

Obie definicje `shared_counter` pochodzą z jednego nagłówka i są zgodne. Usunięcie `inline` tworzyłoby niedozwolone wielokrotne definicje funkcji. Zastąpienie go `static` dałoby każdej jednostce własną funkcję i własny licznik, więc program zakończyłby się wynikiem jeden. Przy wielu wątkach inicjalizacja lokalnej zmiennej statycznej ma ochronę języka, lecz późniejsze `++value` wymaga osobnej synchronizacji.

## Porównanie i decyzje

Pomocniczą funkcję używaną tylko w `.cpp` umieszczaj w anonimowej przestrzeni nazw. Publiczną nieinline funkcję definiuj w jednej jednostce. Inline stosuj dla treści, które rzeczywiście muszą być dostępne w wielu jednostkach, i oceniaj koszt kompilacji dużych nagłówków. LTO może optymalizować wywołania między jednostkami bez przenoszenia wszystkich implementacji do nagłówków.

**Ćwiczenie.** Program z różnymi definicjami klasy w dwóch jednostkach kompiluje się i linkuje. Czy to dowód legalności? **Odpowiedź:** nie. Część naruszeń ODR jest ill-formed, no diagnostic required. Linker zwykle nie porównuje pełnej semantyki typów. Potrzebne są spójne nagłówki, konfiguracja i budowanie wszystkich zależnych jednostek po zmianach interfejsu.

Źródła reguł: [C++23: ODR](https://timsong-cpp.github.io/cppwp/n4950/basic.def.odr), [inline](https://timsong-cpp.github.io/cppwp/n4950/dcl.inline), [linkage](https://timsong-cpp.github.io/cppwp/n4950/basic.link).

## Powiązane tematy

- [Translation units i nagłówki](01_translation_units_headers_i_include.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
