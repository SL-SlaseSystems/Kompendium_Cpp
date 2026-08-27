[← Spis treści](../README.md)

# Benchmarki i profilowanie

Benchmark mierzy określony scenariusz, a profiler wskazuje, gdzie program spędza czas lub alokuje pamięć. Zanim zoptymalizujesz kod, ustal metrykę, reprezentatywne dane i budżet. Pomiar debug build zwykle nie mówi nic o docelowej wydajności.

~~~cpp
#include <algorithm>
#include <cassert>
#include <chrono>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> values(10'000);
    std::iota(values.begin(), values.end(), 1);

    const auto start = std::chrono::steady_clock::now();
    std::ranges::sort(values, std::greater{});
    const auto elapsed = std::chrono::steady_clock::now() - start;

    assert(values.front() == 10'000);
    assert(elapsed >= std::chrono::steady_clock::duration::zero());
}
~~~

Przykład pokazuje mechanikę zegara, ale nie jest dobrym mikrobenchmarkiem. Pojedynczy pomiar podlega rozgrzewce cache, harmonogramowi systemu, zmianom częstotliwości i eliminacji pracy przez optymalizator. Google Benchmark jest biblioteką zewnętrzną, która pomaga powtarzać pomiary i raportować rozkład, lecz również wymaga poprawnego projektu eksperymentu.

Używaj `steady_clock` do odstępów czasu; nie może cofać się wskutek korekty zegara ściennego. Zapewnij, że wynik obliczenia jest obserwowalny, aby optimizer nie usunął pracy. Mierz wersję release z właściwym linkowaniem, LTO i danymi podobnymi do produkcyjnych.

Sampling profiler ma mniejszy narzut i pokazuje hot paths. Instrumentation profiler liczy zdarzenia dokładniej kosztem wpływu na program. Hardware counters pomagają analizować cache misses, branch misprediction i instrukcje. Flame graph jest wizualizacją próbek, nie źródłem danych samym w sobie.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Benchmarki i profilowanie”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz sformułowanie hipotezy, przygotowanie kontrolowanego wejścia, zebranie wyniku, porównanie z oczekiwaniem i zachowanie reprodukcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd funkcjonalny, undefined behavior, problem przenośności i regresję wydajności, ponieważ wymagają innych narzędzi. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przypadek, kod wyjścia, raport sanitizera, statystyczny rozkład pomiarów i konfigurację kompilacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Żadne pojedyncze narzędzie nie dowodzi poprawności programu C++. Test sprawdza zachowanie dla danych, analiza statyczna szuka wzorców, sanitizer obserwuje wykonanie, a profiler mierzy koszt; wiarygodność daje dopiero połączenie niezależnych dowodów. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Mikrobenchmark wymaga warm-up, przeciwdziałania usunięciu pracy przez optimizer i analizy rozkładu, nie jednego czasu. Profil odpowiada, gdzie program zużywa zasoby na reprezentatywnym obciążeniu, zanim powstanie hipoteza optymalizacji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Benchmarki i profilowanie” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Benchmarki i profilowanie
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Benchmarki i profilowanie”, oceniaj zdolność wykrycia realnej regresji, powtarzalność, koszt utrzymania testu i reprezentatywność środowiska. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
- [SIMD i optymalizacja](../zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)
- [chrono](../11_io_i_system/03_chrono_i_czas.md)

