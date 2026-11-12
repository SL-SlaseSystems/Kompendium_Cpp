[← Spis treści](../README.md)

# Metodologia benchmarków

Benchmark jest eksperymentem odpowiadającym na konkretne pytanie o koszt pracy programu. „Wersja B jest szybsza” wymaga określenia danych, wielkości problemu, konfiguracji kompilacji, sprzętu i mierzonej wielkości. Czas całego żądania, czas CPU, przepustowość oraz liczba alokacji opisują inne własności. Dobry eksperyment ustala także, jaki wynik wpłynie na decyzję: oszczędność istotna dla użytkownika może być dużo większa niż różnica widoczna w mikrobenchmarku.

Pierwszym punktem odniesienia jest poprawna wersja bazowa wykonująca tę samą pracę. Nie porównujemy parsera sprawdzającego błędy z funkcją przyjmującą wyłącznie poprawne dane, jeżeli produkcyjny kontrakt wymaga walidacji. Przed pomiarem obie implementacje powinny przejść te same testy poprawności. Następnie zmieniamy jedną hipotezę, na przykład sposób przechodzenia przez dane, i mierzymy skutek. Optymalizacja, która zmienia wynik, nie jest równoważnym rozwiązaniem.

## Jak to działa krok po kroku

Najpierw wybieramy obciążenie: rozmiar danych, rozkład wartości, udział trafień oraz stan pamięci podręcznej. Dane tworzymy poza mierzonym fragmentem, jeżeli pytanie dotyczy samego przetwarzania. Jeśli interesuje nas pełny koszt operacji, uwzględniamy również alokację, parsowanie i sprzątanie. W obu wariantach trzeba podać granice pomiaru. Inaczej ten sam kod może służyć do udowodnienia sprzecznych tez.

Poniższy program mierzy całe partie sumowania. Dane zależą od argumentów uruchomienia, wynik jest użyty po pomiarze, a każda iteracja zmienia jeden element. Ta modyfikacja zapobiega prostemu zastąpieniu identycznych wywołań jednym obliczeniem, ale stanowi również część mierzonej pracy. Program pokazuje konstrukcję eksperymentu, a nie przenośną barierę optymalizacji.

~~~cpp
#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

int main(int argc, char**) {
    constexpr std::size_t count = 1U << 18;
    constexpr std::size_t rounds = 32;
    std::vector<std::uint32_t> data(count);
    std::uint64_t state = static_cast<std::uint64_t>(argc);
    for (auto& value : data) {
        state = state * 6364136223846793005ULL + 1;
        value = static_cast<std::uint32_t>(state >> 32);
    }
    std::vector<double> samples;
    std::uint64_t checksum{};
    for (std::size_t sample = 0; sample < 7; ++sample) {
        const auto begin = std::chrono::steady_clock::now();
        for (std::size_t round = 0; round < rounds; ++round) {
            data[round] ^= static_cast<std::uint32_t>(sample + round);
            checksum += std::accumulate(data.begin(), data.end(),
                                        std::uint64_t{0});
        }
        const auto end = std::chrono::steady_clock::now();
        samples.push_back(
            std::chrono::duration<double, std::milli>(end - begin).count());
    }
    std::ranges::sort(samples);
    std::cout << "batch_ms min=" << samples.front()
              << " median=" << samples[samples.size() / 2]
              << " max=" << samples.back()
              << " checksum=" << checksum << '\n';
}
~~~

`steady_clock` nadaje się do pomiaru upływu czasu, ponieważ nie jest zegarem kalendarzowym podlegającym korektom daty. Nie oznacza to nieograniczonej rozdzielczości ani braku kosztu odczytu. Partia powinna trwać wystarczająco długo, aby narzut zegara nie dominował nad badaną pracą. Dla bardzo krótkich funkcji używamy narzędzia benchmarkowego z odpowiednim mechanizmem użycia wyniku oraz sprawdzamy wygenerowany kod.

