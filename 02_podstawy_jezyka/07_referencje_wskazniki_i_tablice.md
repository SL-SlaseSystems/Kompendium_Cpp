[← Spis treści](../README.md)

# Referencje, wskaźniki i tablice

Referencja `T&` jest aliasem istniejącego obiektu i musi zostać zainicjalizowana. Wskaźnik `T*` przechowuje adres, może być równy `nullptr` i może zmienić cel. Ani referencja, ani surowy wskaźnik nie oznaczają automatycznie własności. Kontrakt API powinien wyjaśniać nullowalność oraz wymagany czas życia.

~~~cpp
#include <array>
#include <cassert>
#include <span>

int sum(std::span<const int> values) {
    int total = 0;
    for (int value : values) {
        total += value;
    }
    return total;
}

int main() {
    std::array data{1, 2, 3};
    int& first = data[0];
    int* pointer = &data[1];
    first = 4;
    *pointer = 5;

    assert(sum(data) == 12);
}
~~~

Wbudowana tablica `T[N]` ma stały rozmiar będący częścią typu. W większości wyrażeń ulega konwersji do wskaźnika na pierwszy element, tracąc informację o długości. `std::array<T, N>` zachowuje semantykę wartości i integruje się z biblioteką, a `std::span<T>` jest niewłaścicielskim widokiem na ciągły zakres.

Arytmetyka wskaźników jest dozwolona tylko w obrębie jednej tablicy oraz na pozycję one-past-the-end, której nie wolno dereferencjonować. Odejmowanie niepowiązanych wskaźników, dereferencja `nullptr`, użycie adresu po końcu lifetime obiektu i naruszenie alignment mogą być undefined behavior.

`const int*` wskazuje na niemodyfikowalny `int`, `int* const` jest stałym wskaźnikiem do modyfikowalnego `int`, a `const int* const` łączy oba ograniczenia. Czytaj deklarację od nazwy na zewnątrz lub w złożonych interfejsach używaj aliasów typów.

## Jak to działa krok po kroku

W pierwszym programie `data` posiada trzy obiekty `int`. Referencja `first` wiąże się z pierwszym i nie może później zostać przestawiona na drugi. Przypisanie do `first` modyfikuje element. Wskaźnik `pointer` przechowuje adres drugiego elementu; przypisanie do `*pointer` modyfikuje wskazaną liczbę, natomiast przypisanie do samego `pointer` zmieniłoby cel. Wywołanie `sum` otrzymuje widok zawierający dostęp do całego zakresu i nie przejmuje własności.

Deklaracja `int& r = a; r = b;` nie przepina referencji. Kopiuje wartość `b` do `a`. Referencja nie jest też automatycznym zabezpieczeniem czasu życia: po zniszczeniu `a` pozostaje wisząca, mimo że jej składnia nie dopuszcza zwykłego `nullptr`. Wskaźniki i referencje wymagają prawdziwego, odpowiednio wyrównanego obiektu, do którego dostęp jest legalny.

Dla tablicy `int a[3]` wyrażenie `a` często konwertuje się do wskaźnika na pierwszy element. Są jednak wyjątki: `sizeof(a)` obejmuje całą tablicę, a `&a` ma typ wskaźnika do tablicy trzech liczb. W funkcji zadeklarowanej jako `f(int a[3])` parametr jest w rzeczywistości wskaźnikiem; rozmiar w nawiasach nie pozostaje częścią jego typu. To różne mechanizmy: konwersja wyrażenia i dostosowanie deklaracji parametru.

## Pogłębienie mechanizmu

Wskaźnik one-past-the-end jest legalnym wartownikiem. Można go porównywać i odejmować w ramach tej samej tablicy, lecz nie można przez niego czytać ani pisać. `a + 3` jest poprawne dla tablicy trzech elementów, a próba utworzenia `a + 4` wykracza już poza dozwoloną arytmetykę. Nie wystarczy obiecać, że zbyt daleki adres nie zostanie później dereferencjonowany.

