[← Spis treści](../README.md)

# Inicjalizacja i initializer_list

## Wymagania wstępne

Potrzebujesz znajomości deklaracji, konstruktorów, `const`, przeciążeń oraz podstaw `std::vector` i `std::unique_ptr`. Rozdział używa C++23. Jego celem jest rozpoznawanie operacji wynikającej ze składni: identycznie wyglądająca lista wartości może inicjalizować agregat, wywoływać konstruktor albo tworzyć pomocniczą tablicę. Od tej decyzji zależą wartości początkowe, koszt kopiowania i czas życia danych.

Inicjalizacja tworzy początkowy stan obiektu; przypisanie zmienia stan obiektu już istniejącego. Zapis `T x = expression;` jest inicjalizacją, mimo znaku równości. Nie oznacza obligatoryjnego utworzenia pustego `x`, a następnie przypisania. Rozróżnienie ma znaczenie dla typów bez operatora przypisania, pól `const` i referencji. Konstruktor nie może „później przypisać” referencji do innego obiektu, dlatego zależności trzeba ustalić podczas inicjalizacji.

## Jak to działa krok po kroku

Najpierw ustal typ i czas przechowywania, potem obecność inicjalizatora, następnie wybraną regułę. Lokalny automatyczny `int x;` podlega *default-initialization*, która dla tego typu nie wykonuje inicjalizacji. Odczyt jego nieustalonej wartości jest w C++23 zasadniczo UB; wyjątki dotyczące wybranych operacji na bajtach nie pozwalają odczytywać takiego `int`. Natomiast obiekt o statycznym czasie przechowywania jest wcześniej zerowany. Sam brak inicjalizatora nie wystarcza więc do przewidzenia wartości.

`int x{};` daje zero. Jest to inicjalizacja listowa pustą listą, prowadząca tutaj do *value-initialization*, a następnie zerowania. Wyrażenie `int()` również daje wartość zero. Dla klasy default-initialization wybiera konstruktor domyślny, który odpowiada za stan pól. Value-initialization może dodatkowo wyzerować obiekt przed konstruktorem, zależnie od właściwości konstruktora. Nie utożsamiaj ogólnej nazwy mechanizmu z jedną instrukcją zerowania pamięci. Reguły rozpisuje [N4950, dcl.init.general](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.general).

~~~cpp
#include <cassert>
#include <initializer_list>
#include <type_traits>
#include <vector>

struct Defaulted {
    int value;
    Defaulted() = default;
};

struct Config {
    int attempts = 3;
    bool verbose;
};

int main() {
    int zero{};
    Defaulted object{};
    Config config{};
    std::vector<int> repeated(4, 7);
    std::vector<int> listed{4, 7};
    auto scalar{7};
    auto list = {7};

    static_assert(std::is_same_v<decltype(scalar), int>);
    static_assert(std::is_same_v<decltype(list), std::initializer_list<int>>);
    assert(zero == 0 && object.value == 0);
    assert(config.attempts == 3 && !config.verbose);
    assert(repeated.size() == 4 && repeated[3] == 7);
    assert(listed.size() == 2 && listed[0] == 4);
}
~~~

`Defaulted` ma konstruktor zadeklarowany przez autora, lecz nie *user-provided*: został jawnie ustawiony jako domyślny przy pierwszej deklaracji. Dlatego `Defaulted{}` zapewnia tutaj zerowanie pola. Gdyby konstruktor miał ciało `Defaulted() {}`, sam pusty zapis klamrowy nie gwarantowałby wartości `value`. Najczytelniejsze zabezpieczenie to inicjalizator pola, na przykład `int value = 0;`, który bezpośrednio opisuje domyślny stan klasy.

`Config` jest agregatem. Pominięte pola korzystają z własnych inicjalizatorów, a pozostałe otrzymują odpowiednią inicjalizację pustą listą. `attempts` dostaje zatem trzy, a `verbose` fałsz. Przy analizie rzeczywistej klasy najpierw sprawdź, czy nadal jest agregatem: dodanie konstruktora może zmienić interpretację klamer. Inicjalizacja agregatowa i wywołanie konstruktora nie są zamiennymi opisami tego samego mechanizmu.

