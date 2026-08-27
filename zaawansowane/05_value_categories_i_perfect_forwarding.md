[← Spis treści](../README.md)

# Value categories i perfect forwarding

Każde wyrażenie ma typ i kategorię wartości. Glvalue wskazuje tożsamość obiektu; prvalue inicjuje wartość; xvalue oznacza obiekt, z którego można odzyskać zasoby. Lvalue i xvalue są glvalues, a prvalue i xvalue są rvalues. Te kategorie sterują wiązaniem referencji i overload resolution.

~~~cpp
#include <cassert>
#include <string>
#include <utility>

void consume(const std::string&) { }
void consume(std::string&& text) { assert(text == "C++"); }

template<class T>
void forward_to_consume(T&& value) {
    consume(std::forward<T>(value));
}

int main() {
    std::string text = "C++";
    forward_to_consume(text);            // T = string&
    forward_to_consume(std::move(text)); // T = string
}
~~~

`T&&` jest forwarding reference tylko gdy `T` jest dedukowane w odpowiednim kontekście. Reference collapsing daje m.in. `T& && -> T&`, dzięki czemu `std::forward<T>` odtwarza kategorię argumentu. Nazwany parametr `value` sam jest lvalue, nawet jeśli jego typ to rvalue reference.

`std::move` jest bezwarunkowym rzutowaniem do xvalue. Nie używaj go na const obiekcie, oczekując wydajnego move — konstruktor przenoszący zwykle potrzebuje modyfikowalnego rvalue, więc może zostać wybrana kopia. Nie wykonuj `return std::move(local);` bez konkretnego powodu, bo może zablokować NRVO.

Perfect forwarding nie jest idealne we wszystkich przypadkach: initializer lists, overloaded function names, bit-fields i wartości `0` jako null mają szczególne problemy dedukcji. `std::forward_like` z C++23 pomaga propagować cv/ref na podstawie innego typu.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Value categories i perfect forwarding”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Lvalue oznacza wyrażenie z tożsamością, xvalue zasób możliwy do ponownego użycia, a prvalue inicjalizuje wynik. Forwarding reference wraz z `std::forward` zachowuje kategorię argumentu po dedukcji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Value categories i perfect forwarding” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Value categories i perfect forwarding
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Value categories i perfect forwarding”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Dedukcja auto i decltype](../05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)

