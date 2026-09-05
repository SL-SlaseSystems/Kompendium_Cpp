[← Spis treści](../README.md)

# Sterowanie przepływem

Instrukcje `if`, `switch`, `while`, `do`, `for` oraz range-based `for` sterują wykonaniem. Warunek jest kontekstowo konwertowany do `bool`. C++17 pozwala umieścić inicjalizator przed warunkiem `if` i `switch`, co ogranicza zakres pomocniczej zmiennej.

~~~cpp
#include <cassert>
#include <vector>

int sum_positive(const std::vector<int>& values) {
    int total = 0;
    for (const int value : values) {
        if (value < 0) {
            continue;
        }
        total += value;
    }
    return total;
}

int main() {
    const auto values = std::vector{3, -2, 5};
    if (const int result = sum_positive(values); result > 0) {
        assert(result == 8);
    } else {
        return 1;
    }
}
~~~

Range-based `for` pobiera element zgodnie z deklaracją zmiennej pętli. `auto element` kopiuje, `auto&` daje modyfikowalną referencję, a `const auto&` odczyt bez kopiowania. Przy proxy references, np. w `std::vector<bool>`, `auto&&` może lepiej zachować semantykę elementu.

`switch` działa na typach całkowitych i enumach. Brak `break` powoduje przejście do kolejnej etykiety; jeśli jest zamierzone, zaznacz je `[[fallthrough]]`. `break` kończy najbliższą pętlę lub switch, a `continue` rozpoczyna następną iterację. `goto` istnieje, lecz zwykle przegrywa z funkcją, RAII i czytelnym przepływem; nie można nim bezkarnie omijać inicjalizacji obiektów.

## Jak to działa krok po kroku

Zwykły `for` wykonuje inicjalizator raz, potem sprawdza warunek, wykonuje ciało i oblicza wyrażenie iteracyjne. Po `continue` nadal wykonuje wyrażenie iteracyjne, zanim znów sprawdzi warunek. W `while` instrukcja `continue` przechodzi bezpośrednio do warunku. Dlatego mechaniczne przepisanie pętli między tymi postaciami może pominąć zwiększenie indeksu i stworzyć nieskończoną pętlę.

W początkowym przykładzie każda ujemna liczba omija dodawanie. Zero jest dodawane, lecz nie zmienia wyniku; nazwa `sum_positive` jest więc zgodna z wynikiem, choć warunek przepuszcza też zero. Suma typu `int` ma wymaganie, aby kolejne wyniki mieściły się w zakresie. Poprawna składnia pętli nie gwarantuje poprawności arytmetyki dla dowolnie dużego wejścia.

Range-based `for` tworzy wewnętrznie dostęp do zakresu oraz jego początku i końca. Przy każdej iteracji dereferencjonuje bieżący iterator i inicjalizuje deklarowaną zmienną elementu. `auto` może więc kopiować, a referencja pozwala operować na samym elemencie. Początek i koniec są uzyskiwane przed iteracjami; modyfikowanie kontenera tak, że unieważnia iteratory lub zapamiętany koniec, może zepsuć pętlę nawet wtedy, gdy aktualny element nadal istnieje.

## Pogłębienie mechanizmu

`break` kończy najbliższą otaczającą pętlę albo `switch`, lecz nie wszystkie zagnieżdżone konstrukcje. `continue` dotyczy najbliższej pętli, nawet jeśli zapisano je wewnątrz `switch`. W złożonym wyszukiwaniu pomocna bywa osobna funkcja i `return`, które jasno kończy całe zadanie. W każdym zwykłym wyjściu z zakresu lokalne obiekty są niszczone, również po `break`, `continue` i `return`.

Etykiety `case` same nie tworzą zakresów. Przejście bezpośrednio do etykiety nie może pomijać niedozwolonej inicjalizacji lokalnego obiektu. Jeżeli gałąź potrzebuje zmiennej, obejmij jej ciało klamrami. `[[fallthrough]];` sygnalizuje zamierzone przejście do następnej etykiety; nie wykonuje skoku ani nie zastępuje `break`.

