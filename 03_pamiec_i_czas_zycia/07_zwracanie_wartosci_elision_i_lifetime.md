[← Spis treści](../README.md)

# Zwracanie wartości, elision i lifetime

## Wymagania wstępne

Potrzebujesz znajomości konstruktorów kopiujących i przenoszących, kategorii wartości, referencji oraz czasu życia obiektów tymczasowych. Przyjmujemy C++23, wyraźnie oddzielając gwarancje obecne od C++17 od opcjonalnych decyzji implementacji. Celem jest projektowanie wyniku, który ma właściwą własność danych i którego poprawność nie zależy od przypadkowego wyeliminowania kopii.

Zwrócenie przez wartość i zwrócenie referencji opisują odmienne kontrakty. W pierwszym przypadku wywołanie daje wynikowy obiekt, który może być niezależnym właścicielem. W drugim odbiorca dostaje dostęp do obiektu istniejącego gdzie indziej. Tani uchwyt, taki jak `string_view`, nadal jest wartością typu niewłaścicielskiego. Samo hasło „zwracamy przez wartość” nie dowodzi więc niezależności wskazywanych danych.

## Jak to działa krok po kroku

Rozważ funkcję `T make() { return T{arguments}; }` i użycie `T object = make();`. Gdy `T{arguments}` jest prvalue tego samego typu co wynik funkcji, od C++17 obiekt jest konstruowany bezpośrednio w miejscu docelowym. Nie trzeba najpierw materializować osobnego źródła i wykonywać ruchu. Usunięty konstruktor kopiujący i przenoszący nie przeszkadza w takim zwrocie. To własność modelu języka, a nie obietnica, że optymalizator będzie wystarczająco sprawny. Zobacz [N4950, dcl.init.general](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.general).

