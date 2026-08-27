[← Spis treści](../README.md)

# Zmienne, const i constexpr

Zmienna wiąże nazwę z obiektem. `const` zabrania modyfikacji przez daną ścieżkę dostępu, lecz nie zawsze oznacza, że wartość powstała podczas kompilacji. `constexpr` deklaruje obiekt albo funkcję możliwą do użycia w constant expression, jeśli argumenty i wykonana ścieżka spełniają wymagania. `consteval` wymaga ewaluacji wywołania w czasie kompilacji.

~~~cpp
#include <array>
#include <cassert>

constexpr int square(int value) {
    return value * value;
}

consteval int checked_size(int value) {
    return value > 0 ? value : 1;
}

int main() {
    constexpr int count = checked_size(4);
    std::array<int, count> values{1, 2, 3, 4};
    const int runtime_sum = values[0] + values[1];

    static_assert(square(count) == 16);
    assert(runtime_sum == 3);
}
~~~

`constinit` nie czyni obiektu niezmiennym. Wymusza statyczną inicjalizację zmiennej o static lub thread storage duration i pomaga uniknąć części problemów kolejności inicjalizacji. `volatile` również nie służy do synchronizacji wątków; opisuje szczególne dostępy istotne dla implementacji, np. niektóre rejestry sprzętowe. Do komunikacji między wątkami używa się atomików i synchronizacji.

`auto` dedukuje typ z inicjalizatora i usuwa najwyższy poziom `const` oraz referencję według reguł podobnych do dedukcji szablonów. `const auto&` zachowuje dostęp referencyjny i często jest dobrym wyborem dla odczytu dużej wartości. Nie używaj `auto` do ukrywania istotnej konwersji lub niejasnej własności.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Zmienne, const i constexpr”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `const` blokuje modyfikację przez dany dostęp, lecz nie zawsze czyni wartość stałą czasu kompilacji. `constexpr` nakłada wymagania umożliwiające constant evaluation, a konkretny odczyt nadal może nastąpić w runtime.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Zmienne, const i constexpr” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Zmienne, const i constexpr
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Zmienne, const i constexpr”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Inicjalizuj obiekty natychmiast. Stosuj `const` domyślnie dla nazw, których nie trzeba modyfikować. Używaj `constexpr`, kiedy operacja ma sens zarówno w compile time, jak i runtime, a `consteval` tylko gdy brak wyniku compile-time ma być błędem. Nie traktuj compile-time jako darmowego: może zwiększać czas kompilacji i rozmiar diagnostyki.

## Powiązane tematy

- [Dedukcja, auto i decltype](../05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
- [Compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)
- [Atomiki](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)

