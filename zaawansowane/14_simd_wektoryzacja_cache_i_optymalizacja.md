[← Spis treści](../README.md)

# SIMD, wektoryzacja, cache i optymalizacja

SIMD wykonuje tę samą operację na wielu lanes. Kompilator może autowektoryzować prostą pętlę, jeśli udowodni niezależność iteracji, alignment i opłacalność. Intrinsics są zależne od ISA, a biblioteczny `std::simd` należy oceniać zgodnie ze statusem wybranego standardu i implementacji.

~~~cpp
#include <cassert>
#include <cstddef>
#include <span>

void add(std::span<const float> left,
         std::span<const float> right,
         std::span<float> output) {
    assert(left.size() == right.size() && right.size() == output.size());
    for (std::size_t i = 0; i < output.size(); ++i) {
        output[i] = left[i] + right[i];
    }
}

int main() {
    const float left[]{1.0F, 2.0F};
    const float right[]{3.0F, 4.0F};
    float output[2]{};
    add(left, right, output);
    assert(output[0] == 4.0F && output[1] == 6.0F);
}
~~~

Pętla jest kandydatem do wektoryzacji, ale nakładające się zakresy mogą ograniczyć optymalizację. Standardowe C++ nie ma ogólnego `restrict`; kompilator może wykonać runtime alias checks lub nie wektoryzować. Raporty `-Rpass=loop-vectorize` w Clang i odpowiedniki GCC/MSVC pomagają zobaczyć decyzję, ale są narzędziami implementacji.

Lokalność danych często daje większy efekt niż ręczne SIMD. Structure of Arrays ułatwia przetwarzanie jednego pola wielu elementów, Array of Structures upraszcza logikę obiektu. Wybór zależy od wzorca dostępu. False sharing występuje, gdy niezależne atomiki w tej samej linii cache są modyfikowane przez różne rdzenie; `std::hardware_destructive_interference_size` jest wskazówką, nie pełnym modelem hardware.

Fast-math może złamać oczekiwania IEEE, obsługę NaN, signed zero i wyjątki floating point. Nie włączaj go globalnie bez kontraktu numerycznego. Testuj różne ISA i zachowaj poprawny scalar fallback.

## Jak to działa krok po kroku

Pętla `add` odczytuje po jednym elemencie obu wejść i zapisuje sumę. Kompilator może pogrupować iteracje, jeżeli zachowa wynik wymagany przez program. Musi uwzględnić nakładanie zakresów: gdy `output` zaczyna się wewnątrz `left`, wcześniejszy zapis może zmienić dane odczytywane przez późniejszą iterację. Utworzenie `span` nie obiecuje braku aliasowania ani poprawności dowolnego przesunięcia.

Implementacja może wygenerować test rozłączności przed pętlą, szybką ścieżkę wektorową i wolniejszą ścieżkę skalarną. Długość niepodzielna przez szerokość wektora wymaga obsługi końcówki przez maskowanie lub dodatkową pętlę. Dla dwóch elementów koszt przygotowania SIMD może przekraczać oszczędność, dlatego brak wektoryzacji tak małego przykładu nie świadczy o niezdolności kompilatora do rozpoznania wzorca.

## Pogłębienie mechanizmu

Zależność między iteracjami jest często ważniejsza niż wyrównanie. Pętla `a[i] = a[i - 1] + x` przenosi informację pomiędzy kolejnymi krokami. Pętla niezależnych dodawań nie ma takiej zależności, o ile zakresy nie nakładają się w problematyczny sposób. `const` na wejściowym wskaźniku zabrania zapisu przez ten wskaźnik, ale nie wyklucza zapisu do tej samej pamięci inną drogą.

Wydajność ogranicza czasami przepustowość pamięci. Dodanie dwóch tablic wymaga odczytu wejść i zapisu wyniku, a wykonuje niewiele arytmetyki. Szersze rejestry mogą wtedy dawać niewielką poprawę, bo rdzeń już czeka na dane. Przy sumowaniu tylko jednego pola milionów obiektów SoA zmniejsza ilość niepotrzebnie przesyłanych danych. Przy przetwarzaniu wszystkich pól pojedynczego obiektu AoS może zachować lepszą lokalność i prostszy kod.

Redukcja zmiennoprzecinkowa jest trudniejsza niż niezależne dodawanie. Zmiana nawiasowania może zmienić zaokrąglenia, więc drzewo równoległych sum nie zawsze jest równoważne pętli sekwencyjnej. Fast-math zezwala na określone uproszczenia implementacji kosztem kontraktu numerycznego, w tym szczególnego traktowania NaN lub nieskończoności. Test wyniku powinien wynikać z oczekiwanej tolerancji i modelu danych, a nie zakładać bezwarunkową identyczność bitów.

