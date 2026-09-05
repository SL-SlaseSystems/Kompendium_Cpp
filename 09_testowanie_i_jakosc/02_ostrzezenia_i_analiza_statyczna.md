[← Spis treści](../README.md)

# Ostrzeżenia i analiza statyczna

Ostrzeżenia kompilatora wykrywają podejrzane, choć formalnie dopuszczalne konstrukcje. Dla Clang i GCC rozsądnym początkiem jest `-Wall -Wextra -Wpedantic`; projekt może dodać m.in. konwersje i shadowing po ocenie szumu. MSVC oferuje `/W4` i `/permissive-`. Zestawy nie są równoważne między kompilatorami.

~~~cpp
#include <cassert>
#include <cstddef>
#include <span>

std::size_t count_positive(std::span<const int> values) {
    std::size_t count = 0;
    for (int value : values) {
        if (value > 0) {
            ++count;
        }
    }
    return count;
}

int main() {
    const int values[]{-1, 2, 3};
    assert(count_positive(values) == 2);
}
~~~

Jawne typy w przykładzie ograniczają niepotrzebne porównania signed/unsigned. Nie wyciszaj ostrzeżenia rzutowaniem bez sprawdzenia, czy konwersja mieści się w zakresie. Warning-as-error pomaga utrzymać czystość własnego kodu, ale zewnętrzne nagłówki warto oznaczyć jako systemowe lub analizować osobnym profilem.

Clang-Tidy, PVS-Studio, Coverity i inne analizatory modelują przepływ danych, lifetime, concurrency oraz reguły stylu. `clang-tidy` ma zestawy checks i mechanizm automatycznych poprawek, ale wynik nadal wymaga przeglądu. Clang Static Analyzer i narzędzia komercyjne mogą wykonywać analizę ścieżek międzyproceduralnych.

Analiza statyczna nie widzi wszystkich danych runtime i może zgłaszać false positives. Wyciszenie powinno być lokalne, udokumentowane i powiązane z konkretnym checkiem. Najlepsza polityka to mały, stabilny baseline, stopniowe włączanie kolejnych reguł i blokowanie nowych naruszeń.

## Jak to działa krok po kroku

Kompilator najpierw analizuje program w konkretnej konfiguracji: z określonym standardem, makrami i ścieżkami nagłówków. Ostrzeżenie dotyczy tej wersji jednostki translacji. Jeżeli projekt kompiluje osobne ścieżki przez `#ifdef`, pojedynczy build nie obejmuje wszystkich wariantów. `-Wall` jest nazwą zestawu wybranego przez autorów kompilatora, a nie obietnicą włączenia dosłownie wszystkich możliwych ostrzeżeń.

Czytając ostrzeżenie o konwersji, ustal dziedzinę źródła i celu. Zmiana `int` na `size_t` nie naprawia automatycznie sytuacji, gdy ujemna liczba oznacza błąd. Najpierw trzeba sprawdzić znak lub użyć typu wynikowego. Dopiero potem konwersja może być uzasadniona. Rzutowanie wyciszające komunikat bez zmiany kontraktu często tylko ukrywa problem przed kolejną osobą.

Dla clang-tidy dostarcz rzeczywistą bazę komend kompilacji. Plik `compile_commands.json` opisuje parametry potrzebne do poprawnego parsowania każdej jednostki. Bez niego analizator może widzieć inne makra, brakujące nagłówki albo inny standard niż build produkcyjny. W CMake bazę można generować przez `CMAKE_EXPORT_COMPILE_COMMANDS`, z uwzględnieniem wsparcia konkretnego generatora.

## Pogłębienie mechanizmu

Diagnostyka kompilatora obejmuje błędy wymagające odrzucenia programu oraz opcjonalne ostrzeżenia o konstrukcjach ryzykownych lub nieprzenośnych. Brak ostrzeżeń nie oznacza braku UB: wiele naruszeń wymaga danych runtime albo analizy całego systemu. Z kolei ostrzeżenie nie zawsze oznacza błąd standardu. Trzeba rozróżniać regułę języka, heurystykę narzędzia i konwencję projektu.

Analiza ścieżek śledzi możliwe stany, np. czy wskaźnik może być null po serii warunków. Gdy brakuje modeli zewnętrznych funkcji, wynik może być zbyt ostrożny albo przeoczyć rzeczywistą zależność. Analizator operujący na jednej jednostce ma inne możliwości niż narzędzie międzyproceduralne korzystające z całego projektu. Zestaw checks dotyczących stylu nie zastępuje analizy przepływu zasobów.

