[← Spis treści](../README.md)

# Testy jednostkowe i integracyjne

Standard C++ nie dostarcza frameworka testowego. Najprostszy test może być programem zwracającym niezerowy kod przy porażce. W praktyce Catch2, GoogleTest, doctest i Boost.Test oferują rejestrację przypadków, czytelne asercje, fixtures i integrację z runnerem. Są to biblioteki zewnętrzne.

~~~cpp
#include <cassert>
#include <limits>
#include <stdexcept>

int divide(int numerator, int denominator) {
    if (denominator == 0) {
        throw std::invalid_argument{"zero denominator"};
    }
    if (numerator == std::numeric_limits<int>::min() && denominator == -1) {
        throw std::overflow_error{"division overflow"};
    }
    return numerator / denominator;
}

void test_division() {
    assert(divide(8, 2) == 4);
    try {
        (void)divide(1, 0);
        assert(false && "expected exception");
    } catch (const std::invalid_argument&) {
    }
}

int main() {
    test_division();
}
~~~

`assert` wystarcza do demonstracji, ale znika po zdefiniowaniu `NDEBUG`; produkcyjny framework ma własne makra i raportowanie. Test powinien obejmować zachowanie obserwowalne przez publiczny interfejs, nie prywatną strukturę implementacji. Nazwa przypadku opisuje scenariusz i oczekiwany wynik.

Test jednostkowy izoluje małą odpowiedzialność. Test integracyjny sprawdza współpracę modułów, plików, sieci lub procesu. End-to-end obejmuje cały przepływ. Granice nie są absolutne; ważniejsze są koszt, niezawodność i informacja diagnostyczna.

Unikaj zależności od kolejności testów, globalnego stanu i czasu ściennego. Wstrzykuj zegar, generator losowy i porty systemowe przez interfejs. Każdy wykryty błąd powinien otrzymać minimalny test regresyjny, który najpierw odtwarza porażkę.

## Jak to działa krok po kroku

Test składa się z przygotowania stanu, wykonania jednej obserwowanej operacji i sprawdzenia wyniku. Dla dzielenia przygotowaniem są argumenty, działaniem jest wywołanie funkcji, a obserwacją wynik lub typ zgłoszonego błędu. Test porażki musi zawieść również wtedy, gdy wyjątek nie zostanie zgłoszony. Sam pusty `catch` bez sprawdzenia braku wyjątku nie potwierdza oczekiwanego zachowania.

Z dziedziny wejścia wyodrębnij klasy zachowania: dodatnie i ujemne operandy, zero jako licznik, zero jako mianownik oraz granice reprezentacji. Dla signed division istnieje jeszcze przypadek minimalnej wartości podzielonej przez minus jeden, gdy wynik nie mieści się w typie. Poprawne testowanie wymaga znajomości takiej reguły języka; wielka liczba losowych zwykłych liczb może nigdy nie trafić na tę granicę.

Następnie przemyśl informację diagnostyczną. Jedna ogromna funkcja testująca wszystko może zakończyć się na pierwszym błędzie i zasłonić pozostałe zachowania. Osobne przypadki nazywające warunek i oczekiwanie pomagają rozróżnić awarię walidacji od awarii obliczenia. Framework zapewnia raport, lecz jakość scenariuszy nadal zależy od autora.

## Pogłębienie mechanizmu

Izolacja nie oznacza obowiązkowego mockowania każdej klasy. Zwykłe obiekty wartościowe i szybkie biblioteki wewnętrzne często warto testować razem. Mock sprawdzający dokładną kolejność prywatnych wywołań wiąże test z implementacją i może utrudniać bezpieczną refaktoryzację. Używaj go, gdy interakcja jest częścią kontraktu, np. wymagane jest dokładnie jedno zatwierdzenie transakcji po skutecznym zapisie.

Fake to uproszczona działająca implementacja, np. repozytorium w pamięci. Stub zwraca przygotowane odpowiedzi. Mock dodatkowo weryfikuje oczekiwania interakcji. Niezależnie od nazwy, test z zastępczą bazą nie dowodzi, że rzeczywiste SQL, izolacja transakcji i migracje działają. Do tego służy test integracyjny z rzeczywistym komponentem i kontrolowanym środowiskiem.

