[← Spis treści](../README.md)

# constexpr, consteval i metaprogramowanie

Metaprogramowanie w C++ może obliczać typy i wartości podczas kompilacji. Historycznie opierało się głównie na specjalizacjach szablonów. Współczesny C++ pozwala często pisać zwykłe funkcje `constexpr`, instrukcje `if constexpr`, pętle i lokalne zmienne, co daje czytelniejszy kod.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>

constexpr unsigned factorial(unsigned value) {
    unsigned result = 1;
    for (unsigned current = 2; current <= value; ++current) {
        result *= current;
    }
    return result;
}

template<std::size_t N>
constexpr auto squares() {
    std::array<unsigned, N> result{};
    for (std::size_t i = 0; i < N; ++i) {
        result[i] = static_cast<unsigned>(i * i);
    }
    return result;
}

int main() {
    constexpr auto values = squares<4>();
    static_assert(factorial(5) == 120);
    static_assert(values[3] == 9);
    assert(factorial(3) == 6);
}
~~~

Funkcja `constexpr` może być wywołana w runtime, jeśli kontekst nie wymaga stałej. `consteval` tworzy immediate function, której potencjalnie ewaluowane wywołania muszą być stałe. `constinit` dotyczy inicjalizacji obiektów statycznych i nie jest zamiennikiem tych dwóch mechanizmów.

`if constexpr` odrzuca niewybraną gałąź podczas instancjacji, co umożliwia różne implementacje zależne od typu. Type traits z `<type_traits>` reprezentują własności i transformacje typów. Concepts powinny opisywać publiczne wymagania, a `if constexpr` wybierać implementację wewnątrz poprawnego kontraktu.

Compile time nie jest darmowy. Nadmierna liczba instancjacji zwiększa czas budowania, pamięć kompilatora i rozmiar binarium. Korzyścią może być weryfikacja inwariantów oraz brak kosztu runtime, ale decyzję należy mierzyć na pełnym projekcie.

## Jak to działa krok po kroku

Wywołanie funkcji `constexpr` ma dwa możliwe konteksty. Jeżeli wynik służy jako inicjalizator zmiennej `constexpr`, warunek `static_assert` lub odpowiedni argument szablonu, obliczenie musi spełnić reguły stałego wyrażenia. Przy zwykłym wywołaniu z danymi runtime ta sama funkcja działa podczas wykonania, chyba że optymalizator zgodnie z regułą as-if uprości wynik.

W `squares<4>()` parametr szablonu określa długość zwracanego `std::array`. Funkcja tworzy lokalną tablicę, wykonuje pętlę i zapisuje wyniki do jej elementów. Takie zmienne i pętle są dozwolone w nowoczesnych funkcjach `constexpr`; nie trzeba reprezentować każdego kroku kolejną instancją rekurencyjnego szablonu. `static_assert` sprawdza potem konkretny element jako część warunku kompilacji.

`consteval` opisuje funkcję natychmiastową. Wywołanie w kontekście wymagającym immediate invocation musi być stałym wyrażeniem; zwykłe dane od użytkownika nie mogą po prostu stać się jej argumentami. Istnieją specjalne konteksty wewnątrz innych funkcji natychmiastowych i gałęzi `if consteval`, dlatego reguła jest precyzyjniejsza niż „każdy zapis wywołania musi zawierać same literały”.

## Pogłębienie mechanizmu

Stałe obliczenie nie może na ocenianej ścieżce wykonywać operacji wykluczonych przez reguły, takich jak odpowiednie UB lub wywołanie nieprzystosowanej funkcji runtime. Dzielenie przez zero albo signed overflow w wymaganym stałym wyrażeniu prowadzi do błędu kompilacji. Przepełnienie unsigned nadal jest zdefiniowaną arytmetyką modulo i nie staje się automatycznie błędem tylko dlatego, że obliczenie zachodzi wcześniej.

Pierwszy `factorial` używa unsigned, więc dla zbyt dużej wartości daje wynik modulo, który nie jest matematyczną silnią. Pętla ma też warunek wymagający ostrożności przy maksymalnej wartości argumentu. Przykład ilustruje mechanizm na małych liczbach, nie stanowi walidowanego API dowolnej silni. Obliczenia compile-time potrzebują tych samych przemyślanych granic co runtime.

