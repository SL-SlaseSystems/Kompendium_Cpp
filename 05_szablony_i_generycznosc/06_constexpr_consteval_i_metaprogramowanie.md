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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „constexpr, consteval i metaprogramowanie”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `consteval` wymaga constant evaluation każdego potencjalnie ocenianego wywołania, natomiast funkcja `constexpr` może działać zarówno podczas kompilacji, jak i runtime. Constant evaluation nadal przestrzega reguł języka i diagnozuje niedozwolone operacje.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „constexpr, consteval i metaprogramowanie” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: constexpr, consteval i metaprogramowanie
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „constexpr, consteval i metaprogramowanie”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Zmienne, const i constexpr](../02_podstawy_jezyka/03_zmienne_const_i_constexpr.md)
- [Zaawansowany compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)
- [Concepts](04_concepts_i_requires.md)

