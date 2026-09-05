[← Spis treści](../README.md)

# Funkcje i przeciążanie

Funkcja ma typ zwracany, nazwę, listę parametrów i opcjonalne specyfikatory. Argument przekazywany przez wartość tworzy osobny obiekt parametru. `const T&` pozwala czytać bez kopiowania i może wiązać temporary, `T&` oznacza modyfikowalny argument istniejący, a `T&&` ma różne role zależnie od kontekstu. Dla małych typów wartościowych przekazanie przez wartość jest zwykle najprostsze.

~~~cpp
#include <cassert>
#include <string>
#include <string_view>

std::string greet(std::string_view name) {
    return "Witaj, " + std::string{name};
}

int area(int side) {
    return side * side;
}

int area(int width, int height) {
    return width * height;
}

int main() {
    assert(greet("Ada") == "Witaj, Ada");
    assert(area(4) == 16);
    assert(area(4, 5) == 20);
}
~~~

Przeciążenia mają tę samą nazwę, ale różne listy parametrów. Typ zwracany sam nie rozróżnia przeciążenia. Kompilator tworzy zbiór kandydatów, odrzuca niewykonalne, porównuje sekwencje konwersji i wybiera najlepszą funkcję. Niejawne konwersje i parametry domyślne mogą spowodować niejednoznaczność.

Parametry domyślne są dołączane w miejscu wywołania, dlatego ich zmiana w publicznym nagłówku może wymagać przebudowania klientów. Funkcja `inline` pozwala na identyczne definicje w wielu jednostkach translacji; nie jest poleceniem optymalizacji. `[[nodiscard]]` ostrzega, gdy wynik o istotnym znaczeniu został pominięty.

Zwracanie referencji lub wskaźnika wymaga, aby wskazywany obiekt żył wystarczająco długo. Nigdy nie zwracaj referencji do zwykłej zmiennej lokalnej. Return value optimization i move semantics sprawiają, że zwracanie obiektów przez wartość jest naturalnym i często wydajnym wyborem.

## Jak to działa krok po kroku

Przy wywołaniu funkcji kompilator najpierw wyszukuje nazwę i zbiera kandydatów. Obejmuje to zwykłe wyszukiwanie oraz, dla odpowiednich wywołań, ADL korzystające z typów argumentów. Następnie sprawdza liczbę parametrów, dostępne argumenty domyślne, możliwość konwersji i ograniczenia szablonów. Dopiero wśród funkcji wykonalnych porównuje dopasowanie. Dostępność `private` nie służy jako wygodny filtr pozwalający wybrać gorszy publiczny overload: kontrola dostępu następuje po wyborze.

Dokładne dopasowanie zwykle wygrywa z promocją, a promocja ze zwykłą konwersją. Dla argumentu `short` przeciążenie przyjmujące `int` może więc wygrać z wersją `double`. To porównanie sekwencji konwersji, nie arbitralne mierzenie, ile bajtów różni typy. Przy kilku argumentach może nie być jednej funkcji lepszej od wszystkich pozostałych, co daje niejednoznaczność.

Po wyborze funkcji obliczane są argumenty i inicjalizowane parametry. Parametr przez wartość jest osobnym obiektem, ale sposób jego utworzenia zależy od źródła: może dojść do kopiowania, przeniesienia albo bezpośredniej konstrukcji. Referencja wiąże się z istniejącym obiektem. Nazwany parametr `T&&` użyty wewnątrz funkcji jest wyrażeniem lvalue; ruch dalej wymaga świadomego `std::move` albo, dla forwarding reference, `std::forward`.

## Pogłębienie mechanizmu

Parametry `int` oraz `const int` przekazywane przez wartość nie tworzą dwóch różnych przeciążeń. Najwyższa kwalifikacja nie należy tu do typu funkcji, choć w definicji ogranicza modyfikowanie lokalnego parametru. Inaczej jest z `int&` i `const int&`: kwalifikacja dotyczy obiektu, do którego uzyskuje się dostęp, i wpływa na możliwość wiązania argumentu.

