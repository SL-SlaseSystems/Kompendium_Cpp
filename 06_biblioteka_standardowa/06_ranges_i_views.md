[← Spis treści](../README.md)

# Ranges i views

Biblioteka ranges z C++20 opisuje zakres przez `range`, iterator i sentinel. Algorytmy `std::ranges` mają lepsze constraints, obsługują projection i mogą przyjmować cały zakres. Views są leniwymi, zwykle tanimi adaptacjami: filtrują, transformują lub ograniczają dane bez natychmiastowego tworzenia nowego kontenera.

~~~cpp
#include <cassert>
#include <ranges>
#include <vector>

int main() {
    const std::vector values{1, 2, 3, 4, 5, 6};
    auto result = values
        | std::views::filter([](int value) { return value % 2 == 0; })
        | std::views::transform([](int value) { return value * value; });

    std::vector<int> materialized;
    for (int value : result) {
        materialized.push_back(value);
    }

    assert((materialized == std::vector{4, 16, 36}));
}
~~~

Pipeline nie wykonuje pracy przy utworzeniu `result`; elementy są obliczane podczas iteracji. To może eliminować kolekcje pośrednie, ale wielokrotne przejście może ponawiać obliczenia. Nie każdy view jest common, sized lub random-access. Wymagania zależą od źródła i zastosowanych adapterów.

Lifetime jest kluczowy. View może przechowywać referencję do zakresu źródłowego albo posiadać rvalue range przez `owning_view`, zależnie od konstrukcji. `borrowed_range` pozwala określić, czy iterator wyniku może przetrwać zniszczenie obiektu range. Nie oznacza ogólnej gwarancji, że wszystkie elementy są wieczne.

C++23 dodaje kilka adapterów i usprawnień, lecz wsparcie konkretnej biblioteki standardowej trzeba sprawdzać feature-test macros. Jeśli końcowy API potrzebuje `vector`, zmaterializuj wynik jawnie; `std::ranges::to` jest C++23, ale lokalna implementacja może jeszcze go nie dostarczać.

## Jak to działa krok po kroku

Utworzenie pipeline przechowuje zakres bazowy oraz obiekty predykatu i transformacji. Przy rozpoczęciu iteracji filtr szuka pierwszego elementu spełniającego warunek, czyli liczby dwa. Dereferencja iteratora transformacji oblicza cztery. Inkrementacja przechodzi do następnego elementu spełniającego filtr, czyli cztery, a kolejna dereferencja daje szesnaście. Dopiero `push_back` zapisuje obliczoną wartość w kontenerze wynikowym.

Leniwość nie oznacza, że każda operacja zawsze kosztuje tyle samo ani że żaden adapter nigdy nie wykonuje przygotowania. Dla `filter_view` nad forward range pierwsze wyszukanie początku może być buforowane wewnątrz widoku. Transformacja zwykle następuje przy dereferencji, więc dwa odczyty tej samej pozycji mogą ponownie uruchomić funkcję. Nie projektuj kodu tak, aby poprawność zależała od dokładnej liczby jej wywołań.

Kolejność adapterów zmienia znaczenie i koszt. `filter | take(3)` wybiera pierwsze trzy pasujące elementy, a `take(3) | filter` filtruje jedynie pierwsze trzy elementy wejścia. `transform | filter` może obliczać transformację także dla odrzucanych danych. Rozpisanie pracy dla kilku elementów pozwala wykryć różnicę bez zgadywania na podstawie wyglądu operatorów `|`.

## Pogłębienie mechanizmu

`view` jest zakresem spełniającym dodatkowe wymagania dotyczące przenoszenia i kosztów operacji na jego reprezentacji. Nie oznacza zawsze obiektu niewłaścicielskiego. Adapter zastosowany do lvalue wektora zwykle korzysta z `ref_view`, a odpowiedni rvalue wektora może zostać przejęty przez `owning_view`. Wyjątkowa ostrożność jest potrzebna dla `initializer_list`, którego obiekt opisowy nie staje się właścicielem trwałej tablicy tylko dlatego, że został skopiowany.