Włączanie `-Werror` w kontrolowanym CI zapobiega narastaniu ostrzeżeń, ale nowa wersja kompilatora może rozszerzyć diagnostykę. Aktualizację toolchainu traktuj jako zmianę wymagającą przeglądu. Publiczna biblioteka nie powinna narzucać klientowi wszystkich prywatnych ostrzeżeń jako wymagań interfejsu. Zewnętrzny kod można analizować oddzielnie, zachowując własne rygorystyczne ustawienia bez masowego wyciszania całego programu.

Automatyczna poprawka clang-tidy jest propozycją zmiany kodu. Może naruszyć intencję, szczególnie gdy przekształca własność, konstrukcję obiektu lub granicę API. Przejrzyj diff i uruchom właściwe testy. Jeśli ostrzeżenie jest uzasadnionym wyjątkiem, stosuj lokalne wyciszenie konkretnego checka z wyjaśnieniem. Ogólne „ignore all” usuwa również ochronę przed przyszłymi błędami tego miejsca.

## Drugi przykład

Sprawdzana konwersja jest lepszą odpowiedzią na ostrzeżenie niż samo dodanie castu. C++20 `std::in_range` porównuje reprezentowalne zakresy obsługiwanych typów całkowitych bez kłopotliwego ręcznego mieszania znaków.

~~~cpp
#include <cassert>
#include <cstddef>
#include <limits>
#include <optional>
#include <utility>

std::optional<int> count_as_int(std::size_t count) {
    if (!std::in_range<int>(count)) return std::nullopt;
    return static_cast<int>(count);
}

int main() {
    assert(count_as_int(42) == 42);
    const auto huge = std::numeric_limits<std::size_t>::max();
    if (!std::in_range<int>(huge)) {
        assert(!count_as_int(huge));
    }
}
~~~

Konwersja jest wykonywana dopiero po sprawdzeniu. Test skrajnej wartości pozostaje warunkowy, ponieważ relacje szerokości typów należą do implementacji; nie zakładamy mechanicznie, że `size_t` ma zawsze 64 bity. W realnym API warto też zapytać, dlaczego odbiorca żąda `int` i czy nie lepiej zachować naturalny typ liczności przez cały przepływ.

~~~text
# Przykład dla CMake z generatorem Ninja i zainstalowanym clang-tidy:
cmake -S . -B build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
clang-tidy src/parser.cpp -p build \
  -checks='-*,clang-analyzer-*,bugprone-*'
~~~

Lista checków jest punktem startowym do przeglądu, nie uniwersalnym standardem jakości. Nazwy i dostępność konkretnych reguł zależą od wersji narzędzia. W repozytorium utrwal przemyślaną konfigurację `.clang-tidy`, aby lokalna analiza i CI odpowiadały sobie.

## Porównanie i decyzje

Ostrzeżenia działają szybko i warto wykonywać je przy każdym buildzie. Analiza statyczna może kosztować więcej, ale bada również ścieżki niewykonane w testach. Sanitizery obserwują realne wykonanie i uzupełniają tę perspektywę. Najbardziej użyteczna konfiguracja daje komunikaty, które zespół naprawdę przegląda, zamiast tysięcy permanentnie ignorowanych zgłoszeń.

**Ćwiczenie.** Czy `static_cast<unsigned>(negative)` eliminuje problem ujemnego wejścia? **Odpowiedź:** nie, wynik konwersji jest określony regułami typu bez znaku, ale może nie mieć oczekiwanego znaczenia domenowego. Najpierw trzeba zdecydować, czy ujemna wartość jest błędem, znacznikiem czy legalną liczbą. Poprawność języka i poprawność zadania to osobne kwestie.

Źródła: [Clang: opcje diagnostyczne](https://clang.llvm.org/docs/UsersManual.html), [clang-tidy](https://clang.llvm.org/extra/clang-tidy/), [baza komend kompilacji](https://clang.llvm.org/docs/JSONCompilationDatabase.html).

## Powiązane tematy

- [Kompilatory i toolchain](../01_wprowadzenie/03_kompilatory_i_toolchain.md)
- [Sanitizery i debugowanie](03_sanitizery_i_debuggery.md)
- [C++ Core Guidelines](../zrodla.md)