Deklaracja parametru `int values[10]` jest dostosowywana do `int*`. Nie wymusza dziesięciu elementów. Dla wymagania stałego rozmiaru użyj referencji do tablicy lub `std::span<int, 10>`, a dla rozmiaru dynamicznego `std::span<int>`. Składnia przypominająca tablicę nie stanowi kontroli jej granic.

Domyślne argumenty nie są częścią typu funkcji i są dobierane z deklaracji widocznych przy wywołaniu. `noexcept` natomiast od C++17 jest elementem typu funkcji. Obietnica `noexcept` nie zatrzymuje kompilacji każdego potencjalnie rzucającego wywołania; jeśli wyjątek faktycznie opuści funkcję, nastąpi `std::terminate`. Stosuj tę obietnicę na podstawie zachowania wszystkich operacji, które mogą się wykonać.

Referencja zwracana przez funkcję nie przedłuża automatycznie życia wskazywanego obiektu. Szczególnie niebezpieczna jest funkcja przyjmująca `const T&` i zwracająca ten sam alias: argument tymczasowy może zniknąć na końcu instrukcji wywołującej. Zwrócenie wartości lepiej wyraża niezależny wynik, a gwarantowana konstrukcja z prvalue i opcjonalne NRVO często eliminują koszt dodatkowego obiektu.

## Drugi przykład

Przeciążenia referencyjne pozwalają obserwować różnicę między obiektem modyfikowalnym, stałym i tymczasowym. Jednoargumentowe wywołanie funkcji z wartością domyślną nadal wywołuje tę samą funkcję dwuparametrową.

~~~cpp
#include <cassert>
#include <string_view>
#include <utility>

std::string_view category(int&) { return "mutable lvalue"; }
std::string_view category(const int&) { return "const lvalue"; }
std::string_view category(int&&) { return "rvalue"; }

int scale(int value, int factor = 2) { return value * factor; }

int main() {
    int value = 5;
    const int fixed = 6;
    assert(category(value) == "mutable lvalue");
    assert(category(fixed) == "const lvalue");
    assert(category(7) == "rvalue");
    assert(category(std::move(value)) == "rvalue");
    assert(value == 5);
    assert(scale(4) == 8);
    assert(scale(4, 3) == 12);
}
~~~

`std::move(value)` nie zmienia tu liczby. Umożliwia wybór wersji `int&&`, a ta tylko zwraca opis. Rzeczywisty efekt zależy od ciała wybranej funkcji, nie od samej kategorii argumentu.

## Porównanie i decyzje

Parametr przez wartość jest naturalny dla małych liczb i dla funkcji, która potrzebuje własnej kopii. `const T&` sprawdza się przy odczycie większego obiektu, `T&` przy wymaganej modyfikacji, a wskaźnik lub typ opcjonalny przy dopuszczalnym braku argumentu. Widok na tekst opisuje odczyt znaków lepiej niż wymuszanie konkretnego kontenera.

Unikaj rodzin przeciążeń, które różnią się drobnymi konwersjami liczbowymi o innym znaczeniu. Osobne nazwy operacji lub mocne typy jednostek mogą wyeliminować przypadkowy wybór. Wartość domyślna powinna oznaczać stabilną, zrozumiałą politykę, ponieważ jest powielana w skompilowanych miejscach wywołania.

**Ćwiczenie.** Czy można przeciążyć `int parse(std::string_view)` przez dodanie `double parse(std::string_view)`?

**Odpowiedź.** Nie. Wywołanie nie jest rozstrzygane wyłącznie przez oczekiwany typ wyniku. Potrzebne są różne parametry, różne nazwy lub jawny argument szablonu opisujący żądany typ.

Źródła: [wybór najlepszej funkcji](https://timsong-cpp.github.io/cppwp/n4950/over.match.best), [deklaratory funkcji](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct), [argumenty domyślne](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct.default).

## Powiązane tematy

- [Copy, move i rule of zero](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Szablony funkcji](../05_szablony_i_generycznosc/01_function_i_class_templates.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)

