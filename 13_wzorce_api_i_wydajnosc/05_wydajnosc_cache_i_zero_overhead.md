[← Spis treści](../README.md)

# Wydajność, cache i zero-overhead

Zasada zero-overhead mówi, że nieużywane mechanizmy nie powinny kosztować, a użyte abstrakcje mają być konkurencyjne z ręczną implementacją. Nie oznacza, że każdy szablon, iterator lub lambda jest zawsze szybsza. Wydajność zależy od algorytmu, reprezentacji danych, pamięci, optymalizatora i sprzętu.

~~~cpp
#include <cassert>
#include <numeric>
#include <vector>

int sum(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

int main() {
    const std::vector values{10, 20, 12};
    assert(sum(values) == 42);
}
~~~

Iteratorowy algorytm może zostać zoptymalizowany do zwykłej pętli bez obiektu sterującego runtime. Największe zyski często wynikają jednak z wyboru złożoności i układu danych, nie mikrooptymalizacji składni. Ciągły vector zwykle wykorzystuje cache lepiej niż lista z osobnymi węzłami.

Koszty obejmują alokacje, cache misses, branch misprediction, synchronizację, kopiowanie, rozrost kodu po monomorfizacji i brak inline przez granice ABI. Small-buffer optimization jest detalem konkretnego typu/implementacji, jeśli standard go nie gwarantuje. Copy elision może być gwarantowana w wybranych kontekstach, ale `std::move` lokalnego wyniku może ją utrudnić.

Buduj release z odpowiednią optymalizacją, a przy whole-program scenariuszach rozważ LTO. Profile-guided optimization wykorzystuje reprezentatywne wykonania. Każda opcja zmienia czas budowania, debugowalność i czasem ABI; włączaj ją przez kontrolowane profile.

## Jak to działa krok po kroku

Zacznij od mierzalnego wymagania: przepustowości, mediany opóźnienia, wysokiego percentyla lub maksymalnego zużycia pamięci. Następnie ustal, która część rzeczywistego programu odpowiada za koszt. Profil może pokazać, że domniemana „wolna pętla” zajmuje niewielki procent czasu, a większość przypada na alokacje lub oczekiwanie na I/O.

Zaproponuj jedną zmianę wynikającą z hipotezy, na przykład ograniczenie alokacji przez `reserve`, zmianę algorytmu albo układu danych. Porównaj wersje na tych samych danych i konfiguracji. Sprawdź również wynik obliczeń oraz zużycie pamięci. Szybsza wersja nie jest ulepszeniem, jeżeli pomija część pracy albo zmienia wymaganą precyzję.

## Pogłębienie mechanizmu

Procesor pobiera dane w jednostkach związanych z hierarchią pamięci. Dostęp sekwencyjny do zwartego bufora często pozwala efektywnie wykorzystać kolejne pobrane dane. Lista wskaźnikowa może wymagać odczytania węzła, aby poznać adres następnego, co ogranicza możliwość wcześniejszego pobierania. To uzasadnia hipotezę o lokalności, ale dokładne koszty zależą od sprzętu, danych i liczby elementów.

Układ array of structures przechowuje razem pola jednego obiektu, a structure of arrays grupuje to samo pole wielu obiektów. Pierwszy pasuje do pracy na całych rekordach, drugi może ograniczyć ruch pamięci podczas przetwarzania jednego pola. Zysk trzeba zestawić ze złożonością utrzymania spójności wielu tablic i kosztami innych operacji, takich jak wstawianie i usuwanie rekordów.

Pamięć podręczna danych to nie jedyny zasób. Rozbudowane szablony i agresywne inline mogą zwiększyć kod maszynowy i obciążyć cache instrukcji. Oddziel też przydzieloną pojemność od liczby elementów: `reserve` może wyeliminować realokacje podczas wzrostu, lecz zużywa pamięć i nie tworzy elementów. Nie wolno zapisywać przez indeks w zarezerwowanym, ale logicznie pustym wektorze.

## Drugi przykład

~~~cpp
#include <cassert>
#include <cstddef>
#include <vector>

int main() {
    constexpr std::size_t count = 100;
    std::vector<int> values;
    values.reserve(count);
    assert(values.empty());
    const auto capacity = values.capacity();
    values.push_back(0);
    const int* first = &values[0];
    for (std::size_t i = 1; i < count; ++i) {
        values.push_back(static_cast<int>(i));
    }
    assert(values.size() == count);
    assert(values.capacity() == capacity);
    assert(first == &values[0] && *first == 0);
}
~~~

Po `reserve` rozmiar nadal wynosi zero. Dopiero `push_back` tworzy pierwszy element, którego adres zapamiętujemy. Kolejne dodania mieszczą się w pojemności, więc nie powodują realokacji. Program dowodzi konkretnej własności kontenera; nie mierzy przyspieszenia i nie określa dokładnej liczby bajtów zajętych przez allocator.

## Porównanie i decyzje

Złożoność asymptotyczna przewiduje wzrost kosztu, ale dla małych danych stałe i lokalność mogą dominować. Posortowany wektor może konkurować z drzewem dla odczytów, a hash table potrzebuje dobrego hasha i odpowiedniego obciążenia. Porównuj reprezentacje według rzeczywistych proporcji wyszukiwania, wstawiania i iteracji, zamiast wybierać strukturę po jednej kolumnie Big-O.

Benchmark powinien uniemożliwiać usunięcie mierzonego wyniku przez optimizer, ale nie wprowadzać dowolnej pracy przez `volatile`, która zmieni badany problem. Użyj odpowiednich mechanizmów biblioteki benchmarkowej, odseparuj przygotowanie danych i uwzględnij rozgrzewkę. Wynik raportuj z jednostką, zmiennością, liczbą prób i konfiguracją; pojedynczy najniższy czas jest słabym dowodem.

## Ćwiczenie z odpowiedzią

Czy `reserve(size() + 1)` przed każdym `push_back` zawsze przyspiesza wzrost wektora? Nie: może wymusić częste realokacje i zniszczyć korzyść z jego zwykłej strategii wzrostu. Rezerwuj sensownie oszacowaną liczbę elementów. Następnie oceń, czy przyspieszenie funkcji zajmującej 1% czasu o połowę może podwoić szybkość programu: nie, pozostałe 99% nie zmienia kosztu.

Źródła: [C++23, vector capacity](https://timsong-cpp.github.io/cppwp/n4950/vector.capacity), [Clang — profile-guided optimization](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization).

## Powiązane tematy

- [Benchmarki i profilowanie](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [Kontenery sekwencyjne](../06_biblioteka_standardowa/02_vector_array_deque_list.md)
- [SIMD i optymalizacja](../zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

