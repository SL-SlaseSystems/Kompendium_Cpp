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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Ostrzeżenia i analiza statyczna”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz sformułowanie hipotezy, przygotowanie kontrolowanego wejścia, zebranie wyniku, porównanie z oczekiwaniem i zachowanie reprodukcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd funkcjonalny, undefined behavior, problem przenośności i regresję wydajności, ponieważ wymagają innych narzędzi. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przypadek, kod wyjścia, raport sanitizera, statystyczny rozkład pomiarów i konfigurację kompilacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Żadne pojedyncze narzędzie nie dowodzi poprawności programu C++. Test sprawdza zachowanie dla danych, analiza statyczna szuka wzorców, sanitizer obserwuje wykonanie, a profiler mierzy koszt; wiarygodność daje dopiero połączenie niezależnych dowodów. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Wysoki poziom ostrzeżeń wykrywa podejrzane konstrukcje podczas kompilacji, a analizator statyczny śledzi ścieżki, ownership i przepływ danych szerzej. Ostrzeżenia projektu warto traktować jako błędy, z kontrolowanymi wyjątkami dla kodu zewnętrznego.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Ostrzeżenia i analiza statyczna” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Ostrzeżenia i analiza statyczna
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Ostrzeżenia i analiza statyczna”, oceniaj zdolność wykrycia realnej regresji, powtarzalność, koszt utrzymania testu i reprezentatywność środowiska. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Kompilatory i toolchain](../01_wprowadzenie/03_kompilatory_i_toolchain.md)
- [Sanitizery i debugowanie](03_sanitizery_i_debuggery.md)
- [C++ Core Guidelines](../zrodla.md)

