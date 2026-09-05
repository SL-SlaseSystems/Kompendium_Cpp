[← Spis treści](../README.md)

# Funkcje specjalne i operatory

Funkcje specjalne sterują domyślną konstrukcją, kopiowaniem, przenoszeniem i destrukcją. Kompilator może je zadeklarować automatycznie, lecz zależności między regułami są subtelne. Najprostszy projekt korzysta z rule of zero: pola same mają poprawną semantykę wartości, więc klasa nie pisze ręcznie żadnej z pięciu operacji zasobowych.

~~~cpp
#include <cassert>
#include <compare>

class Point {
public:
    Point(int x, int y) : x_{x}, y_{y} {}

    Point operator+(const Point& other) const {
        return {x_ + other.x_, y_ + other.y_};
    }

    auto operator<=>(const Point&) const = default;

    [[nodiscard]] int x() const noexcept { return x_; }
    [[nodiscard]] int y() const noexcept { return y_; }

private:
    int x_;
    int y_;
};

int main() {
    const Point result = Point{1, 2} + Point{3, 4};
    assert((result == Point{4, 6}));
}
~~~

Przeciążony operator powinien zachowywać intuicję operatora. `+` zwykle nie zmienia operandów i zwraca wartość, `+=` modyfikuje lewy operand i zwraca `*this`. Nie można zmienić priorytetu, łączności ani liczby operandów operatora. Co najmniej jeden operand musi mieć typ klasowy lub enum.

Domyślne `operator<=>` może wygenerować porównania leksykograficzne pól, a `operator==` zostaje odpowiednio dostarczony. Semantyka pola musi jednak odpowiadać tożsamości logicznej typu. Nie generuj porównania z przypadkowego cache lub uchwytu implementacyjnego.

Assignment powinien obsługiwać samoprzypisanie zgodnie z kontraktem. Idiom copy-and-swap bywa prosty i bezpieczny wyjątkowo, ale może wprowadzić zbędny koszt. Najpierw wykorzystaj poprawne operacje pól, a ręczną optymalizację poprzyj pomiarem.

## Jak to działa krok po kroku

Najpierw ustal, czy zapis tworzy nowy obiekt, czy zmienia istniejący. `T b = a;` wywołuje konstrukcję kopiującą, a `b = a;` operator przypisania. Domyślny konstruktor kopiujący inicjalizuje bazy i pola z odpowiednich części źródła. Domyślny operator przypisania przypisuje do już istniejących podobiektów, co może być niemożliwe dla stałych pól lub referencji.

Kompilator deklaruje funkcje specjalne według reguł całej klasy. Każdy konstruktor deklarowany przez użytkownika wpływa na dostępność automatycznego konstruktora domyślnego. Deklarowany destruktor blokuje automatyczne deklarowanie ruchu. Pole niekopiowalne może usunąć domyślną kopię klasy. Zapis `= default` prosi o mechanizm języka, ale nie wymusza legalności operacji, której nie potrafi wykonać któreś pole.

W przykładzie `Point` operator dodawania konstruuje nową wartość. Domyślne porównanie analizuje kolejno `x_` i `y_`, więc kolejność pól staje się częścią porządku. Nie jest to porządek według odległości od początku układu ani sortowanie po sumie współrzędnych. Wybór operatora powinien odpowiadać udokumentowanemu znaczeniu typu.

## Pogłębienie mechanizmu

Funkcja domyślnie zdefiniowana przy pierwszej deklaracji zachowuje inne własności niż funkcja najpierw zadeklarowana, a dopiero poza klasą zdefiniowana przez `= default`. W tym drugim przypadku jest user-provided, co może wpłynąć na trywialność i zachowanie inicjalizacji wartościowej. Nie traktuj przesunięcia `= default` do pliku źródłowego jako zawsze czysto kosmetycznego zabiegu.

Usunięta funkcja nadal uczestniczy w wyborze przeciążenia. Jeśli jest najlepsza, wywołanie jest błędne; kompilator nie ma obowiązku szukać mniej pasującej dozwolonej alternatywy. Pozwala to świadomie blokować niechciane konwersje. Specjalne reguły dotyczą niektórych domyślnie usuniętych operacji ruchu, dlatego warto badać konkretny zestaw funkcji zamiast mechanicznie stosować jedną heurystykę.