Testy systemowe powinny tworzyć własne zasoby: katalog tymczasowy, izolowaną bazę i port przydzielony bez kolizji. Po awarii sprzątanie powinno być odporne, a artefakty diagnostyczne wystarczające do odtworzenia problemu. Stały plik `/tmp/test.db` i wspólna globalna konfiguracja są częstą przyczyną konfliktów podczas równoległego uruchamiania testów.

Pokrycie linii pokazuje, co wykonano, nie co poprawnie sprawdzono. Test może przejść przez całą funkcję bez zauważenia błędnego wyniku. Pokrycie gałęzi i testy mutacyjne dostarczają dodatkowej informacji, lecz także nie są dowodem kompletności. Przy regresji dodaj przypadek reprodukujący konkretną porażkę i sprawdź, że nie odrzuca poprawnych zachowań w sąsiedniej części dziedziny.

Dla wyników zmiennoprzecinkowych nie dobieraj jednej przypadkowej tolerancji do każdego testu. Błąd bezwzględny pomaga blisko zera, a względny skaluje się z wielkością wyniku. Jawnie rozważ NaN, nieskończoności i podpisane zero, jeżeli należą do dziedziny. Zbyt luźna tolerancja ukrywa regresję, a zbyt ścisła odrzuca poprawne różnice zaokrągleń. Oczekiwana dokładność powinna wynikać z kontraktu obliczenia i jakości zastosowanego algorytmu numerycznego.

## Drugi przykład

Prosty program testowy może raportować błędy niezależnie od `NDEBUG`. Ten przypadek sprawdza stan kolekcji oraz zwracany wynik po udanej i nieudanej operacji.

~~~cpp
#include <algorithm>
#include <iostream>
#include <string_view>
#include <vector>

bool remove_first(std::vector<int>& values, int target) {
    const auto found = std::find(values.begin(), values.end(), target);
    if (found == values.end()) return false;
    values.erase(found);
    return true;
}

int main() {
    int failures = 0;
    const auto check = [&](bool result, std::string_view name) {
        if (!result) {
            std::cerr << "FAIL: " << name << '\n';
            ++failures;
        }
    };
    std::vector<int> values{1, 2, 2, 3};
    check(remove_first(values, 2), "existing element reported");
    check(values == std::vector<int>{1, 2, 3}, "only first match removed");
    const auto before = values;
    check(!remove_first(values, 9), "missing element reported");
    check(values == before, "missing element preserves state");
    std::vector<int> empty;
    check(!remove_first(empty, 1), "empty input accepted");
    return failures == 0 ? 0 : 1;
}
~~~

Dwa sprawdzenia po usunięciu nie są zbędne: funkcja mogłaby zwrócić właściwe bool, ale usunąć wszystkie duplikaty. Po nieudanym usunięciu test potwierdza brak zmiany danych, a nie tylko sygnał porażki. Test nie wymaga konkretnego algorytmu wyszukiwania, więc pozostanie wartościowy po zmianie implementacji zachowującej interfejs.

## Porównanie i decyzje

Utrzymuj szybki zestaw testów lokalnych i osobny zestaw sprawdzający rzeczywiste granice systemu. Długi test end-to-end ma szeroki zasięg, ale słabszą lokalizację błędu. Nie zastępuje wszystkich małych testów, podobnie jak tysiące mocków nie zastąpią choć jednego rzeczywistego połączenia komponentów. O kolejności wykonywania decyduj na podstawie kosztu i wartości wykrywania regresji.

**Ćwiczenie.** Test sortowania sprawdza tylko, że wynik jest uporządkowany. Jakiego błędu nie wykryje? **Odpowiedź:** funkcja mogłaby zwrócić pusty zakres albo zgubić duplikaty. Potrzebne jest również zachowanie liczby i multizbioru elementów. Warto sprawdzić własność permutacji wejścia i wyjścia, a przy sortowaniu stabilnym także kolejność elementów równoważnych.

Źródła: [GoogleTest: podstawy i asercje](https://google.github.io/googletest/primer.html), [CTest](https://cmake.org/cmake/help/latest/manual/ctest.1.html), [C++23: dzielenie](https://timsong-cpp.github.io/cppwp/n4950/expr.mul).

## Powiązane tematy

- [CMake](../08_budowanie_i_organizacja/05_cmake.md)
- [Fuzzing](05_fuzzing_i_property_based_testing.md)
- [Assertions i kontrakty](../07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)