`borrowed_range` odpowiada na węższe pytanie: czy same iteratory mogą pozostać użyteczne po zniszczeniu obiektu zakresu? Dla `string_view` mogą, jeżeli nadal żyją znaki. Dla właścicielskiego wektora zniszczenie zakresu niszczy także elementy. Dlatego algorytm ranges zwracający iterator z niepożyczanego rvalue może zwrócić `std::ranges::dangling`; zapobiega to przypadkowemu dereferencjonowaniu wyniku o utraconym właścicielu.

Nie każda właściwość źródła przetrwa adaptację. Filtr wektora nie zapewnia skoku do k-tego pasującego elementu w stałym czasie, więc traci random access oraz zwykle znany rozmiar. Transformacja może zachować dostęp losowy, ale zwracać wartości zamiast referencji. `const` zastosowane do obiektu widoku nie jest automatycznie odpowiednikiem widoku na stałe elementy. O dostępnej mutacji decyduje typ uzyskiwanej referencji oraz konstrukcja zakresu.

Zakres nie musi być skończony. `views::iota(0)` tworzy sekwencję, którą należy ograniczyć przed algorytmem wymagającym dojścia do końca. `take(n)` ogranicza liczbę wyników, ale filtr umieszczony przed nim nadal może bez końca szukać kolejnego dopasowania, jeśli predykat nigdy go nie znajdzie. Granica pracy i granica liczby wyprodukowanych wartości nie są tym samym. Dla strumieni zewnętrznych trzeba dodatkowo uwzględnić błędy, czas oczekiwania i zatrzymanie źródła.

## Drugi przykład

Funkcja może bezpiecznie zwrócić pipeline posiadający przeniesiony wektor. Utrwalać wynik trzeba dopiero wtedy, gdy potrzebna jest wielokrotna praca na gotowych danych.

~~~cpp
#include <cassert>
#include <ranges>
#include <utility>
#include <vector>

auto positive_squares(std::vector<int> input) {
    return std::views::all(std::move(input))
        | std::views::filter([](int n) { return n > 0; })
        | std::views::transform([](int n) { return n * n; });
}

int main() {
    auto owned = positive_squares({-2, 1, 3});
    std::vector<int> result;
    for (int value : owned) {
        result.push_back(value);
    }
    assert((result == std::vector<int>{1, 9}));

    const std::vector<int> source{1, 2, 3, 4, 5};
    auto first_two_even = source
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::take(2);
    int sum = 0;
    for (int n : first_two_even) sum += n;
    assert(sum == 6);
}
~~~

Argument `input` jest wartością, a jawne przeniesienie oddaje jego bufor do zakresu właścicielskiego. Zwrócenie pipeline zbudowanego z samego `input` jako lvalue pozostawiłoby referencję do lokalnego wektora. Składnia funkcji wyglądałaby podobnie, lecz model czasu życia byłby zupełnie inny. Przykład ogranicza wartości tak, aby kwadraty mieściły się w `int`.

## Porównanie i decyzje

Widoki pomagają przy jednokrotnym przetwarzaniu, szczególnie gdy odrzucają większość danych albo kończą po znalezieniu kilku wyników. Materializacja jest korzystna, gdy obliczenia są kosztowne i powtarzane, wynik musi mieć stabilną własność lub interfejs wymaga ciągłego bufora. C++23 `ranges::to` upraszcza materializację, ale zwykła pętla pozostaje przejrzystym wariantem kompatybilnym ze starszymi bibliotekami.

**Ćwiczenie.** Czy zmiana elementu wektora z nieparzystego na parzysty musi zostać zauważona przez istniejący `filter_view` dokładnie tak, jak przez nowo utworzony filtr? **Odpowiedź:** nie należy na tym polegać. Buforowany początek i wymagania iteratorów filtra komplikują mutowanie predykatu przez zmianę danych. Po takiej zmianie najczytelniej utworzyć widok ponownie; nie modyfikuj przez iterator filtra elementu tak, aby przestał spełniać predykat.

Źródła reguł: [C++23: zakresy](https://timsong-cpp.github.io/cppwp/n4950/ranges), [filter_view](https://timsong-cpp.github.io/cppwp/n4950/range.filter), [borrowed_range](https://timsong-cpp.github.io/cppwp/n4950/range.range).

## Powiązane tematy

- [Iteratory](04_iteratory_i_invalidacja.md)
- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Concepts](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
