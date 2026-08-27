[← Spis treści](../README.md)

# Testy jednostkowe i integracyjne

Standard C++ nie dostarcza frameworka testowego. Najprostszy test może być programem zwracającym niezerowy kod przy porażce. W praktyce Catch2, GoogleTest, doctest i Boost.Test oferują rejestrację przypadków, czytelne asercje, fixtures i integrację z runnerem. Są to biblioteki zewnętrzne.

~~~cpp
#include <cassert>
#include <stdexcept>

int divide(int numerator, int denominator) {
    if (denominator == 0) {
        throw std::invalid_argument{"zero denominator"};
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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Testy jednostkowe i integracyjne”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz sformułowanie hipotezy, przygotowanie kontrolowanego wejścia, zebranie wyniku, porównanie z oczekiwaniem i zachowanie reprodukcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd funkcjonalny, undefined behavior, problem przenośności i regresję wydajności, ponieważ wymagają innych narzędzi. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przypadek, kod wyjścia, raport sanitizera, statystyczny rozkład pomiarów i konfigurację kompilacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Żadne pojedyncze narzędzie nie dowodzi poprawności programu C++. Test sprawdza zachowanie dla danych, analiza statyczna szuka wzorców, sanitizer obserwuje wykonanie, a profiler mierzy koszt; wiarygodność daje dopiero połączenie niezależnych dowodów. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Test jednostkowy izoluje mały kontrakt, integracyjny sprawdza współpracę realnych granic, a end-to-end cały przepływ. Double ma wartość tylko wtedy, gdy zachowuje kontrakt, którego test naprawdę potrzebuje.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Testy jednostkowe i integracyjne” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Testy jednostkowe i integracyjne
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Testy jednostkowe i integracyjne”, oceniaj zdolność wykrycia realnej regresji, powtarzalność, koszt utrzymania testu i reprezentatywność środowiska. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [CMake](../08_budowanie_i_organizacja/05_cmake.md)
- [Fuzzing](05_fuzzing_i_property_based_testing.md)
- [Assertions i kontrakty](../07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)