## Pogłębienie mechanizmu

Dla odpowiedniej klasy niebędącej agregatem wybór konstruktora przy niepustej liście ma dwie fazy. Najpierw rozpatrywane są konstruktory przyjmujące `std::initializer_list`, traktujące całą listę jako argument. Dopiero brak pasującego kandydata otwiera zwykłe przeciążenia. Dlatego wektor z nawiasami okrągłymi zawiera cztery siódemki, a wektor z klamrami dwa elementy. Pusta lista i konstruktor domyślny mają szczególne reguły; `std::vector<int>{}` tworzy pusty wektor. Szczegóły podaje [N4950, over.match.list](https://timsong-cpp.github.io/cppwp/n4950/over.match.list).

Zakaz *narrowing* jest dodatkowym sprawdzeniem inicjalizacji listowej. Obejmuje między innymi konwersję liczby zmiennoprzecinkowej na całkowitą oraz część konwersji między typami całkowitymi. `int{3.0}` jest błędne, chociaż konkretna wartość wygląda bezpiecznie. Dla pewnych konwersji całkowitych istnieją wyjątki, gdy wyrażenie stałe mieści się w typie docelowym: `unsigned char{42}` jest poprawne. Zmienna przechowująca akurat 42 nie staje się przez to wyrażeniem stałym. Sprawdzenie dotyczy reguł typów i stałych, nie przewidywania danych podczas wykonania.

Wybranie konstruktora listowego wymagającego narrowing nie uruchamia automatycznie ponownego wyboru wygodniejszego przeciążenia. Program jest błędny. Podobnie `T x{argument};` i `T x = {argument};` różnią się obsługą `explicit`: jeżeli copy-list-initialization ostatecznie wybierze konstruktor jawny, inicjalizacja jest niepoprawna. Te rozstrzygnięcia opisuje [N4950, dcl.init.list](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.list).

Lista klamrowa sama nie jest zwykłym wyrażeniem posiadającym typ. Dedukcja `auto x = {1, 2};` ma specjalną obsługę tworzącą `initializer_list<int>`, natomiast `auto x{1};` daje `int`. Bezpośrednia lista dla takiego `auto` musi zawierać pojedynczy element. Szablon `template<class T> void f(T);` nie potrafi ogólnie wydedukować `T` z samego `f({1, 2})`; potrzebuje odpowiedniego parametru listowego albo jawnie nazwanego typu. Zobacz [reguły auto w N4950](https://timsong-cpp.github.io/cppwp/n4950/dcl.spec.auto).

## Drugi przykład

`std::initializer_list<T>` zapewnia dostęp do elementów typu `const T`. Kopia tego uchwytu nie kopiuje tablicy. To wygodne dla krótkotrwałego odczytu, ale nie jest właścicielskim kontenerem. Konstruktor wektora kopiuje wartości z takiej listy do własnego magazynu; później wektor nie zależy od tablicy pomocniczej. Własności interfejsu potwierdza [N4950, support.initlist](https://timsong-cpp.github.io/cppwp/n4950/support.initlist).

~~~cpp
#include <cassert>
#include <initializer_list>
#include <memory>
#include <type_traits>
#include <vector>

int sum(std::initializer_list<int> values) {
    int result = 0;
    for (int value : values) {
        result += value;
    }
    return result;
}

int main() {
    std::initializer_list<int> values{2, 3, 5};
    auto alias = values;
    static_assert(std::is_same_v<decltype(*values.begin()), const int&>);
    assert(alias.begin() == values.begin());
    assert(sum(values) == 10 && sum({4, 6}) == 10);

    std::vector<std::unique_ptr<int>> owners;
    owners.reserve(2);
    owners.push_back(std::make_unique<int>(11));
    owners.push_back(std::make_unique<int>(13));
    assert(*owners[0] + *owners[1] == 24);
}
~~~

Tablica związana bezpośrednio z lokalnym `values` żyje przez czas życia tej listy. `alias` wskazuje te same elementy, ale jego skopiowanie nie ustanawia nowego przedłużenia czasu życia. Dla `sum({4, 6})` tablica trwa do końca pełnego wyrażenia, więc funkcja może ją odczytać podczas wywołania. Zwrócenie otrzymanej listy i zachowanie jej po średniku nie zachowałoby elementów. Mechanizm ma te same ograniczenia co referencje do obiektów tymczasowych, opisane w [N4950, class.temporary](https://timsong-cpp.github.io/cppwp/n4950/class.temporary).

Poniższy blok jest celowo niekompilowalny: pierwszy wiersz zawęża, drugi wymaga kopiowania `unique_ptr` z elementu listy będącego `const`. Nie należy go uruchamiać.

~~~cpp,notest
#include <memory>
#include <vector>

int main() {
    int narrowed{3.0};
    std::vector<std::unique_ptr<int>> owners{
        std::make_unique<int>(7)
    };
}
~~~

Dodanie `std::move` wokół listy nie usuwa `const` z jej elementów. Nawet przeniesienie `const unique_ptr` nie pasuje do konstruktora przenoszącego oczekującego modyfikowalnego źródła. Budowanie wektora przez `push_back` w drugim programie przekazuje natomiast świeże, niestałe obiekty tymczasowe. To rozwiązuje rzeczywistą przeszkodę typów, zamiast sugerować kompilatorowi większą liczbę ruchów.

## Porównanie i decyzje

Używaj klamer, gdy chcesz inicjalizacji agregatu, jawnej listy elementów albo kontroli narrowing. Wybieraj nawiasy okrągłe, gdy argumenty oznaczają parametry konstruktora, na przykład liczbę elementów i wartość powtarzaną. Dla klasy udostępniającej oba rodzaje konstruktorów sprawdzaj semantykę zamiast stosować mechaniczną zamianę nawiasów. Dodanie przeciążenia listowego do biblioteki może zmienić zachowanie istniejących wywołań z klamrami.

Własne API przyjmujące `initializer_list` powinno przetworzyć wartości od razu albo skopiować je do właścicielskiego kontenera. Przechowywanie samego uchwytu jest poprawne tylko przy wyraźnie kontrolowanym czasie życia tablicy. Dla przenoszenia zasobów lepszy bywa kontener przekazywany przez wartość lub interfejs zakresowy z odpowiednimi wymaganiami. Przed projektem API ustal, czy odbiorca tylko ogląda elementy, kopiuje je, czy przejmuje ich własność.

**Ćwiczenie 1.** Jak różnią się `std::vector<int> a(2, 9)` i `std::vector<int> b{2, 9}`? Co powstanie z `std::vector<int> c{}`?

<details>
<summary>Rozwiązanie</summary>

`a` zawiera dwie dziewiątki. `b` zawiera liczby dwa i dziewięć. `c` jest pustym wektorem; puste klamry nie wymuszają konstruktora listowego, gdy zastosowanie mają reguły konstruktora domyślnego.

</details>

**Ćwiczenie 2.** Funkcja zapisuje otrzymany `initializer_list<int>` w polu klasy. Wywołano ją jako `save({1, 2, 3})`. Czy odczyt pola w następnej instrukcji jest bezpieczny?

<details>
<summary>Rozwiązanie</summary>

Nie. Skopiowano uchwyt, a pomocnicza tablica przestała istnieć po pełnym wyrażeniu wywołania. Pole powinno być właścicielskim kontenerem, do którego wartości zostaną skopiowane przed końcem wywołania.

</details>

## Powiązane tematy

- [Zmienne, const i constexpr](03_zmienne_const_i_constexpr.md)
- [Funkcje i przeciążanie](05_funkcje_i_przeciazanie.md)
- [Copy, move i rule of zero](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Zwracanie wartości, elision i lifetime](../03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md)
