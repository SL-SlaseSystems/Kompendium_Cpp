[← Spis treści](../README.md)

# Dedukcja, auto, decltype i CTAD

Dedukcja typu ogranicza powtarzanie informacji, ale działa według konkretnych reguł. `auto` dedukuje podobnie do parametru szablonu przekazywanego przez wartość: usuwa referencję i najwyższy poziom `const`. `auto&`, `const auto&` oraz `auto&&` mają inne zachowanie. `decltype(expr)` zachowuje kategorię wartości według szczególnej reguły dla nieujętej w nawiasy nazwy.

~~~cpp
#include <cassert>
#include <type_traits>
#include <utility>
#include <vector>

int main() {
    const int value = 3;
    auto copy = value;
    const auto& reference = value;
    decltype(auto) exact = (value);
    std::pair pair{1, 2.5}; // CTAD

    static_assert(std::is_same_v<decltype(copy), int>);
    static_assert(std::is_same_v<decltype(reference), const int&>);
    static_assert(std::is_same_v<decltype(exact), const int&>);
    assert(pair.first == 1);
}
~~~

Nawiasy w `decltype((value))` sprawiają, że analizowane jest wyrażenie lvalue i wynikiem jest referencja. To użyteczne w kodzie generycznym, ale może przypadkowo zwrócić dangling reference. `decltype(auto)` w typie zwracanym należy stosować tylko wtedy, gdy dokładne propagowanie referencji jest świadomą częścią API.

CTAD (*class template argument deduction*) pozwala wywnioskować parametry szablonu klasy z konstruktora lub deduction guide. `std::pair pair{1, 2.5}` daje `pair<int, double>`. Nie każda pożądana semantyka wynika z konstruktorów, więc biblioteka może dostarczyć własne guides. Alias template deduction ma dodatkowe ograniczenia implementacyjne i wersyjne.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Dedukcja, auto, decltype i CTAD”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `auto` stosuje reguły zbliżone do dedukcji parametru szablonu i zwykle usuwa referencję oraz top-level const. `decltype(expr)` zachowuje typ zależnie od formy wyrażenia, a `decltype((name))` uwzględnia kategorię wartości.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Dedukcja, auto, decltype i CTAD” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Dedukcja, auto, decltype i CTAD
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Dedukcja, auto, decltype i CTAD”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Pułapki

`auto list{1, 2}` i `auto value{1}` nie dedukują zawsze tego samego rodzaju konstrukcji; reguły inicjalizacji listowej mają szczególne przypadki. Nie polegaj na dedukcji, jeśli jawny typ dokumentuje jednostkę, precyzję, własność lub koszt konwersji.

## Powiązane tematy

- [Szablony funkcji i klas](01_function_i_class_templates.md)
- [Value categories i forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)