Operator składowy ma niejawny parametr obiektu po lewej. Operator nieskładowy, często przyjaciel typu, może umożliwić symetryczne konwersje obu operandów. Typowy wzorzec implementuje `+=` jako podstawową operację, a `+` przez utworzenie kopii lewego argumentu i użycie `+=`. Zapobiega rozchodzeniu się definicji dodawania i dodawania z przypisaniem.

Nie wszystkie operatory mogą być przeciążane: nie można zmienić działania `.` ani `::`, a nowe symbole nie stają się operatorami. Przeciążone `&&` i `||` nie pomijają ewaluacji argumentów. Z kolei operator indeksowania powinien jasno określać sprawdzanie granic i rodzaj zwracanej referencji, ponieważ użytkownik może przechować ten wynik dłużej niż obiekt.

Domyślne `<=>` może zwracać kategorię silnego, słabego lub częściowego porządku wynikającą z podobiektów. Pole `double` prowadzi zwykle do `partial_ordering`, ponieważ NaN jest nieuporządkowane. Przypadkowe dodanie cache do domyślnego porównania może sprawić, że dwie logicznie równe wartości staną się nierówne. Operator `==` i funkcja haszująca muszą uzgadniać znaczenie równości, jeśli typ ma być kluczem kontenera nieuporządkowanego.

## Drugi przykład

Ten typ ma jedno znaczenie liczbowe, symetryczne dodawanie i domyślne porównanie. Żadna operacja nie zarządza surowym zasobem, więc ręczne definiowanie kopiowania i destrukcji byłoby zbędne.

~~~cpp
#include <cassert>
#include <compare>

class Distance {
    int metres_;
public:
    explicit Distance(int value) : metres_{value} {}
    Distance& operator+=(Distance other) {
        metres_ += other.metres_;
        return *this;
    }
    friend Distance operator+(Distance left, Distance right) {
        left += right;
        return left;
    }
    auto operator<=>(const Distance&) const = default;
};

int main() {
    Distance first{3};
    const Distance second{4};
    assert((first + second == Distance{7}));
    assert(first == Distance{3});
    Distance& same = (first += second);
    assert(&same == &first);
    assert(first > second);
}
~~~

Przekazywanie niewielkiego `Distance` przez wartość jest celowe. `+` modyfikuje tylko swoją kopię, natomiast `+=` zmienia odbiorcę i zwraca referencję do niego. Przykład wymaga, aby suma mieściła się w `int`; produkcyjny typ jednostki powinien określić politykę przepełnienia.

## Porównanie i decyzje

Stosuj operator, gdy ma powszechnie rozumiane znaczenie dla typu. Działania takie jak zapis do sieci, kosztowna aktualizacja bazy czy walidowana zmiana jednostki zwykle lepiej wyrazić nazwaną metodą. Zanim dopiszesz funkcję specjalną, sprawdź, czy to reprezentacja wymaga zmiany: pole RAII często usuwa potrzebę całej ręcznej obsługi zasobów.

**Ćwiczenie.** Klasa ma pole `const int id`. Dlaczego może pozwalać na kopiowanie przy konstrukcji, a odrzucać przypisanie?

**Odpowiedź.** Konstruktor może zainicjalizować nowe stałe pole wartością źródła. Operator przypisania musiałby zmienić już istniejące `id`, czego `const` zabrania. Dostępność konstrukcji i przypisania to odrębne własności typu; nie należy zakładać jednej na podstawie drugiej.

Źródła: [funkcje specjalne](https://timsong-cpp.github.io/cppwp/n4950/special), [funkcje default i delete](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct.def.default), [przeciążone operatory](https://timsong-cpp.github.io/cppwp/n4950/over.oper), [porównania domyślne](https://timsong-cpp.github.io/cppwp/n4950/class.compare).

## Powiązane tematy

- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
- [Value semantics](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
