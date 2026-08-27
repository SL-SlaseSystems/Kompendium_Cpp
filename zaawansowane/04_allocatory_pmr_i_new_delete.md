[← Spis treści](../README.md)

# Alokatory, PMR i new/delete

Wyrażenie `new T(args...)` łączy uzyskanie storage z konstrukcją obiektu. `delete` wywołuje destruktor i zwalnia storage. Funkcje `operator new/delete` zajmują się surową pamięcią i mogą być przeciążane globalnie lub dla klasy, lecz poprawne wsparcie rozmiaru, alignment, tablic oraz wyjątków jest złożone.

Allocator-aware containers oddzielają politykę pamięci od kontenera. Klasyczne allocators są częścią typu kontenera. Polymorphic memory resources z `<memory_resource>` przenoszą wybór strategii do runtime, a `std::pmr::vector<T>` używa `polymorphic_allocator`.

~~~cpp
#include <array>
#include <cassert>
#include <memory_resource>
#include <vector>

int main() {
    std::array<std::byte, 1024> buffer{};
    std::pmr::monotonic_buffer_resource arena{buffer.data(), buffer.size()};
    std::pmr::vector<int> values{&arena};

    values.assign({10, 20, 12});
    assert(values[0] + values[1] + values[2] == 42);
}
~~~

Monotonic resource przydziela szybko i zwalnia pamięć grupowo przy destrukcji zasobu; indywidualne deallocation jest zwykle no-op. Kontenery nadal wywołują destruktory elementów. Obiekt korzystający z resource nie może go przeżyć, a przenoszenie między kontenerami z różnymi resource ma szczegółowe reguły.

Pool resources pomagają dla wielu podobnych alokacji. `unsynchronized_pool_resource` nie jest bezpieczny do równoczesnego dostępu, a `synchronized_pool_resource` płaci za synchronizację. PMR nie usuwa kosztu konstrukcji ani automatycznie nie poprawia cache.

Placement new i `construct_at` wymagają ręcznego zarządzania lifetime. Implementując kontener, licz skonstruowane elementy, aby wyjątek posprzątał tylko te istniejące. Preferuj sprawdzone kontenery; własna arena ma sens dopiero po profilu i jasnym modelu zwalniania.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Alokatory, PMR i new/delete”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Allocator rozdziela politykę uzyskiwania storage od kontenera, a PMR przenosi wybór resource do runtime. Resource musi żyć dłużej niż wszystkie alokacje, które zostaną przez niego zwolnione.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Alokatory, PMR i new/delete” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Alokatory, PMR i new/delete
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Alokatory, PMR i new/delete”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Dynamiczna pamięć](../03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
- [Lifetime i provenance](02_lifetime_aliasing_i_pointer_provenance.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