Przykład kompilujemy z optymalizacją, na przykład `clang++ -std=c++23 -O3 bench.cpp -o bench`, i uruchamiamy poza debuggerem. Konfigurację diagnostyczną lub sanitizer mierzymy osobno, jeżeli właśnie ona jest przedmiotem pytania. Wydruk sumy kontrolnej utrzymuje zależność od wyniku, lecz sama obserwowalność nie zabrania kompilatorowi zastosowania szybszego równoważnego algorytmu. Celem jest pomiar wykonywanego programu, dlatego analiza asemblera może być częścią weryfikacji hipotezy.

## Pogłębienie mechanizmu

Wersja bazowa ma dwa zastosowania. Poprzednia implementacja pokazuje praktyczny zysk. Pusty lub uproszczony przebieg szkieletu pomiarowego pomaga ocenić narzut pętli, zegara i infrastruktury. Nie odejmujemy go automatycznie od każdego wyniku: składniki kosztu nie muszą dodawać się niezależnie, a odejmowanie dwóch bliskich zaszumionych liczb może pogorszyć wynik. Jeżeli narzut dominuje, lepiej zwiększyć partię lub zmienić metodę.

Zapisujemy wiele próbek, a nie pojedynczy najlepszy czas. Minimum przybliża wykonanie najmniej zakłócone, mediana opisuje typowy wynik, a rozrzut pokazuje stabilność eksperymentu. Żadna z tych liczb sama nie jest uniwersalnym estymatorem. Raport powinien zachować próbki i liczbę powtórzeń. Przy małej różnicy między wersjami trzeba sprawdzić, czy jest większa niż zwykła zmienność; dwie cyfry po przecinku nie zwiększają wiarygodności danych.