False sharing powstaje przy współbieżnych zapisach do różnych obiektów współdzielących linię cache. Nie jest data race, jeśli wątki poprawnie używają odrębnych obiektów, lecz może powodować kosztowną wymianę własności linii. Padding może pomóc, ale zwiększa working set. `hardware_destructive_interference_size` jest wartością zależną od implementacji; wstawienie jej w eksportowany typ wymaga uwagi na ABI i identyczność konfiguracji jednostek translacji.

Runtime dispatch musi sprawdzić nie tylko obecność instrukcji w CPU, ale również gotowość systemu operacyjnego do zachowywania odpowiedniego stanu rejestrów, gdy wymaga tego architektura. Rozszerzenia `target`, `target_clones`, intrinsics i flagi typu `-march` są narzędziami kompilatora. Kod skompilowany globalnie dla nowszej ISA może zawierać niedozwolone instrukcje nawet poza ręcznie oznaczoną szybką funkcją.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>

struct Particles {
    std::array<float, 4> x;
    std::array<float, 4> vx;
};
void advance(Particles& p, float dt) {
    for (std::size_t i = 0; i < p.x.size(); ++i)
        p.x[i] += p.vx[i] * dt;
}
int main() {
    Particles p{{0, 1, 2, 3}, {2, 2, 2, 2}};
    advance(p, 0.5f);
    assert(p.x[0] == 1 && p.x[3] == 4);
}
~~~

Osobne tablice pozycji i prędkości zapewniają ciągły dostęp do każdego pola. Każda iteracja zapisuje inny element i czyta odpowiadającą prędkość. Jest to układ sprzyjający wektoryzacji, ale standard nie obiecuje instrukcji SIMD. Liczby dobrano tak, aby proste asercje były dokładne w typowych reprezentacjach binarnych; rozbudowana symulacja potrzebuje jawnego modelu tolerancji błędu.

## Porównanie i decyzje

Najpierw mierz cały etap obliczeń na reprezentatywnym rozmiarze, a potem używaj raportu optymalizacji do wyjaśnienia wyniku. Benchmark powinien konsumować wynik, uwzględniać rozgrzanie cache i rozdzielać koszt alokacji od pętli. Ręczne intrinsics mają sens, gdy pomiar i analiza kodu maszynowego wykazują istotną lukę, a projekt potrafi utrzymać warianty ISA i skalarny fallback.

**Ćwiczenie.** Czy `alignas(64)` gwarantuje szybszą pętlę? **Odpowiedź:** nie, nie usuwa zależności, nie zwiększa przepustowości pamięci i nie ustala rozmiaru danych. Czy brak data race wyklucza false sharing? Nie; problem dotyczy mechanizmu cache, a nie naruszenia modelu pamięci. Czy `std::simd` jest częścią C++23? Nie; standardowy interfejs należy oznaczać jako **C++26**, a wcześniejsze biblioteki SIMD i TS rozpatrywać osobno.

Źródła implementacyjne: [LLVM Loop Vectorizer](https://llvm.org/docs/Vectorizers.html) i [Clang: diagnostyka optymalizacji](https://clang.llvm.org/docs/UsersManual.html#options-to-emit-optimization-reports).

### Ocena wyniku pomiaru

Przed porównaniem wersji skalarnej i SIMD ustal, czy mierzysz opóźnienie pojedynczego zadania, przepustowość wielu zadań czy czas całego procesu. Inicjalizacja dispatchu może mieć znaczenie tylko przy pierwszym wywołaniu. Przetwarzanie bufora mieszczącego się w cache odpowiada innemu ograniczeniu niż strumień znacznie większy od pamięci podręcznej. Jeden rozmiar danych nie charakteryzuje całego algorytmu.

Kontrola poprawności powinna objąć pusty zakres, krótkie zakresy i długości wokół wielokrotności liczby lanes. To właśnie obsługa końcówki często powoduje wyjścia poza przydział. Nie wolno odczytywać poza buforem tylko dlatego, że nadmiarowe wyniki zostaną później zamaskowane; legalność zależy od semantyki konkretnej instrukcji i kontraktu pamięci. Skalarny fallback jest też użytecznym punktem odniesienia dla walidacji.

Jeżeli różnica czasu jest mała, zbierz serię pomiarów i obserwuj rozrzut. Migracja pomiędzy rdzeniami, częstotliwość procesora i konkurencyjne obciążenie mogą zasłonić zysk. Raport kompilatora odpowiada na pytanie, jak przekształcono pętlę; profiler odpowiada, gdzie zużywany jest czas. Dopiero połączenie tych informacji uzasadnia utrzymywanie bardziej złożonej implementacji.

## Powiązane tematy

- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
- [Benchmarki](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [Layout i alignment](03_layout_alignment_padding_i_triviality.md)

