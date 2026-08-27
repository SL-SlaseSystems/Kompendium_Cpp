[← Spis treści](../README.md)

# Layout, alignment, padding i triviality

`sizeof(T)` obejmuje storage obiektu wraz z paddingiem, a `alignof(T)` wymagane wyrównanie. Kolejność i rozmiar paddingu zależą od implementacji z wyjątkiem konkretnych gwarancji standardu. Nie serializuj obiektu przez zapis `sizeof(T)` bajtów: padding może mieć nieokreśloną zawartość, a reprezentacja zależy od ABI i endianess.

~~~cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <type_traits>

struct PacketHeader {
    std::uint32_t length;
    std::uint16_t kind;
    std::uint16_t flags;
};

int main() {
    static_assert(std::is_standard_layout_v<PacketHeader>);
    static_assert(std::is_trivially_copyable_v<PacketHeader>);
    assert(alignof(PacketHeader) >= alignof(std::uint32_t));
    assert(offsetof(PacketHeader, length) == 0);
}
~~~

Standard-layout daje ograniczone gwarancje interoperacyjności i layoutu, a trivially copyable pozwala kopiować reprezentację do tablicy `char`, `unsigned char` lub `std::byte` i z powrotem zgodnie z regułami. Nadal nie gwarantuje przenośnego formatu pliku.

`alignas` może zwiększyć wymagane wyrównanie obiektu. Over-aligned typy wymagają dopasowanej alokacji; współczesne `new` obsługuje aligned allocation, ale własne alokatory muszą propagować wymagania. `std::assume_aligned` jest obietnicą dla optymalizatora, nie runtime checkiem.

`[[no_unique_address]]` pozwala, by potencjalnie pusty element współdzielił adres z innymi danymi, lecz dokładny layout pozostaje zależny od implementacji. Empty Base Optimization także jest używany do kompresji policy objects.

`std::bit_cast` kopiuje reprezentację między trivially copyable typami o tym samym rozmiarze i jest bezpieczniejszy od aliasowania przez `reinterpret_cast`. Nie gwarantuje jednak, że każdy wzorzec bitów reprezentuje prawidłową wartość typu docelowego ani że wynik jest przenośnym formatem danych.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Layout, alignment, padding i triviality”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Alignment może wprowadzać padding między polami i na końcu obiektu, dlatego suma `sizeof` członów nie wyznacza layoutu klasy. Trivially copyable umożliwia określone kopiowanie reprezentacji bajtowej, ale nie dowolną serializację między ABI.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Layout, alignment, padding i triviality” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Layout, alignment, padding i triviality
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Layout, alignment, padding i triviality”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [FFI i interoperacyjność](13_odr_moduly_ffi_i_interoperacyjnosc.md)
- [SIMD i cache](14_simd_wektoryzacja_cache_i_optymalizacja.md)