`if constexpr` od C++17 jest mechanizmem wyboru podczas instancjacji szablonu. Zwykły `if`, nawet z warunkiem `false`, nadal wymaga poprawności obu gałęzi. W `if constexpr` niewybrana zależna gałąź szablonu nie jest instancjonowana, lecz nie można umieszczać tam dowolnie błędnej składni. Poza szablonem także nie jest to ogólny sposób ukrywania błędnego programu.

C++23 rozszerza przedłużanie życia obiektów tymczasowych w inicjalizatorze pętli zakresowej. Nadal nie naprawia funkcji, która sama zwraca referencję do już zniszczonego parametru lub lokalnego obiektu. Jawny inicjalizator pętli, dostępny od C++20, jest dobrym sposobem przechowania właściciela danych: `for (auto owner = make(); const auto& x : owner.items())`. W ten sposób zależność życia jest widoczna również dla czytelnika.

## Drugi przykład

Usuwanie podczas iteracji powinno korzystać z iteratora zwracanego przez `erase`. Po usunięciu nie zwiększamy starego iteratora, ponieważ dla wektora przestał być ważny.

~~~cpp
#include <cassert>
#include <vector>

int main() {
    std::vector values{1, -2, 3, -4, 5};
    for (auto it = values.begin(); it != values.end();) {
        if (*it < 0) {
            it = values.erase(it);
        } else {
            ++it;
        }
    }
    assert((values == std::vector{1, 3, 5}));

    int total = 0;
    for (int& value : values) {
        value *= 2;
        total += value;
    }
    assert(total == 18);
}
~~~

Pierwsza pętla świadomie ponownie pobiera `end()` w warunku. Zwykły zakresowy `for` nie zastępuje jej poprawnie, ponieważ usuwanie unieważnia iteratory. Dla samego filtrowania od C++20 prostsze jest `std::erase_if`; ręczny zapis służy tu prześledzeniu reguł i jest przydatny, gdy z usuwaniem łączą się dodatkowe operacje.

## Porównanie i decyzje

Warunek pętli powinien odpowiadać temu, co faktycznie gwarantuje jej ciało. Przy indeksie bez znaku zapis `i >= 0` jest zawsze prawdziwy i nie nadaje się do zakończenia odliczania w dół. Bezpieczny schemat może zaczynać od rozmiaru i sprawdzać `i > 0`, a używać elementu `i - 1`. Trzeba rozpatrzyć także pusty zakres, zanim wykona się pierwsze odejmowanie.

Wybieraj zakresowy `for`, gdy odwiedzasz elementy bez strukturalnej zmiany kontenera. Użyj indeksu, kiedy pozycja jest częścią obliczenia, a iteratora, gdy operacja zwraca nowe miejsce kontynuacji. Algorytm standardowy jest wygodniejszy, gdy zadanie ma wyraźną nazwę, taką jak wyszukanie, zliczenie lub filtrowanie.

**Ćwiczenie.** Pętla ma postać `while (i < n) { if (skip(i)) continue; ++i; }`. Dlaczego może się nie skończyć?

**Odpowiedź.** Dla wartości, dla której `skip(i)` zwraca prawdę, `continue` omija zwiększenie `i`. Kolejne sprawdzenie widzi ten sam indeks. Przeniesienie zwiększania do części iteracyjnej `for` zapewnia wykonanie także po `continue`, jeśli taki przebieg odpowiada kontraktowi.

Źródła: [instrukcje iteracyjne](https://timsong-cpp.github.io/cppwp/n4950/stmt.iter), [pętla zakresowa](https://timsong-cpp.github.io/cppwp/n4950/stmt.ranged), [instrukcje wyboru](https://timsong-cpp.github.io/cppwp/n4950/stmt.select).

## Powiązane tematy

- [Algorytmy i lambdy](../06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
- [enum i variant](../04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)
- [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md)

