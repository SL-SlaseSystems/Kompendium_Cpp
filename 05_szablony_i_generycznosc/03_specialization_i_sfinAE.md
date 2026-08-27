[← Spis treści](../README.md)

# Specialization i SFINAE

Pełna specjalizacja zastępuje zachowanie szablonu dla konkretnego zestawu argumentów. Częściowa specjalizacja jest dostępna dla szablonów klas i zmiennych, nie dla funkcji; funkcje zwykle przeciąża się. Specjalizacje powinny pozostawać zgodne z ogólnym kontraktem, inaczej kod generyczny staje się nieprzewidywalny.

SFINAE oznacza *Substitution Failure Is Not An Error*. Jeśli podczas podstawiania argumentów do bezpośredniego kontekstu sygnatury powstanie niedozwolona konstrukcja, kandydat może zostać usunięty zamiast wywołać twardy błąd. Concepts są czytelniejszym narzędziem w nowym kodzie, lecz SFINAE pozostaje ważne dla starszych bibliotek i pewnych idiomów detekcji.

~~~cpp
#include <cassert>
#include <type_traits>

template<class T>
struct Category {
    static constexpr const char* name = "other";
};

template<class T>
struct Category<T*> {
    static constexpr const char* name = "pointer";
};

template<class T>
std::enable_if_t<std::is_integral_v<T>, T> twice(T value) {
    return value * 2;
}

int main() {
    static_assert(Category<int*>::name[0] == 'p');
    assert(twice(4) == 8);
}
~~~

`std::enable_if_t` może pojawiać się w typie zwracanym, parametrze szablonu albo sygnaturze. Niektóre rozmieszczenia powodują kolizje redeklaracji lub słabą diagnostykę. Detection idiom z `std::void_t` pozwala sprawdzać poprawność wyrażeń, ale requires-expression zwykle wyraża intencję prościej.

Nie wolno ogólnie specjalizować szablonów w namespace `std`. Standard dopuszcza tylko konkretne, jawnie wskazane wyjątki, np. `std::hash` dla pewnych typów użytkownika. Zamiast zgadywać, sprawdź wymagania danego customization point.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Specialization i SFINAE”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- SFINAE usuwa kandydata tylko wtedy, gdy błąd powstaje w bezpośrednim kontekście substytucji. Partial specialization dotyczy szablonów klas i zmiennych; funkcje zamiast tego wykorzystują przeciążanie.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Specialization i SFINAE” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Specialization i SFINAE
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Specialization i SFINAE”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Concepts i requires](04_concepts_i_requires.md)
- [Dependent names i two-phase lookup](../zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)
- [map, set i hash](../06_biblioteka_standardowa/03_map_set_unordered_i_hash.md)

