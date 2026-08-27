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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „SIMD, wektoryzacja, cache i optymalizacja”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Lokalność danych często wpływa na wydajność bardziej niż liczba instrukcji źródłowych. Zero-overhead abstractions należy oceniać na assembly i profilu; szablon może usunąć dispatch, ale zwiększyć kod i presję instruction cache.
- Autowektoryzacja wymaga niezależności iteracji, znanego aliasingu i opłacalnego układu danych. SIMD przyspiesza obliczenia tylko wtedy, gdy koszt ładowania, wyrównania, remainder loop i transferu danych nie dominuje.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „SIMD, wektoryzacja, cache i optymalizacja” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: SIMD, wektoryzacja, cache i optymalizacja
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „SIMD, wektoryzacja, cache i optymalizacja”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
- [Benchmarki](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [Layout i alignment](03_layout_alignment_padding_i_triviality.md)

