[← Spis treści](../README.md)

# Leksemy, deklaracje i zakresy

Kod C++ składa się z tokenów: słów kluczowych, identyfikatorów, literałów, operatorów i znaków interpunkcyjnych. Komentarze `//` trwają do końca wiersza, a `/* ... */` mogą obejmować wiele wierszy, lecz nie zagnieżdżają się. Wielkość liter ma znaczenie, więc `value` i `Value` są innymi nazwami.

Deklaracja wprowadza nazwę i opisuje jej typ. Definicja dodatkowo tworzy obiekt, ciało funkcji albo inną encję wymagającą definicji. Zakres (*scope*) określa, gdzie nazwa jest widoczna; czas życia obiektu to osobne zagadnienie i nie zawsze pokrywa się z zakresem nazwy.

~~~cpp
#include <cassert>

int twice(int value); // deklaracja

int twice(int value) { // definicja
    return value * 2;
}

int main() {
    int result = twice(4);
    {
        int result = 10; // przesłania zewnętrzną nazwę
        assert(result == 10);
    }
    assert(result == 8);
}
~~~

Blok `{}` tworzy zakres blokowy. Parametry funkcji, elementy klasy, przestrzenie nazw, inicjalizatory instrukcji `if` i `for` mają własne reguły zakresu. Przesłanianie (*shadowing*) jest legalne, ale może utrudniać czytanie. Ostrzeżenia kompilatora pomagają wykryć przypadkowe przesłonięcia.

Identyfikatory rozpoczynające się podkreśleniem i wielką literą oraz nazwy zawierające podwójne podkreślenie są zarezerwowane dla implementacji. W globalnej przestrzeni nazw zarezerwowane są także nazwy zaczynające się od pojedynczego podkreślenia. Nie używaj takich nazw we własnym API.

## Inicjalizacja

Zwykła lokalna zmienna `int` bez inicjalizatora ma w C++23 wartość indeterminate; jej odczyt prowadzi do undefined behavior. Szczególne wyjątki dotyczą pewnych operacji na typach bajtowych, nie zwykłych obliczeń na `int`. Inicjalizuj obiekty przy deklaracji, najlepiej nawiasami klamrowymi, gdy chcesz blokować konwersje zawężające.

## Jak to działa krok po kroku

Kompilator najpierw rozpoznaje tokeny, a potem interpretuje ich układ jako deklaracje i wyrażenia. Biały znak zwykle tylko oddziela tokeny, lecz `long long` musi pozostać dwoma słowami, a `++` jest jednym operatorem. Komentarz nie tworzy zakresu. Dyrektywy preprocessora działają wcześniej niż analiza typów: makro nie respektuje prywatności klasy ani zwykłych reguł wyszukiwania nazw.

W pierwszym programie deklaracja `twice` informuje, jakie wywołanie jest dozwolone. Następująca po niej definicja dostarcza ciało tej samej funkcji. Gdy analizowane jest `twice(4)`, deklaracja musi już być osiągalna. Wewnętrzne `result` wprowadza nowy obiekt. Wyszukiwanie niekwalifikowane znajduje najbliższą pasującą deklarację, dlatego asercja wewnątrz bloku sprawdza dziesięć. Wyjście z bloku kończy życie wewnętrznego obiektu i odsłania nazwę zewnętrzną; nie przywraca żadnej zapisanej wcześniej wartości.

Miejsce wprowadzenia nazwy może poprzedzać inicjalizator. Zapis `int x = x;` wewnątrz bloku nie kopiuje automatycznie zewnętrznego `x`: po prawej znajduje już nową zmienną. Dla zwykłego lokalnego `int` jest to w C++23 odczyt wartości indeterminate i prowadzi do UB. Ostrzeżenia o niezainicjalizowanych zmiennych są tu cenniejsze niż obserwowanie przypadkowego wyniku.

## Pogłębienie mechanizmu

