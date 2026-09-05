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

Dla `Category<int*>` najpierw identyfikowany jest szablon główny, a następnie sprawdzane pasujące specjalizacje częściowe. Wzorzec `Category<T*>` pasuje z `T = int` i jest bardziej szczegółowy niż ogólna wersja, więc dostarcza definicję klasy. Specjalizacja nie dziedziczy automatycznie brakujących pól i metod szablonu głównego; stanowi własną definicję wymagającą zachowania oczekiwanego interfejsu.

Przy `twice(4)` dedukcja daje `T = int`. `enable_if_t<true, int>` oznacza `int`, więc deklaracja funkcji pozostaje poprawna. Dla argumentu `double` warunek jest fałszywy i alias nie dostarcza typu. Jeżeli błąd powstaje we właściwym bezpośrednim kontekście podstawienia, kandydat znika ze zbioru. Gdy nie zostaje inne wykonalne przeciążenie, całe wywołanie nadal jest błędne; SFINAE nie gwarantuje, że zawsze istnieje plan awaryjny.

Błąd z wnętrza ciała wybranej funkcji zwykle jest już zwykłym błędem instancjacji. Szablon `void f(T value) { value.missing(); }` nie zostaje bezpiecznie pominięty tylko dlatego, że dla `int` nie istnieje `missing`. Żądane wyrażenie trzeba przenieść do sprawdzanego interfejsu, na przykład requires-expression, jeśli ma decydować o dostępności przeciążenia.

## Pogłębienie mechanizmu

Bezpośredni kontekst jest ograniczony. Substytucja może uruchomić instancjację innego szablonu klasy, a błąd wewnątrz tej klasy nie musi należeć do chronionego kontekstu. Zagnieżdżanie pomocniczych traits nie zmienia automatycznie każdego twardego błędu w łagodne odrzucenie. Kolejność podstawiania również może mieć znaczenie, dlatego układ deklaracji powinien być prosty i spójny.

`std::void_t<...>` zamienia poprawne argumenty typowe na `void`. Gdy któregoś argumentu nie da się utworzyć, odpowiednia specjalizacja częściowa traits może przestać pasować. Wersja główna dostarcza wtedy wynik fałszywy. `std::declval<T>()` pozwala formułować wyrażenia bez konstruowania `T`, lecz wolno go używać w kontekstach nieewaluowanych, takich jak `decltype`, nie jako rzeczywistej fabryki obiektu.

Pełna specjalizacja funkcji nie uczestniczy w rozstrzyganiu tak jak zwykłe niezależne przeciążenie. Najpierw wybierany jest właściwy szablon funkcji, a potem może zostać użyta jego specjalizacja. Dodanie przeciążenia o innym wzorcu może zmienić, który szablon w ogóle zostanie wybrany. Dla funkcji zazwyczaj czytelniej jest przeciążyć interfejs lub użyć constraints zamiast budować rozbudowaną sieć pełnych specjalizacji.

Specjalizacja jawna powinna być zadeklarowana, zanim użycie spowoduje odpowiednią niejawną instancjację w każdej jednostce translacji, w której jest potrzebna. Umieszczenie jej przypadkiem za pierwszym wywołaniem nie jest sposobem na późniejsze podmienienie już wybranego zachowania. Rozmieszczenie specjalizacji w nagłówkach należy analizować również pod kątem ODR.

Nie należy rozróżniać dwóch szablonów funkcji wyłącznie domyślnymi argumentami parametru szablonu. Dwie wersje `template<class T, class = enable_if_t<...>>` mogą być redeklaracjami tego samego szablonu, mimo innego warunku. Constraints od C++20 lepiej wyrażają takie alternatywy i zwykle dają krótszą diagnostykę.

## Drugi przykład

Trait wykrywa możliwość wywołania `size()` na stałym obiekcie. Pytanie dotyczy konkretnego wyrażenia i kwalifikacji, a nie tylko istnienia nazwy o takim brzmieniu.

~~~cpp
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

template<class T, class = void>
struct HasConstSize : std::false_type {};

template<class T>
struct HasConstSize<T, std::void_t<decltype(std::declval<const T&>().size())>>
    : std::true_type {};

struct MutableOnly {
    int size() { return 1; }
};

int main() {
    static_assert(HasConstSize<std::string>::value);
    static_assert(HasConstSize<std::vector<int>>::value);
    static_assert(!HasConstSize<int>::value);
    static_assert(!HasConstSize<MutableOnly>::value);
}
~~~

`MutableOnly` ma metodę `size`, ale nie można jej wywołać na `const T&`, dlatego trait zwraca fałsz. Gdyby algorytm potrzebował również konkretnego typu wyniku lub niezgłaszania wyjątków, te własności należałoby sprawdzić osobno. Sama nazwa trait nie ustanawia dodatkowych wymagań.

## Porównanie i decyzje

W nowym kodzie C++23 używaj concepts do opisywania dostępności operacji, a `if constexpr` do wyboru implementacji wewnątrz poprawnego kontraktu. SFINAE jest potrzebne przy czytaniu starszych bibliotek i rozwijaniu kodu obsługującego wcześniejsze standardy. Specjalizacja częściowa pozostaje naturalna dla transformacji typów i różnych reprezentacji klas, także w nowoczesnym C++.

**Ćwiczenie.** Czy brak metody w ciele funkcji z dedukowanym zwracanym `auto` zawsze zostanie potraktowany jako SFINAE?

**Odpowiedź.** Nie. Ustalenie wyniku może wymagać instancjacji ciała, a jej błąd jest zwykle twardym błędem. Jeśli dostępność ma zależeć od wyrażenia, umieść warunek w requires lub odpowiednim bezpośrednim kontekście deklaracji, zamiast liczyć na ochronę całej implementacji.

Źródła: [reguły substytucji](https://timsong-cpp.github.io/cppwp/n4950/temp.deduct.general), [specjalizacje częściowe](https://timsong-cpp.github.io/cppwp/n4950/temp.spec.partial), [specjalizacje jawne](https://timsong-cpp.github.io/cppwp/n4950/temp.expl.spec).

## Powiązane tematy

- [Concepts i requires](04_concepts_i_requires.md)
- [Dependent names i two-phase lookup](../zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)
- [map, set i hash](../06_biblioteka_standardowa/03_map_set_unordered_i_hash.md)

