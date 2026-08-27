[← Spis treści](../README.md)

# Concepts i requires

Concept jest nazwanym predykatem compile-time opisującym wymagania wobec argumentów szablonu. Constrained templates uczestniczą w overload resolution tylko wtedy, gdy constraints są spełnione. Dzięki temu interfejs wyraża potrzebne zachowanie, a błędy pojawiają się bliżej miejsca wywołania.

~~~cpp
#include <cassert>
#include <concepts>
#include <string>

template<class T>
concept Addable = requires(T left, T right) {
    { left + right } -> std::same_as<T>;
};

template<Addable T>
T add(const T& left, const T& right) {
    return left + right;
}

int main() {
    assert(add(2, 3) == 5);
    assert(add(std::string{"C"}, std::string{"++"}) == "C++");
}
~~~

Requires-expression może zawierać simple requirements sprawdzające poprawność wyrażenia, type requirements, compound requirements z typem wyniku i `noexcept` oraz nested requirements. Nie wykonuje wyrażeń; bada, czy byłyby poprawne po podstawieniu.

Concept nie powinien jedynie sprawdzać składni. Semantyczne wymagania, takie jak relacja równoważności lub brak modyfikacji argumentu, nie zawsze są weryfikowalne przez kompilator, lecz nadal należą do kontraktu. Standardowe concepts, np. `std::integral`, `std::regular`, `std::ranges::range` i `std::invocable`, tworzą wspólny język takich wymagań.

Constraints mogą być zapisane po nazwie template, przy parametrze, jako trailing `requires` lub requires-clause. Wybierz postać, która najlepiej pokazuje interfejs. Złożone reguły normalizacji i subsumption wpływają na wybór „bardziej ograniczonego” przeciążenia; tekstowo podobne predykaty nie muszą być traktowane identycznie.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Concepts i requires”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Concept nazywa predykat nad argumentami szablonu, a requires-expression sprawdza poprawność wymaganych operacji bez ich wykonywania. Ograniczenie powinno opisywać semantyczny kontrakt algorytmu, nie przypadkowe szczegóły implementacji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Concepts i requires” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Concepts i requires
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Concepts i requires”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [SFINAE](03_specialization_i_sfinAE.md)
- [Concept normalization i subsumption](../zaawansowane/08_concepts_normalization_i_subsumption.md)
- [Ranges](../06_biblioteka_standardowa/06_ranges_i_views.md)

