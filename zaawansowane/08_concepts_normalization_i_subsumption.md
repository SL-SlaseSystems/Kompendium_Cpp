[← Spis treści](../README.md)

# Concept normalization i subsumption

Constraints są normalizowane do atomic constraints połączonych logicznie. Subsumption określa, czy jeden zestaw wymagań jest co najmniej tak restrykcyjny jak drugi i wpływa na partial ordering przeciążeń. Kompilator nie wykonuje ogólnego dowodzenia logicznego; tożsamość atomic constraints zależy od ich pochodzenia po normalizacji.

~~~cpp
#include <cassert>
#include <concepts>

template<class T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<class T>
concept SignedNumeric = Numeric<T> && std::signed_integral<T>;

template<Numeric T>
constexpr int category(T) { return 1; }

template<SignedNumeric T>
constexpr int category(T) { return 2; }

int main() {
    static_assert(category(1) == 2);
    static_assert(category(1u) == 1);
    assert(category(1.0) == 1);
}
~~~

Nazwany concept `Numeric` jest ponownie użyty w `SignedNumeric`, więc kompilator może rozpoznać wspólne atomic constraint. Powtórzenie tekstowo podobnego wyrażenia w dwóch miejscach nie zawsze buduje tę samą tożsamość i może dać niejednoznaczność.

Kolejność `&&` i `||` ma znaczenie także dla podstawiania: constraints są sprawdzane w kolejności lewo–prawo z short-circuit. Najpierw umieszczaj wymaganie, które czyni późniejsze wyrażenie poprawnym. Nie używaj zwykłej funkcji bool zamiast concept, jeśli potrzebna jest normalizacja i subsumption.

Semantyczne wymagania standardowych concepts, np. equality preservation, mogą nie być sprawdzane. Typ może syntaktycznie spełniać concept i łamać jego semantykę, co narusza kontrakt algorytmu.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Concept normalization i subsumption”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Concept nazywa predykat nad argumentami szablonu, a requires-expression sprawdza poprawność wymaganych operacji bez ich wykonywania. Ograniczenie powinno opisywać semantyczny kontrakt algorytmu, nie przypadkowe szczegóły implementacji.
- Constraints są normalizowane do atomowych ograniczeń, a subsumption ustala, który przeciążony kandydat jest bardziej ograniczony. Logicznie równoważne wyrażenia zapisane niezależnie nie zawsze tworzą te same atomic constraints.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Concept normalization i subsumption” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Concept normalization i subsumption
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Concept normalization i subsumption”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Concepts i requires](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)
- [Dependent names i SFINAE](07_dependent_names_two_phase_lookup_i_sfinae.md)