`if constexpr` wybiera gałąź na podstawie warunku stałego. W szablonie niewybrana gałąź zależna nie jest instancjonowana, dzięki czemu jedna funkcja może obsługiwać różne operacje typów. Nadal obowiązuje poprawna składnia i analiza niezależnych konstrukcji. Zwykłe `if` nie ma takiej własności. Z kolei `if consteval`, dodane w C++23, rozróżnia kontekst ewaluacji, nie typ argumentu.

`std::is_constant_evaluated()` od C++20 pozwala pytać o stałą ewaluację. Umieszczenie go bezrefleksyjnie jako warunku `if constexpr` nie sprawdza runtime'owej sytuacji danego wywołania, ponieważ sam warunek `if constexpr` wymaga stałej ewaluacji. Zwykły `if` lub `if consteval` lepiej wyraża odpowiedni podział. Alternatywne ścieżki powinny utrzymywać sensowny wspólny kontrakt wyników.

Od C++20 pewne dynamiczne alokacje mogą występować podczas stałej ewaluacji, ale muszą być odpowiednio rozliczone w jej obrębie. Lokalny `vector` może służyć jako przestrzeń robocza, jeśli implementacja biblioteki obsługuje wymagane operacje constexpr. Nie wynika z tego ogólna możliwość umieszczenia dowolnego bufora dynamicznego w trwałej wartości `constexpr` zwracanej poza ewaluację.

Type traits, takie jak `remove_cvref_t`, obliczają typy. Funkcje `constexpr` obliczają wartości. Łączenie obu narzędzi jest naturalne, lecz nie wymaga budowania rekurencyjnych klas dla prostego sumowania. Koszt wielu specjalizacji i dużych tabel stałych może obciążać kompilator oraz zwiększać binarium, więc przeniesienie pracy do kompilacji powinno odpowiadać konkretnemu wymaganiu.

## Drugi przykład

Walidowana funkcja wyznacza rozmiar tablicy. Jej błędne wywołanie podczas wymaganej ewaluacji nie może przejść do wykonania programu, ponieważ oceniana ścieżka rzuca wyjątek.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <stdexcept>

consteval std::size_t bounded_size(int requested) {
    if (requested < 1 || requested > 64) {
        throw std::invalid_argument{"size outside [1, 64]"};
    }
    return static_cast<std::size_t>(requested);
}

constexpr int magnitude(int value) {
    return value < 0 ? -value : value;
}

int main() {
    std::array<int, bounded_size(8)> buffer{};
    static_assert(magnitude(-7) == 7);
    int input = -5;
    assert(magnitude(input) == 5);
    assert(buffer.size() == 8);
    // std::array<int, bounded_size(0)> invalid; // celowy błąd kompilacji
}
~~~

`throw` jest legalnie zapisany w funkcji, ale jego wykonanie na ścieżce wymaganej stałej ewaluacji odrzuca ten inicjalizator. Funkcja `magnitude` ma osobny warunek dziedzinowy: nie należy przekazywać najmniejszego `int`, którego dodatnia wartość nie mieści się w tym typie. Samo `constexpr` nie dodaje kontroli tego zakresu.

## Porównanie i decyzje

Wybieraj `constexpr` dla wspólnego algorytmu stałego i dynamicznego, `consteval` dla operacji mającej odrzucać niewłaściwą konfigurację przy kompilacji, a concepts dla dostępności interfejsu zależnej od typów. `constinit` służy innemu celowi: wymusza odpowiednią statyczną inicjalizację obiektu, który może później zmieniać wartość.

**Ćwiczenie.** Czy `constexpr unsigned result = maximum_unsigned + 1u;` musi wywołać błąd, jeśli `maximum_unsigned` jest maksymalnym unsigned?

**Odpowiedź.** Nie. Arytmetyka unsigned jest zdefiniowana modulo i wynikiem jest zero. Jeżeli zero oznacza błąd domeny, trzeba wprowadzić osobne sprawdzenie. Obliczenie podczas kompilacji gwarantuje zgodność z regułami języka, nie z niewyrażoną intencją matematyczną.

Źródła: [stałe wyrażenia](https://timsong-cpp.github.io/cppwp/n4950/expr.const), [constexpr i consteval](https://timsong-cpp.github.io/cppwp/n4950/dcl.constexpr), [if constexpr i if consteval](https://timsong-cpp.github.io/cppwp/n4950/stmt.if).

## Powiązane tematy

- [Zmienne, const i constexpr](../02_podstawy_jezyka/03_zmienne_const_i_constexpr.md)
- [Zaawansowany compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)
- [Concepts](04_concepts_i_requires.md)

