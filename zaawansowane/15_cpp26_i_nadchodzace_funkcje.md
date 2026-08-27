[← Spis treści](../README.md)

# C++26 i nadchodzące funkcje

**Status zweryfikowany 2026-08-12:** C++26 znajduje się w aktualnym working draft WG21 N5054, ale nie jest jeszcze opublikowaną normą ISO. Draft może otrzymywać poprawki redakcyjne i defect resolutions, a implementacje wspierają tylko wybrane części. Kod produkcyjny powinien używać feature-test macros i testów konfiguracji.

Do głównych mechanizmów obecnych w projekcie standardu należą statyczna refleksja oparta o `std::meta::info`, contracts, pack indexing i dalsze rozszerzenia constant evaluation. Draft rozróżnia także erroneous behavior w części sytuacji wcześniej opisywanych przez wartości indeterminate. Biblioteka rozwija execution, narzędzia współbieżne, kontenery oraz interfejsy numeryczne, w tym standardowe SIMD.

Poniższy zapis pokazuje jedynie ideę pack indexing i jest nietestowany przez bazowy Clang 17:

~~~cpp,notest
template<std::size_t I, class... Types>
using element_t = Types...[I]; // C++26 pack indexing

static_assert(std::same_as<element_t<1, int, double>, double>);
~~~

Reflection umożliwia reprezentowanie encji programu jako wartości compile-time, introspekcję i generowanie deklaracji przez splicing zgodnie z przyjętym modelem. Jest to duża zmiana metaprogramowania, ale składnia, ograniczenia i zakres powinny być czytane z opublikowanej wersji lub aktualnego draftu, nie ze starych prototypów.

Contracts w working draft opisują contract assertions i semantyki ewaluacji. Historia tej funkcji zawiera wcześniejsze projekty usunięte z C++20, dlatego nie mieszaj dawnych składni z aktualnym tekstem. Toolchain może nie implementować mechanizmu albo używać flag eksperymentalnych.

~~~cpp
#include <cassert>

int main() {
#if defined(__cpp_pack_indexing) && __cpp_pack_indexing >= 202311L
    constexpr bool has_pack_indexing = true;
#else
    constexpr bool has_pack_indexing = false;
#endif
    assert(!has_pack_indexing || has_pack_indexing);
}
~~~

## Strategia adopcji

Najpierw ustal realną macierz kompilator–biblioteka–platforma. Izoluj nową funkcję w małym adapterze, zapewnij fallback i buduj obie ścieżki w CI. Nie emuluj refleksji lub contracts rozbudowanym makrem, jeśli koszt utrzymania przewyższa korzyść. Po publikacji normy zaktualizuj numer dokumentu i usuń określenie „projekt”.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „C++26 i nadchodzące funkcje”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Funkcja planowana dla C++26 przechodzi od propozycji przez głosowanie do publikacji i implementacji. Materiał powinien oznaczać status, feature macro i ograniczenia konkretnego toolchainu zamiast przedstawiać projekt jako powszechny standard.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „C++26 i nadchodzące funkcje” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: C++26 i nadchodzące funkcje
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „C++26 i nadchodzące funkcje”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Standardy i implementacje](../01_wprowadzenie/02_standardy_i_implementacje.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [Compile time](09_constexpr_consteval_i_compile_time.md)