Zakres, powiązanie nazwy (*linkage*) i czas życia odpowiadają na trzy różne pytania. Lokalny `static` ma nazwę dostępną tylko w swoim bloku, ale jego obiekt może przetrwać wszystkie wywołania funkcji. Deklaracja `extern int count;` zwykle deklaruje obiekt zdefiniowany gdzie indziej; nie tworzy kolejnego licznika przy każdym dołączeniu nagłówka. Natomiast `extern int count = 1;` jest definicją, ponieważ zawiera inicjalizator.

Reguła jednej definicji, ODR, ogranicza sposób rozmieszczania definicji między jednostkami translacji. Zwykła niewbudowana zmienna globalna lub funkcja nie może otrzymać wielu zwykłych definicji w programie. Dla klas, szablonów i encji `inline` istnieją szczegółowe wyjątki, wymagające między innymi zgodności definicji. To powód, dla którego nagłówek nie jest dowolnym miejscem na definicję globalnego stanu.

Kwalifikacja `config::limit` wskazuje przestrzeń nazw, a `::limit` globalny zakres. `using` może udostępniać konkretną nazwę lub tworzyć alias typu, lecz nie tworzy kopii obiektu. `using namespace` w nagłówku poszerza wyszukiwanie także w kodzie dołączającym ten nagłówek; konflikt może ujawnić się dopiero po dodaniu nowej biblioteki.

## Drugi przykład

Poniższy licznik pokazuje, że widoczność nazwy i trwałość obiektu są niezależne. Obiekt `calls` inicjalizuje się raz, a każde wywołanie zwiększa ten sam stan.

~~~cpp
#include <cassert>

namespace config {
    inline constexpr int limit = 3;
}

int next_call() {
    static int calls{};
    return ++calls;
}

int main() {
    int limit = 9;
    assert(limit == 9);
    assert(config::limit == 3);
    assert(next_call() == 1);
    if (const int call = next_call(); call < config::limit) {
        assert(call == 2);
    }
    assert(next_call() == 3);
}
~~~

Nazwa `call` jest dostępna w warunku oraz obu gałęziach instrukcji `if`, ale nie po niej. `limit` w `main` nie zmienia obiektu `config::limit`. Kwalifikacja rozstrzyga wybór bez zmiany zakresu którejkolwiek deklaracji. Przykład nie jest licznikiem bezpiecznym dla równoczesnych modyfikacji z wielu wątków.

## Porównanie i decyzje

Deklaruj zmienną w najmniejszym zakresie obejmującym jej rzeczywiste użycia. W ten sposób kompilator pomaga wykrywać przypadkowy dostęp po zakończeniu potrzebnej operacji. Zamiast używać przesłaniania do zmiany znaczenia nazwy, nazwij kolejne etapy obliczenia, na przykład `raw_size` i `checked_size`. Dla publicznego API wybieraj własną przestrzeń nazw, aby ograniczyć kolizje z zależnościami.

Rozdzielając projekt na nagłówek i plik implementacji, umieść deklarację funkcji w nagłówku, a jedną definicję w pliku źródłowym. Definicje klas i szablonów zwykle muszą być dostępne użytkownikowi; nie wynika z tego, że każda zmienna globalna również powinna być definiowana w nagłówku. `inline constexpr` nadaje się do współdzielonej stałej od C++17.

**Ćwiczenie.** Czy dwukrotne wywołanie funkcji zawierającej `static int n = 0; return ++n;` tworzy dwa obiekty? Czy można odwołać się do `n` z `main`?

**Odpowiedź.** Jest jeden obiekt, a wyniki kolejnych wywołań to jeden i dwa. Nazwa pozostaje lokalna, więc bezpośredni zapis `n` w `main` go nie odnajdzie. Funkcja zapewnia dostęp do zachowania tego obiektu, nie poszerza zakresu jego nazwy.

Reguły źródłowe: [zakresy nazw](https://timsong-cpp.github.io/cppwp/n4950/basic.scope), [deklaracje i definicje](https://timsong-cpp.github.io/cppwp/n4950/basic.def), [ODR](https://timsong-cpp.github.io/cppwp/n4950/basic.def.odr).

## Powiązane tematy

- [Typy i literały](02_typy_podstawowe_i_literaly.md)
- [Storage duration i lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Namespaces](../08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)

