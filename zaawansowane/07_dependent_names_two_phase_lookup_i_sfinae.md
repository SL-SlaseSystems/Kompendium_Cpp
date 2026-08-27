[← Spis treści](../README.md)

# Dependent names, two-phase lookup i SFINAE

W definicji szablonu część nazw zależy od parametrów. Nazwy niezależne są wyszukiwane przy definicji, a zależne dodatkowo podczas instancjacji według reguł two-phase lookup. To zapobiega przypadkowemu uzależnieniu szablonu od deklaracji pojawiających się później.

`typename` informuje parser, że zależna kwalifikowana nazwa oznacza typ. Słowo `template` informuje, że zależna składowa jest szablonem. Brak tych disambiguators jest częstym źródłem diagnostyki.

~~~cpp
#include <cassert>
#include <vector>

template<class Container>
typename Container::value_type first_or_default(const Container& values) {
    using Value = typename Container::value_type;
    return values.empty() ? Value{} : values.front();
}

template<class T>
struct Wrapper {
    template<class U>
    static U convert(T value) { return static_cast<U>(value); }
};

template<class T>
double convert_to_double(T value) {
    return Wrapper<T>::template convert<double>(value);
}

int main() {
    assert(first_or_default(std::vector<int>{}) == 0);
    assert(convert_to_double(21) == 21.0);
}
~~~

ADL przy instancjacji może znaleźć funkcje w przestrzeniach powiązanych z zależnymi argumentami, ale zwykły lookup nie zbiera dowolnych późniejszych deklaracji. Różnice implementacji two-phase lookup były historycznym źródłem nieprzenośnego kodu, szczególnie w starszym MSVC.

SFINAE działa tylko dla niepoprawności w immediate context podstawienia. Błąd głęboko w instancjowanym ciele może być twardym błędem. Requires-expressions lepiej lokalizują badane wyrażenie i dają czytelniejszy kontrakt, choć zrozumienie dependent names nadal jest konieczne.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Dependent names, two-phase lookup i SFINAE”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- SFINAE usuwa kandydata tylko wtedy, gdy błąd powstaje w bezpośrednim kontekście substytucji. Partial specialization dotyczy szablonów klas i zmiennych; funkcje zamiast tego wykorzystują przeciążanie.
- Nazwa zależna może być rozstrzygnięta dopiero podczas instancjacji; `typename` i `template` pomagają parserowi określić jej rolę. Two-phase lookup zapobiega przypadkowemu przejęciu późniejszych deklaracji nieskojarzonych z argumentami.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Dependent names, two-phase lookup i SFINAE” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Dependent names, two-phase lookup i SFINAE
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Dependent names, two-phase lookup i SFINAE”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Specialization i SFINAE](../05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
- [Concepts](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)

