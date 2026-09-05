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

Dla `forward_to_consume(text)` dedukcja rozpoznaje argument lvalue. Parametr szablonu `T` staje się `std::string&`, a zapis `T&&` po reference collapsing oznacza `std::string&`. `std::forward<T>(value)` odtwarza lvalue i wybrana zostaje funkcja przyjmująca `const std::string&`. Nie ma przeniesienia zasobu ani utworzenia dodatkowego napisu.

Dla `forward_to_consume(std::move(text))` argument jest xvalue, więc `T` to `std::string`. Parametr ma typ `std::string&&`, ale jego nazwa nadal jest wyrażeniem lvalue. Dopiero `std::forward<T>` produkuje xvalue, które może związać się z drugim przeciążeniem. Samo wywołanie funkcji przyjmującej rvalue reference jeszcze nie zmienia napisu; trzeba rzeczywiście wykonać operację, która wykorzystuje tę zgodę, na przykład skonstruować inny `string`.

## Pogłębienie mechanizmu

Kategorie wartości opisują wyrażenia, nie trwałą etykietę zmiennej. Zmienna zadeklarowana jako `T&&` ma nazwę będącą lvalue. Wywołanie funkcji zwracającej `T&` jest lvalue, zwracającej `T&&` jest xvalue, a zwracającej `T` zwykle prvalue. `decltype((expr))` koduje tę różnicę jako odpowiednio `T&`, `T&&` albo `T`; pojedyncze, nieujęte w nawiasy użycie nazwy ma szczególną regułę `decltype` i zwraca deklarowany typ.

Od C++17 prvalue klasy może bezpośrednio inicjalizować obiekt docelowy, bez wcześniejszej „tymczasowej kopii”. Dlatego `return T{...};` może działać dla typu niekopiowalnego i nieprzenoszalnego. NRVO dla nazwanej zmiennej lokalnej jest inną, opcjonalną optymalizacją. Dodanie `std::move(local)` odbiera takiej instrukcji powrotu postać wymaganą dla NRVO i zwykle nie przynosi oczekiwanej korzyści.

Forwarding reference wymaga cv-niekwalifikowanego parametru typu dedukowanego dla danego wywołania. `const T&&` nie jest forwarding reference. W klasie `Box<T>` parametr zwykłej metody `void set(T&&)` używa już ustalonego `T`, więc również nie spełnia tej roli. Osobny szablon metody `template<class U> void set(U&&)` może ją pełnić. `auto&&` zwykle stosuje analogiczną dedukcję, z wyjątkiem szczególnych reguł initializer lists.

Przekazywanie dalej nie przedłuża lifetime. Wrapper zwracający referencję do przekazanego obiektu tymczasowego może oddać wiszącą referencję po końcu pełnego wyrażenia wywołania. Idealne zachowanie cv/ref bywa zatem niewłaściwym kontraktem API, gdy funkcja powinna zapewnić własność wyniku. Również dwukrotne użycie `forward<T>(value)` może przekazać ten sam argument do dwóch operacji konsumujących, a drugi odbiorca zobaczy już stan po przeniesieniu.

## Drugi przykład

~~~cpp
#include <cassert>
#include <string>
#include <type_traits>
#include <utility>

struct Box {
    std::string value;
    const std::string& get() const & { return value; }
    std::string get() && { return std::move(value); }
};
int main() {
    Box box{"dane"};
    static_assert(std::is_same_v<decltype(box.get()), const std::string&>);
    const auto& view = box.get();
    auto owned = Box{"wynik"}.get();
    assert(view == "dane" && owned == "wynik");
}
~~~

Metoda z kwalifikatorem `const &` udostępnia referencję do pola istniejącego obiektu. Wywołanie na tymczasowym `Box` wybiera przeciążenie `&&`, które zwraca własny `string` przez wartość. Dzięki temu `owned` przeżywa zniszczenie tymczasowego pudełka. Zwrócenie `std::string&&` zamiast wartości nie byłoby równoważne: referencja wskazywałaby pole obiektu kończącego życie.

## Porównanie i decyzje

Przyjmuj przez wartość, gdy funkcja potrzebuje swojej kopii i zwykle ją zachowa. Użyj `const T&` do synchronicznego odczytu, a konkretnego `T&&` do jednoznacznej operacji konsumującej. Forwarding reference sprawdza się w fabryce lub adapterze wywołania, lecz znacznie rozszerza zbiór kandydatów i może przechwycić wywołanie oczekiwane dla copy constructor. Ograniczaj takie konstruktory conceptami i wykluczaj własny typ, gdy wymaga tego projekt.

**Ćwiczenie.** Co otrzymuje typowy konstruktor po `std::move(const_string)`? **Odpowiedź:** `const std::string&&`, który nie pasuje do modyfikowalnego parametru move constructor; zwykle następuje kopia przez `const&`. Czy `std::forward<int>(named_int)` zawsze jest właściwe? Nie: jawne `int` wymusza xvalue, choć pierwotny argument mógł być lvalue. Szablon musi używać parametru wynikającego z rzeczywistej dedukcji.

Źródła: [N4950: kategorie wartości](https://timsong-cpp.github.io/cppwp/n4950/basic.lval) i [dedukcja argumentów wywołania](https://timsong-cpp.github.io/cppwp/n4950/temp.deduct.call).

### Dedukcja nie odtwarza składni wywołania

Lista `{1, 2, 3}` nie jest zwykłym wyrażeniem o jednym typie, z którego dowolna forwarding reference potrafi wydedukować `T`. Konstruktor kontenera może obsługiwać `initializer_list`, lecz generyczna fabryka pośrednicząca w wywołaniu potrzebuje często jawnego obiektu takiej listy lub osobnego przeciążenia. Podobnie nazwa przeciążonej funkcji nie wyznacza jednej wartości, dopóki kontekst nie wybierze sygnatury. Perfect forwarding zachowuje informacje już uzyskane przez dedukcję, nie tworzy brakujących informacji.

Pole bitowe również nie zachowuje się jak zwykły adresowalny obiekt przy wiązaniu referencji. Wrapper z `T&&` może odrzucić wywołanie, które bezpośrednia funkcja przyjmująca liczbę przez wartość obsłużyłaby bez problemu. W takiej sytuacji jawna kopia wartości często najlepiej wyraża intencję. Dążenie do zachowania każdej referencji może zwiększyć liczbę ograniczeń bez korzyści wydajnościowej.

C++23 dodaje `std::forward_like`, które przenosi odpowiedni model cv/ref z innego typu na wyrażenie. Jest przydatne przy implementacji dostępu do pól zależnego od kategorii obiektu odbiorcy. Nie zastępuje analizy lifetime ani nie gwarantuje, że zwrócona referencja będzie bezpieczna po zniszczeniu właściciela.

Dedukcja typu wyniku przez auto i decltype(auto) prowadzi do odmiennych decyzji przy proxy references. Iterator nie musi zwracać prawdziwego T&; może oddawać niewielki obiekt pośredniczący w dostępie, jak w niektórych wyspecjalizowanych kontenerach. Skopiowanie takiego proxy niekoniecznie tworzy niezależną kopię wartości. W kodzie generycznym sprawdzaj typ referencji iteratora oraz zamierzone zachowanie wyniku, zamiast utożsamiać każdy zapis auto z bezpiecznym posiadaniem danych.

## Powiązane tematy

- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Dedukcja auto i decltype](../05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)