Na wynik wpływają częstotliwość procesora, temperatura, migracja między rdzeniami, inne procesy, stan alokatora, cache i przewidywanie skoków. Mały rozrzut nie wyklucza błędu systematycznego. Dokumentacja [LLVM Benchmarking tips](https://llvm.org/docs/Benchmarking.html) podkreśla potrzebę powtórzeń i kontroli zakłóceń. W praktyce zapisujemy warunki oraz przeplatamy uruchomienia wersji, aby powolne nagrzewanie komputera nie faworyzowało stale pierwszej lub ostatniej implementacji.

Rozgrzewka ma sens, jeśli produkcyjne użycie także pracuje w stanie ustalonym. Nie wolno nią usuwać kosztu, który użytkownik faktycznie ponosi przy zimnym starcie. Osobno mierzymy pierwszy odczyt pliku, kolejne odczyty z cache oraz pracę na danych większych od dostępnej pamięci podręcznej. Jedna nazwa „odczyt” kryje wtedy kilka różnych eksperymentów.

Dla usług przepustowość i opóźnienie muszą być analizowane razem. Stała liczba klientów może zmniejszać tempo wysyłania żądań, gdy serwer zwalnia, ukrywając narastanie kolejki. Generator obciążenia powinien odpowiadać modelowi ruchu, który chcemy badać. Raport zapisuje rozmiar próby, czas trwania, liczbę równoczesnych operacji, błędy oraz percentyle opóźnienia. Średnia z udanych odpowiedzi pomijająca timeouty może wyglądać dobrze właśnie wtedy, gdy usługa odrzuca najtrudniejsze żądania.

Dane eksperymentu powinny wystarczać do jego odtworzenia: identyfikator kodu, dokładna komenda budowania, wersja kompilatora i biblioteki standardowej, wariant konfiguracji oraz generator danych. Zachowujemy również wersję bazową. Zmiana kompilatora albo zależności może przyspieszyć obie implementacje inaczej, dlatego porównanie wyniku dzisiejszego kandydata z liczbą zapisaną miesiąc wcześniej jest słabsze niż ponowne uruchomienie obu wersji w tych samych warunkach.

## Drugi przykład

Porównanie wyszukiwania liniowego z binarnym wymaga tej samej semantyki: odpowiedzi, czy element istnieje. Dane są posortowane, a zapytania obejmują trafienia oraz braki. Pierwszy przebieg mierzy wersję bazową, drugi alternatywę; program nie wystarcza do rozstrzygnięcia statystycznego, dlatego powtarzamy go także z odwróconą kolejnością pomiarów.

~~~cpp
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <span>
#include <stdexcept>
#include <vector>

bool linear(std::span<const int> data, int key) {
    return std::ranges::find(data, key) != data.end();
}

bool binary(std::span<const int> data, int key) {
    return std::ranges::binary_search(data, key);
}

struct Result { double milliseconds; std::uint64_t hits; };

Result measure(bool (*lookup)(std::span<const int>, int),
               std::span<const int> data, std::span<const int> queries) {
    std::uint64_t hits{};
    const auto begin = std::chrono::steady_clock::now();
    for (int key : queries) hits += lookup(data, key);
    const auto end = std::chrono::steady_clock::now();
    return {std::chrono::duration<double, std::milli>(end - begin).count(),
            hits};
}

int main(int argc, char**) {
    std::vector<int> data(4096);
    std::iota(data.begin(), data.end(), 0);
    std::vector<int> queries(20000);
    std::uint64_t state = static_cast<std::uint64_t>(argc);
    for (int& key : queries) {
        state = state * 6364136223846793005ULL + 1;
        key = static_cast<int>((state >> 32) % 8192);
    }
    const auto baseline = measure(linear, data, queries);
    const auto candidate = measure(binary, data, queries);
    if (baseline.hits != candidate.hits) {
        throw std::runtime_error("rozne wyniki wyszukiwania");
    }
    std::cout << "linear_ms=" << baseline.milliseconds
              << " binary_ms=" << candidate.milliseconds
              << " hits=" << baseline.hits << '\n';
}
~~~

Koszt sortowania nie występuje w pomiarze, ponieważ kontrakt zakłada dane już posortowane. Jeżeli aplikacja otrzymuje losową tablicę i wykonuje jedno zapytanie, dodanie sortowania może odwrócić decyzję. Dla małej liczby elementów liniowy przebieg bywa konkurencyjny dzięki lokalności. Te zależności trzeba zmierzyć, a nie wyprowadzać bezpośrednio z samych klas złożoności.

Nie ustawiamy automatycznego progu regresji na podstawie jednego pomiaru lokalnego. Najpierw badamy zwykły rozrzut środowiska CI i wybieramy stabilne scenariusze. Przekroczenie progu powinno zachować próbki oraz konfigurację do analizy, zamiast jedynie wyświetlić czerwony status. Przy dużej zmienności można wydzielić dedykowaną maszynę pomiarową lub potraktować wynik jako sygnał do ponownego eksperymentu. Wspólny serwer budowania mierzy często także obciążenie pozostałych zadań, a nie wyłącznie koszt zmienionego kodu.

## Porównanie i decyzje

Mikrobenchmark pozwala odizolować mechanizm i szybko odrzucić hipotezę. Benchmark całej aplikacji pokazuje wpływ na rzeczywistą ścieżkę, uwzględniając inne koszty. Profilowanie pomaga wybrać fragment warty poprawy. Łączymy te narzędzia: zmniejszenie kosztu funkcji o połowę nie daje podobnego przyspieszenia programu, jeśli funkcja stanowi niewielką część całego wykonania. Nie przenosimy też pojedynczego wyniku w nanosekundach na inny procesor i kompilator.

**Zadanie 1.** Wersje różnią się o 2%, a próbki pojedynczej wersji mają rozrzut 10%. Jaką decyzję można podjąć?

<details><summary>Rozwiązanie</summary>

Obecny eksperyment nie daje stabilnego sygnału do wyboru. Zbadaj zakłócenia, zwiększ czas partii i liczbę powtórzeń, przeplataj wersje oraz zachowaj surowe próbki. Nie publikuj 2% jako potwierdzonego przyspieszenia na podstawie pojedynczych pomiarów.

</details>

**Zadanie 2.** Nowy kontener przyspiesza wyszukiwanie, lecz wymaga drogiego przygotowania. Jak wyznaczyć opłacalność?

<details><summary>Rozwiązanie</summary>

Zmierz przygotowanie i koszt zapytania dla reprezentatywnych danych. Porównaj koszt całkowity przy różnych liczbach zapytań, uwzględniając aktualizacje oraz pamięć. Punkt opłacalności zależy od częstotliwości użycia i nie wynika z samego benchmarku funkcji wyszukującej.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Profilowanie CPU](02_profilowanie_cpu.md)
- [Cache, lokalność i layout danych](04_cache_lokalnosc_i_layout_danych.md)
