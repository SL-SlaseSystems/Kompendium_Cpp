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

Najpierw postaw mierzalne pytanie: czas posortowania określonej liczby rekordów, liczba obsłużonych żądań na sekundę albo opóźnienie dziewięćdziesiątego dziewiątego percentyla. To różne cele. Optymalizacja przepustowości może pogorszyć opóźnienie pojedynczego żądania, gdy zwiększa grupowanie pracy. Bez wybranej metryki łatwo ogłosić sukces na podstawie liczby niepowiązanej z potrzebą użytkownika.

Ustal, co znajduje się w mierzonym odcinku. Jeśli porównujesz same algorytmy sortowania, generowanie danych i kopiowanie wejścia powinno być osobno. Jeśli oceniasz całą operację aplikacyjną, alokacja, dekodowanie i zapis wyniku mogą należeć do kosztu. Obie wersje są sensowne, ale odpowiadają na inne pytania. Zapisz tę granicę obok wyniku, aby ktoś inny mógł odtworzyć eksperyment.

Powtarzaj pracę na odpowiednich danych. Sortowanie raz losowego, a potem wielokrotnie już posortowanego wektora zmienia scenariusz. Podobnie wyszukiwanie ciągle tego samego klucza rozgrzewa cache i predyktor inaczej niż produkcyjna mieszanka. Oddziel rozgrzewkę od pomiarów i zbieraj wiele próbek, zamiast wybierać pojedynczy najlepszy czas.

## Pogłębienie mechanizmu

Optymalizator może usunąć obliczenie, którego wynik nie wpływa na obserwowalne zachowanie. `volatile` nie jest ogólnym rozwiązaniem: zmienia generowane dostępy do obiektu i może mierzyć koszt innej operacji. Biblioteki benchmarkowe udostępniają narzędzia takie jak `DoNotOptimize` i `ClobberMemory`, lecz trzeba rozumieć ich granice. Nawet one nie nakazują zachowania dowolnego zbędnego podwyrażenia w dokładnie oczekiwanej postaci.

Średnia może ukrywać sporadyczne długie przerwy. Mediana opisuje typowy pomiar, percentyle pomagają badać ogon, a rozrzut pokazuje stabilność. Próbki nie zawsze są niezależne: temperatury procesora, skalowanie częstotliwości i inne procesy mogą zmieniać warunki przez całą serię. Porównuj wersje w podobnych warunkach i przeplataj kolejność, gdy powolny dryf maszyny wpływa na wynik.

Profiler próbkowy pokazuje udział zebranych próbek stosu. Szeroki prostokąt flame graph oznacza wiele próbek w danej gałęzi, nie koniecznie jedną bardzo wolną funkcję. Koszt włączny obejmuje wywołanych potomków, a własny dotyczy samej funkcji. Profil CPU może nie wyjaśnić opóźnień programu czekającego na dysk, sieć lub mutex; potrzebne są także dane o oczekiwaniu i czasie ściennym.

Prawo Amdahla ogranicza zysk całego programu: przyspieszenie niewielkiego fragmentu ma niewielki wpływ na sumę. Jeśli parser zajmuje dziesięć procent czasu, jego dwukrotne przyspieszenie redukuje całość tylko o pięć procent przy niezmienionym pozostałym koszcie. Po zmianie profiluj ponownie, ponieważ wąskie gardło może przenieść się w inne miejsce. Wynik mikrobenchmarku nie zastępuje pomiaru pełnego przepływu.

## Drugi przykład

Program zbiera kilka czasów sortowania, odtwarza to samo wejście przed każdą próbą i sprawdza wynik poza mierzonym odcinkiem. Jest samodzielnym ćwiczeniem metodologii, a nie gotowym dowodem przewagi konkretnego algorytmu.

~~~cpp
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

int main() {
    std::mt19937 generator{12345};
    std::vector<std::uint32_t> source(20'000);
    for (auto& value : source) value = generator();
    std::vector<double> samples;
    std::uint64_t checksum = 0;
    for (int trial = 0; trial < 9; ++trial) {
        auto values = source;
        const auto start = std::chrono::steady_clock::now();
        std::ranges::sort(values);
        const auto end = std::chrono::steady_clock::now();
        if (!std::ranges::is_sorted(values)) return 1;
        checksum += values[values.size() / 2];
        if (trial != 0) {
            samples.push_back(std::chrono::duration<double, std::micro>(end - start).count());
        }
    }
    std::ranges::sort(samples);
    std::cout << "middle sample [us]: " << samples[samples.size() / 2]
              << ", checksum: " << checksum << '\n';
}
~~~

Pierwsza próba służy rozgrzewce i nie trafia do zestawu. Wypisany checksum wiąże wynik pracy z obserwowalnym zachowaniem, ale przy bardzo agresywnej optymalizacji nadal warto sprawdzić wygenerowany kod i użyć dedykowanej biblioteki pomiarowej. Kopiowanie wejścia jest poza odcinkiem, lecz wpływa na stan cache. Otrzymujemy więc pomiar sortowania danych po świeżym kopiowaniu, a nie dowolnego możliwego stanu pamięci.

## Porównanie i decyzje

Mikrobenchmark pomaga rozstrzygnąć konkretny wybór w gorącym fragmencie; benchmark aplikacyjny pokazuje wartość dla całości. Profilowanie wskazuje kandydatów, a eksperyment potwierdza efekt zmiany. Zachowaj wersję kompilatora, flagi, sprzęt, rozmiary danych i surowe próbki wraz z wynikiem. Bez tych informacji niewielka procentowa różnica może być niemożliwa do odróżnienia od szumu.

**Ćwiczenie.** Wersja B jest szybsza dla stu elementów, ale wolniejsza dla miliona. Czy benchmark jest sprzeczny? **Odpowiedź:** nie. Koszty stałe, złożoność, alokacje i hierarchia cache zmieniają znaczenie wraz z rozmiarem. Decyzję należy odnieść do rzeczywistego rozkładu wejść, ewentualnie zastosować różne strategie dla uzasadnionych zakresów.

Źródła: [Google Benchmark: przewodnik pomiarów](https://google.github.io/benchmark/user_guide.html), [LLVM: benchmarkowanie](https://llvm.org/docs/Benchmarking.html), [C++23: steady_clock](https://timsong-cpp.github.io/cppwp/n4950/time.clock.steady).

## Powiązane tematy

- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
- [SIMD i optymalizacja](../zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)
- [chrono](../11_io_i_system/03_chrono_i_czas.md)
