[← Spis treści](../README.md)

# Arytmetyka, przepełnienia i float

## Wymagania wstępne

Zakładamy znajomość typów całkowitych, konwersji, porównań i `std::optional`. Punktem odniesienia jest C++23. Rozdział rozdziela trzy pytania: jaki typ otrzymuje działanie, czy wynik mieści się w tym typie i czy reprezentacja wystarcza dla wymaganej dokładności. Poprawny wybór typu zmiennej docelowej nie rozwiązuje automatycznie pozostałych problemów.

Typ jest częścią algorytmu. Licznik elementów, saldo i próbka pomiarowa mają różne wymagania, chociaż wszystkie mogą wyglądać jak liczby. Dla rozmiaru bufora błędne zawinięcie prowadzi do zbyt małej alokacji, a dla pomiaru zbyt ostra tolerancja odrzuca prawidłowy wynik. Najpierw określ zakres danych i politykę błędu; dopiero potem wybierz działania i reprezentację.

## Jak to działa krok po kroku

Przy dodawaniu i mnożeniu liczb całkowitych najpierw następują promocje, a następnie zwykłe konwersje arytmetyczne. Typ zmiennej po lewej stronie przypisania nie bierze udziału w wyborze typu wcześniejszego mnożenia. W `long long result = a * b;`, gdy oba argumenty mają typ `int`, mnożenie zachodzi w `int`. Aby wykonać je w szerszym typie, zmień operand przed działaniem, na przykład `1LL * a * b`. Nadal trzeba upewnić się, że również szerszy typ wystarcza. Zasady podają [N4950, expr.arith.conv](https://timsong-cpp.github.io/cppwp/n4950/expr.arith.conv) i [expr.mul](https://timsong-cpp.github.io/cppwp/n4950/expr.mul).

Wynik niemieszczący się w typie całkowitym ze znakiem powoduje UB. Nie jest przenośnym sposobem otrzymywania ujemnych liczb ani sprawdzania przepełnienia po fakcie. Dla typu bez znaku arytmetyka zachodzi modulo dwa do potęgi liczby bitów wartości. Ten mechanizm jest zdefiniowany, lecz nadal może naruszać wymagania programu. Nowoczesna reprezentacja liczb signed w kodzie uzupełnień do dwóch nie zmienia reguły przepełnienia. Zobacz [N4950, basic.fundamental](https://timsong-cpp.github.io/cppwp/n4950/basic.fundamental) i [expr.pre](https://timsong-cpp.github.io/cppwp/n4950/expr.pre).

~~~cpp
#include <cassert>
#include <cstddef>
#include <limits>
#include <optional>
#include <utility>

std::optional<int> checked_add(int a, int b) {
    const int low = std::numeric_limits<int>::lowest();
    const int high = std::numeric_limits<int>::max();
    if ((b > 0 && a > high - b) ||
        (b < 0 && a < low - b)) {
        return std::nullopt;
    }
    return a + b;
}

std::optional<std::size_t> buffer_size(std::size_t count,
                                       std::size_t element_size) {
    const auto high = std::numeric_limits<std::size_t>::max();
    if (element_size != 0 && count > high / element_size) {
        return std::nullopt;
    }
    return count * element_size;
}

int main() {
    assert(checked_add(20, 22) == 42);
    assert(!checked_add(std::numeric_limits<int>::max(), 1));
    assert(!checked_add(std::numeric_limits<int>::lowest(), -1));
    assert(buffer_size(12, 4) == 48);
    assert(!buffer_size(std::numeric_limits<std::size_t>::max(), 2));

    unsigned wrapped = std::numeric_limits<unsigned>::max();
    ++wrapped;
    assert(wrapped == 0);
    const int side = 30'000;
    assert(1LL * side * side == 900'000'000LL);
    assert(std::cmp_less(-1, 1u));
}
~~~

Kontrola dodawania sama nie przepełnia typu: dla dodatniego `b` odejmuje go od maksimum, a dla ujemnego od minimum. Dopiero sprawdzenie pozwala wykonać sumę. Kontrola mnożenia unsigned korzysta z dzielenia przed mnożeniem, osobno obsługując zerowy rozmiar elementu. Samo `count * element_size < count` nie jest ogólnym testem przepełnienia. Niektóre zawinięte wyniki nadal będą większe od pierwszego argumentu.

Mieszanie znaków wymaga dodatkowego namysłu. Dla `int` i `unsigned int` wspólnym typem jest `unsigned int`; dlatego porównanie `-1 < 1u` daje fałsz. Przy różnych rangach signed może pozostać typem wspólnym, jeśli mieści wszystkie wartości odpowiedniego unsigned. Reguła „unsigned zawsze wygrywa” jest zbyt prosta. Do porównywania wartości całkowitych o różnych znakach używaj odpowiednio `std::cmp_less`, a do sprawdzania konwersji `std::in_range`, opisanych w [N4950, utility.intcmp](https://timsong-cpp.github.io/cppwp/n4950/utility.intcmp).

## Pogłębienie mechanizmu

UB arytmetyczne obejmuje także przypadki mniej oczywiste niż dodawanie. Dzielenie całkowite przez zero jest błędne. Dzielenie minimum typu signed przez minus jeden również ma UB, ponieważ dodatni wynik nie mieści się w typie. Tego samego problemu nie omija operator reszty `%`. Zaprzeczenie minimum przez jednoargumentowy minus też nie daje reprezentowalnej wartości. Walidator liczb powinien obejmować każdą używaną operację, a nie tylko najbardziej widoczną sumę.

Poniższy blok celowo powoduje UB, więc nie jest wykonywany. Próba rozpoznania przepełnienia po obliczeniu sumy jest spóźniona; kompilator może optymalizować przy założeniu, że poprawny program nie przepełnia `int`.

~~~cpp,notest
#include <limits>

int main() {
    int value = std::numeric_limits<int>::max();
    int next = value + 1; // UB następuje tutaj.
    return next < value;
}
~~~

Liczba zmiennoprzecinkowa przechowuje ograniczoną precyzję, a nie dowolną liczbę rzeczywistą. W popularnym formacie binarnym wiele ułamków dziesiętnych, takich jak jedna dziesiąta, nie ma skończonej reprezentacji. Każde kolejne działanie może wprowadzać zaokrąglenie. W efekcie matematyczna łączność dodawania nie zapewnia identycznego wyniku przestawionych sum. Przy odejmowaniu bliskich przybliżeń mała różnica może dodatkowo ujawnić wcześniej niewidoczny błąd danych.

C++ nie gwarantuje dla każdej implementacji konkretnego formatu IEEE 754 ani szerokości `double`. Właściwości sprawdzaj przez `std::numeric_limits`, w tym `digits`, `radix`, `is_iec559`, `has_infinity` i `has_quiet_NaN`. Dla typu zmiennoprzecinkowego `min()` oznacza najmniejszą dodatnią wartość znormalizowaną; najbardziej ujemną skończoną wartość daje `lowest()`. `epsilon()` opisuje odstęp w okolicy jedności, a nie uniwersalny dopuszczalny błąd obliczeń. Definicje zawiera [N4950, numeric.limits.members](https://timsong-cpp.github.io/cppwp/n4950/numeric.limits.members).

Na implementacji IEC 60559 NaN oznacza wartość niebędącą liczbą i nie jest równe nawet samemu sobie. Porównania porządkowe z NaN są fałszywe, więc sprawdzenie `!(x < 0)` nie dowodzi, że `x` jest nieujemną zwykłą liczbą. Używaj `std::isnan` i `std::isfinite` zgodnie z kontraktem wejścia. Nieskończoność także wymaga świadomej polityki; nie traktuj jej jako dużego skończonego pomiaru. Funkcje klasyfikujące opisuje [N4950, c.math.fpclass](https://timsong-cpp.github.io/cppwp/n4950/c.math.fpclass).

## Drugi przykład

Poniższy predykat realizuje konkretną politykę: NaN odrzuca, jednakowe wartości akceptuje, różne nieskończoności odrzuca. Dla liczb skończonych łączy tolerancję bezwzględną blisko zera z względną przy większej skali. Normalizacja przed odejmowaniem ogranicza ryzyko przepełnienia różnicy dwóch bardzo dużych liczb o przeciwnych znakach. Stałe tolerancji są decyzją przykładu, a nie zaleceniem dla każdej dziedziny.

~~~cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <limits>

bool close(double a, double b) {
    constexpr double absolute_tolerance = 1e-12;
    constexpr double relative_tolerance = 1e-9;
    if (std::isnan(a) || std::isnan(b)) {
        return false;
    }
    if (a == b) {
        return true;
    }
    if (!std::isfinite(a) || !std::isfinite(b)) {
        return false;
    }
    const double scale = std::max(std::abs(a), std::abs(b));
    if (scale <= absolute_tolerance / 2) {
        return true;
    }
    const double normalized_difference = std::abs(a / scale - b / scale);
    return normalized_difference <=
        std::max(absolute_tolerance / scale, relative_tolerance);
}

int main() {
    assert(close(0.0, 5e-13));
    assert(!close(0.0, 1e-6));
    assert(close(1e9, 1e9 + 0.5));
    assert(!close(1e9, 1e9 + 2.0));
    assert(close(0.1 + 0.2, 0.3));

    if constexpr (std::numeric_limits<double>::is_iec559) {
        const double nan = std::numeric_limits<double>::quiet_NaN();
        const double inf = std::numeric_limits<double>::infinity();
        assert(!close(nan, nan));
        assert(close(inf, inf));
        assert(!close(inf, -inf));
        assert(!close(std::numeric_limits<double>::max(),
                      -std::numeric_limits<double>::max()));
    }
}
~~~

Gdy skala nie przekracza połowy tolerancji bezwzględnej, największa możliwa różnica mieści się w całej tolerancji. W pozostałej gałęzi skala jest dodatnia, a wartości po podzieleniu mają moduł nie większy niż jeden. To uzasadnia kolejność sprawdzeń i pozwala unikać niepotrzebnego tworzenia nieskończonej różnicy. Na granicy tolerancji nadal występują zwykłe błędy zaokrągleń; predykat nie jest dowodem równości liczb rzeczywistych.

## Porównanie i decyzje

Porównanie przybliżone nie musi być przechodnie: A może być bliskie B, B bliskie C, a A już nie C. Nie używaj takiej relacji jako dowolnego zamiennika równoważności kluczy ani nie buduj przez nią automatycznie komparatora sortowania. Dla danych pomiarowych tolerancja powinna wynikać z jednostki, skali i błędu modelu. Dla dokładnych wielkości dziesiętnych rozważ reprezentację całkowitą ze świadomie ustaloną jednostką i kontrolą zakresu.

Przetestuj również wartości graniczne: minimum, maksimum, zero, zmianę znaku, rozmiar tuż poniżej limitu oraz pierwszą wartość niedozwoloną. Dla obliczeń przybliżonych dodaj liczby bliskie zeru i reprezentatywne dla największej oczekiwanej skali. Jeśli włączasz opcje kompilatora dopuszczające agresywne przekształcenia arytmetyki zmiennoprzecinkowej, osobno sprawdź ich kontrakt wobec NaN, nieskończoności i kolejności działań. Test wykonany z innymi opcjami nie potwierdza automatycznie zachowania konfiguracji produkcyjnej.

**Ćwiczenie 1.** Czy `static_cast<long long>(a * b)` chroni przed przepełnieniem mnożenia dwóch `int`?

<details>
<summary>Rozwiązanie</summary>

Nie. Konwersja następuje po mnożeniu. Zmień typ przynajmniej jednego argumentu przed działaniem i sprawdź, czy szerszy typ mieści oczekiwany iloczyn.

</details>

**Ćwiczenie 2.** Dlaczego sama tolerancja względna jest niewygodna przy porównywaniu wyniku z zerem?

<details>
<summary>Rozwiązanie</summary>

Skala odniesienia staje się bardzo mała. Dla zera i niewielkiego niezerowego wyniku względna różnica może wynosić jeden, mimo akceptowalnego błędu w jednostkach pomiaru. Składnik bezwzględny opisuje dopuszczalny błąd w tej okolicy.

</details>

## Powiązane tematy

- [Typy podstawowe i literały](02_typy_podstawowe_i_literaly.md)
- [Operatory i konwersje](04_operatory_i_konwersje.md)
- [Inicjalizacja i initializer_list](08_inicjalizacja_i_initializer_list.md)
- [Kolejność ewaluacji i sequencing](09_kolejnosc_ewaluacji_i_sequencing.md)