Różnica wskaźników ma typ `std::ptrdiff_t` i musi być reprezentowalna w tym typie. Arytmetyka wskaźnika uwzględnia rozmiar elementu: `p + 1` przesuwa do kolejnego `T`, a nie o jeden bajt. Dla wielowymiarowego `int a[2][3]` każdy wiersz jest osobną tablicą trzech elementów. Reguły nie dają ogólnego pozwolenia na przechodzenie jednym `int*` przez granice wszystkich wierszy tylko dlatego, że reprezentacja jest ciągła.

Dodawanie kwalifikacji na wielu poziomach wskaźników jest subtelne. `int*` można skonwertować do `const int*`, lecz `int**` nie konwertuje się po prostu do `const int**`. Taka konwersja pozwoliłaby podstawić adres stałej liczby do wskaźnika, który obiecuje modyfikowalny `int`, a potem próbować zmiany stałego obiektu. Ograniczenie wynika więc z ochrony typów, nie z różnicy rozmiaru reprezentacji.

`nullptr` ma własny typ `std::nullptr_t` i jest właściwym sposobem oznaczania braku celu. Literał zero może oznaczać zarówno liczbę, jak i stałą pustego wskaźnika w odpowiednim kontekście, co komplikuje przeciążenia. Samo porównanie z `nullptr` nie wykrywa wskaźnika wiszącego ani adresu niewłaściwego obiektu.

## Drugi przykład

Referencja do tablicy zachowuje jej rozmiar jako parametr szablonu. Druga część pokazuje różnicę między przypisaniem przez referencję i zmianą celu wskaźnika.

~~~cpp
#include <cassert>
#include <cstddef>
#include <type_traits>

template<class T, std::size_t N>
constexpr std::size_t count(T (&)[N]) noexcept { return N; }

int main() {
    int values[]{10, 20, 30};
    static_assert(count(values) == 3);
    static_assert(std::is_same_v<decltype(&values), int (*)[3]>);
    int* begin = values;
    int* end = values + count(values);
    assert(end - begin == 3);

    int& alias = values[0];
    alias = values[1];
    assert(values[0] == 20);
    int* selected = &values[0];
    selected = &values[2];
    *selected = 99;
    assert(values[2] == 99);
}
~~~

## Porównanie i decyzje

Stały rozmiar wbudowanej tablicy nie daje jej zwykłego operatora przypisania całej zawartości. Nie można wykonać `a = b` dla dwóch takich tablic. `std::array` zapewnia natomiast kopiowanie i przypisanie elementów, dzięki czemu można zwracać całą tablicę z funkcji jako wartość. To różnica interfejsu i semantyki typu, mimo że oba rozwiązania mogą przechowywać elementy bez osobnej dynamicznej alokacji.

Używaj referencji dla obowiązkowego pojedynczego argumentu, a wskaźnika, gdy brak obiektu jest sensownym stanem lub trzeba zmieniać cel. Dla wielu elementów wybieraj `span`, ponieważ sam wskaźnik nie przekazuje rozmiaru. Właścicielskie tablice o stałej długości zwykle najwygodniej wyraża `std::array`, a zmiennej długości `std::vector`.

**Ćwiczenie.** Czy `sizeof(p) / sizeof(*p)` oblicza długość tablicy, jeśli `p` jest wskaźnikiem przekazanym do funkcji?

**Odpowiedź.** Nie. Licznik obejmuje reprezentację wskaźnika, a mianownik jeden element. Wynik może przypadkiem wyglądać sensownie, lecz nie zależy od liczby elementów źródła. Przekaż rozmiar osobno, widok `span` albo referencję zachowującą typ całej tablicy.

Źródła: [deklaracje referencji](https://timsong-cpp.github.io/cppwp/n4950/dcl.ref), [arytmetyka wskaźników](https://timsong-cpp.github.io/cppwp/n4950/expr.add), [konwersja tablicy](https://timsong-cpp.github.io/cppwp/n4950/conv.array).

## Powiązane tematy

- [Smart pointery](../03_pamiec_i_czas_zycia/05_smart_pointery.md)
- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Pointer provenance](../zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