Inna sytuacja to `T make() { T local{arguments}; return local; }`. Nazwany lokalny obiekt może kwalifikować się do NRVO: implementacja ma prawo skonstruować go bezpośrednio jako obiekt wynikowy. Nie jest jednak zobowiązana. Gdy NRVO nie zachodzi, właściwe reguły inicjalizacji muszą nadal pozwalać utworzyć wynik. Przykład z typem niekopiowalnym i nieprzenoszalnym, poprawny dla bezpośredniego prvalue, nie staje się przez to poprawny dla dowolnego zwracania lokalnej zmiennej. Kryteria podaje [N4950, class.copy.elision](https://timsong-cpp.github.io/cppwp/n4950/class.copy.elision).

~~~cpp
#include <cassert>

struct Fixed {
    int value;
    explicit Fixed(int number) : value(number) {}
    Fixed(const Fixed&) = delete;
    Fixed(Fixed&&) = delete;
    ~Fixed() = default;
};

Fixed make_fixed() {
    return Fixed{42};
}

struct Parcel {
    inline static int moves = 0;
    int value;
    explicit Parcel(int number) : value(number) {}
    Parcel(const Parcel&) = delete;
    Parcel(Parcel&& source) noexcept : value(source.value) {
        ++moves;
    }
};

Parcel make_parcel() {
    Parcel local{17};
    return local;
}

int main() {
    Fixed fixed = make_fixed();
    assert(fixed.value == 42);

    Parcel::moves = 0;
    Parcel parcel = make_parcel();
    assert(parcel.value == 17);
    assert(Parcel::moves == 0 || Parcel::moves == 1);
}
~~~

Dla `Fixed` nie istnieje legalna operacja ruchu, która mogłaby uratować źle rozumiany model „temporary, potem przeniesienie”. Program jest poprawny dzięki bezpośredniej konstrukcji. Dla `Parcel` oba wyniki licznika są legalne: zero przy NRVO albo jeden, gdy lokalny obiekt przeniesiono do wyniku. Inicjalizacja `parcel` z prvalue zwróconego przez funkcję nie dodaje następnego ruchu. Asercja obejmuje oba przypadki i nie zależy od poziomu optymalizacji.

Wynik funkcji musi mieć dostępny, nieusunięty destruktor także w przykładzie bez kopiowania. Gwarancja konstrukcji nie znosi pozostałych wymagań dotyczących typu. Nie należy również przenosić uproszczenia na inicjalizację potencjalnie nakładających się podobiektów, takich jak podobiekt klasy bazowej. Zasada „każde wyrażenie wyglądające jak `T{}` zawsze usuwa wszystkie wymagania ruchu” byłaby zbyt szeroka. Wymagania `return` opisuje [N4950, stmt.return](https://timsong-cpp.github.io/cppwp/n4950/stmt.return).

## Pogłębienie mechanizmu

Warunki NRVO obejmują nazwany, nieulotny obiekt o automatycznym czasie przechowywania i zgodnym typie, z wyłączeniem między innymi parametru funkcji. `T identity(T value) { return value; }` może więc korzystać z ruchu, ale sam parametr nie kwalifikuje się do NRVO. Kilka różnych obiektów zwracanych z gałęzi może utrudnić eliminację. Poprawność programu i kontrakt wyniku powinny obejmować wszystkie legalne wykonania, także te zawierające ruch.

W C++23 nazwa odpowiedniej lokalnej zmiennej lub parametru w kontekście zwrotu jest *move-eligible* i traktowana jako xvalue. Pozwala to wybrać przenoszenie bez dopisywania `std::move`. Nie jest to ogólna zmiana kategorii nazwanych zmiennych w całym programie: poza odpowiednim kontekstem zwykła nazwa nadal jest lvalue. Reguły uwzględniają również właściwe lokalne referencje rvalue. Definicję zawiera [N4950, expr.prim.id.unqual](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.id.unqual).

Zapis `return std::move(local);` usuwa wymagany dla NRVO kształt operandu będącego nazwą lokalnego obiektu. Może zatem wymusić ruch tam, gdzie zwykłe `return local;` pozwalało go pominąć. `std::move` samo nie przenosi zasobu; tworzy wyrażenie o innej kategorii wartości. Dla zwracania składowej obiektu lub obiektu spoza kwalifikującego kontekstu sytuacja jest inna, więc nie zamieniaj tej wskazówki w zakaz każdego `std::move` wewnątrz `return`. Semantykę pomocników opisuje [N4950, forward](https://timsong-cpp.github.io/cppwp/n4950/forward).

`const` także wpływa na dostępne operacje. Lokalny `const T` może kwalifikować się do NRVO, ale po jego pominięciu xvalue zachowuje kwalifikację `const`. Typowy konstruktor `T(T&&)` nie przyjmuje takiego źródła, więc może zostać wybrana kopia. Dla typu move-only zwrot takiej lokalnej stałej bywa niepoprawny. Nie usuwaj stałości bez namysłu; zdecyduj, czy obiekt rzeczywiście ma pozostać niezmienny, czy jest przygotowywany do przekazania własności.

## Drugi przykład

Forwarding zachowuje kategorię wartości, lecz nie tworzy właściciela i nie odnawia czasu życia. Funkcja przekazująca referencję jest bezpieczna, jeśli odbiorca rozumie, do czego referencja prowadzi. Poniższy program pokazuje trzy różne decyzje: alias żyjącego źródła, kopię przez zwykłe `auto` oraz przejęcie wartości tymczasowej do właścicielskiego napisu przed końcem pełnego wyrażenia.

~~~cpp
#include <cassert>
#include <string>
#include <type_traits>
#include <utility>

template<class T>
decltype(auto) relay(T&& value) {
    return std::forward<T>(value);
}

int main() {
    std::string source = "alpha";
    static_assert(std::is_same_v<decltype(relay(source)), std::string&>);
    static_assert(std::is_same_v<decltype(relay(std::string{})), std::string&&>);

    auto& alias = relay(source);
    auto copy = relay(source);
    alias[0] = 'A';
    assert(source == "Alpha" && copy == "alpha");

    std::string owned = relay(std::string{"temporary"});
    assert(owned == "temporary");

    const std::string& extended = std::string{"extended"};
    assert(extended.size() == 8);
}
~~~

Bezpośrednie związanie lokalnej referencji `extended` z temporary przedłuża czas życia tego temporary. Przepis obejmuje określone formy wyrażeń i ma wyjątki; nie wynika z samego faktu, że gdzieś istnieje referencja. Temporary związane z parametrem referencyjnym trwa zasadniczo do końca pełnego wyrażenia zawierającego wywołanie. Ponowne związanie zwróconej referencji z kolejną referencją nie przedłuża tego czasu drugi raz. Szczegóły podaje [N4950, class.temporary](https://timsong-cpp.github.io/cppwp/n4950/class.temporary).

Poniższy program celowo odczytuje zniszczony obiekt i ma UB. Nie jest uruchamiany: napis tymczasowy przestaje istnieć przy średniku deklaracji `dangling`, choć typ referencji wygląda tak samo jak w poprawnym bezpośrednim związaniu.

~~~cpp,notest
#include <string>
#include <utility>

template<class T>
decltype(auto) relay(T&& value) {
    return std::forward<T>(value);
}

int main() {
    const auto& dangling = relay(std::string{"gone"});
    return static_cast<int>(dangling.size()); // UB: obiekt już nie żyje.
}
~~~

Podobnie funkcja zwracająca referencję do lokalnego obiektu nie staje się bezpieczna dzięki NRVO. Zwracanie referencji nie tworzy właścicielskiego wyniku, którego ten mechanizm dotyczy. W C++23 zachowaj szczególną ostrożność z `decltype(auto)`: dla `return local;` specjalna reguła `decltype` daje zadeklarowany typ, natomiast `return (local);` analizuje kategorię wyrażenia, uwzględniając move-eligible xvalue, i może wydedukować `T&&`. Nawiasy potrafią więc zamienić niezależny wynik w wiszącą referencję. Zobacz [N4950, dcl.type.decltype](https://timsong-cpp.github.io/cppwp/n4950/dcl.type.decltype).

## Porównanie i decyzje

Dla fabryki właścicielskiego obiektu domyślnie wybieraj wynik `T`, bez ręcznego zarządzania miejscem docelowym. Dla dostępu do istniejącego elementu zwracaj referencję lub widok z jawnym warunkiem czasu życia właściciela. Sprawdź również kategorię obiektu, na którym wywoływany jest akcesor: referencja do pola temporary często przestanie być użyteczna po średniku. Kwalifikatory referencyjne metod mogą pomóc rozdzielić dostęp do trwałego obiektu od pobrania wartości z temporary.

Nie opieraj logiki na efektach ubocznych konstruktorów kopiujących i przenoszących, które mogą legalnie zostać pominięte. Dziennik takich wywołań jest narzędziem obserwacji konkretnego wykonania. Do ustalenia własności i lifetime potrzebujesz reguły języka oraz kontraktu typu, a do oceny kosztu także rzeczywistego pomiaru. Poprawny program powinien dawać właściwy wynik przy każdym dozwolonym wyborze NRVO.

**Ćwiczenie 1.** Dlaczego niekopiowalny i nieprzenoszalny `Fixed` można zwrócić jako `return Fixed{42};`, ale nie wolno wymagać, aby zawsze działało `Fixed local{42}; return local;`?

<details>
<summary>Rozwiązanie</summary>

Pierwszy zapis korzysta z gwarantowanej od C++17 konstrukcji prvalue bez odrębnego źródła ruchu. Drugi polegałby na opcjonalnym NRVO, a program musi spełniać wymagania inicjalizacji także bez tej eliminacji. Usunięte konstruktory uniemożliwiają ten zwrot.

</details>

**Ćwiczenie 2.** Czy `auto saved = relay(std::string{"abc"});` pozostawia wiszący wynik?

<details>
<summary>Rozwiązanie</summary>

Nie. Zwykłe `auto` dedukuje właścicielski `std::string`, który zostaje zainicjalizowany z przekazanego xvalue przed zniszczeniem temporary. Użycie `auto&&` albo `decltype(auto)` zachowałoby referencję i po średniku prowadziło do dangling.

</details>

## Powiązane tematy

- [Storage duration i lifetime](01_storage_duration_i_lifetime.md)
- [Copy, move i rule of zero](04_copy_move_i_rule_of_zero.md)
- [Widoki, span, string_view i dangling](06_widoki_span_string_view_i_dangling.md)
- [Inicjalizacja i initializer_list](../02_podstawy_jezyka/08_inicjalizacja_i_initializer_list.md)
