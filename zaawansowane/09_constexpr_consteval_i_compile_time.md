[← Spis treści](../README.md)

# constexpr, consteval i compile time

Constant evaluation wykonuje podzbiór semantyki C++ podczas kompilacji. Nie jest oddzielnym językiem: coraz więcej zwykłych konstrukcji działa w `constexpr`. Nadal istnieją zakazane operacje i ograniczenia zależne od wersji, np. efekty uboczne poza ewaluacją, niektóre formy dynamicznej pamięci i dostęp do obiektów o niewłaściwym lifetime.

~~~cpp
#include <array>
#include <cassert>
#include <cstdint>
#include <string_view>

consteval std::uint32_t hash_literal(std::string_view text) {
    std::uint32_t hash = 2166136261u;
    for (unsigned char byte : text) {
        hash = (hash ^ byte) * 16777619u;
    }
    return hash;
}

int main() {
    constexpr auto id = hash_literal("status");
    static_assert(id != 0);
    assert(id == hash_literal("status"));
}
~~~

Unsigned overflow w tym hash jest zdefiniowany modulo. `consteval` gwarantuje compile-time dla potencjalnie ewaluowanych wywołań. Jeśli chcemy jedną funkcję dostępną także runtime, wybieramy `constexpr`.

`std::is_constant_evaluated()` pozwala wykryć, czy bieżąca ewaluacja jest stała, a `if consteval` z C++23 daje bezpieczniejszą składnię rozdzielenia gałęzi. Nie używaj tego do tworzenia różnych wyników semantycznych bez wyraźnego kontraktu; compile-time i runtime powinny zwykle zgadzać się.

Dynamiczna alokacja podczas constant evaluation może być dozwolona w określonych przypadkach, ale pamięć musi zostać zwolniona w ramach ewaluacji i nie może „wyciec” do runtime. Biblioteka standardowa stopniowo rozszerza constexpr support.

Koszt przenosi się z runtime do kompilatora. Monitoruj czas, pamięć, cache builda i jakość diagnostyki. Precomputed table może zwiększyć binarium i pogorszyć cache bardziej niż krótki runtime calculation.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „constexpr, consteval i compile time”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `consteval` wymaga constant evaluation każdego potencjalnie ocenianego wywołania, natomiast funkcja `constexpr` może działać zarówno podczas kompilacji, jak i runtime. Constant evaluation nadal przestrzega reguł języka i diagnozuje niedozwolone operacje.
- Koszt constant evaluation i instancjacji obciąża build, choć znika z runtime. Limity głębokości, pamięci i diagnostyki kompilatora są praktyczną częścią projektu metaprogramu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „constexpr, consteval i compile time” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: constexpr, consteval i compile time
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „constexpr, consteval i compile time”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [constexpr i metaprogramowanie](../05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [Wydajność](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
