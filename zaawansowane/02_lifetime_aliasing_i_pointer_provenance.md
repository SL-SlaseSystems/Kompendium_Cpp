[← Spis treści](../README.md)

# Lifetime, aliasing i pointer provenance

Adres pamięci nie wystarcza do legalnego dostępu. Musi istnieć żywy obiekt właściwego typu, pointer musi spełniać alignment, a operacja musi respektować reguły aliasowania. Pointer provenance opisuje związek wskaźnika z obiektem i storage, z którego pochodzi; formalny model jest rozwijany i nie powinien być upraszczany do „wskaźnik to liczba”.

~~~cpp
#include <cassert>
#include <cstddef>
#include <memory>
#include <new>

struct Value {
    int number;
};

int main() {
    alignas(Value) unsigned char storage[sizeof(Value)];
    Value* value = std::construct_at(reinterpret_cast<Value*>(storage), Value{42});
    assert(value->number == 42);
    std::destroy_at(value);
}
~~~

Przykład ręcznie rozpoczyna i kończy lifetime w odpowiednio wyrównanym storage. `reinterpret_cast` sam nie konstruuje obiektu. W kodzie aplikacyjnym lepszy jest zwykły obiekt lub kontener; ten wzorzec należy do implementacji alokatorów i struktur o ręcznym storage.

Type-accessible glvalue może odczytać obiekt przez dozwolony typ, m.in. zgodny typ, odpowiednio cv-qualified, odpowiadający signed/unsigned lub typ znakowy/`std::byte` w określonych operacjach reprezentacji. Naruszenie reguł daje UB i pozwala optimizerowi zakładać brak pewnych aliasów.

`std::launder` nie jest uniwersalnym „napraw wskaźnik”. Ma wąskie zastosowanie po utworzeniu nowego obiektu w tym samym storage, gdy stary pointer nie może automatycznie wskazywać nowego obiektu z powodu reguł transparent replacement. Najpierw zrozum dokładny lifetime.

Konwersja pointer–integer–pointer ma implementacyjne i standardowe ograniczenia; operacje na liczbie mogą utracić związek wymagany przez model implementacji. Do przesunięć wewnątrz obiektu używaj reguł pointer arithmetic i `std::byte`, nie arbitralnej arytmetyki adresów.

## Jak to działa krok po kroku

W pierwszym przykładzie tablica zapewnia rozmiar i wyrównanie dla `Value`. Rzutowanie uzyskuje wskaźnik odpowiedniego typu, lecz operacją tworzącą obiekt jest `construct_at`. Jego wynik odnosi się do nowo utworzonego obiektu; dlatego właśnie ten wynik zapisujemy i dereferencjonujemy. `destroy_at` kończy lifetime `Value`, natomiast sama tablica nadal istnieje do końca zakresu. Nie wywołujemy `delete`, ponieważ pamięć nie pochodzi z odpowiadającego mu wyrażenia `new`.

Oddziel trzy pytania: czy bajty są dostępne, czy istnieje w nich obiekt i czy dane wyrażenie może odczytywać jego wartość. Alokator może udostępnić pamięć dla stu elementów, choć kontener skonstruował tylko trzy. Dostęp do czwartego elementu nie staje się legalny przez samo odpowiednie `capacity()`. Z kolei odczyt reprezentacji żywego obiektu przez `unsigned char` nie jest zwykłym dostępem do wartości przez dowolny obcy typ.

## Pogłębienie mechanizmu

C++23 dopuszcza niejawne tworzenie obiektów typów implicit-lifetime w pewnych operacjach, na przykład przy określonych alokacjach lub kopiowaniu pamięci. Nie oznacza to, że każdy zapis przez dowolny wskaźnik rozpoczyna lifetime każdego typu. `std::string` potrzebuje właściwej konstrukcji. Nawet utworzenie obiektu klasy implicit-lifetime nie musi rozpocząć życia podobiektów, które same nie należą do tej kategorii. W kodzie kontenera jawne `construct_at` często daje prostszy, łatwiejszy do sprawdzenia model.

Reguły type accessibility pozwalają oglądać reprezentację przez `char`, `unsigned char` oraz `std::byte`. Nie należy automatycznie dopisywać do tej listy `signed char`. Zgodność rozmiarów `int` i `float` także nie pozwala odczytać jednego przez referencję do drugiego. `memcpy` albo `bit_cast` przekazuje reprezentację bez tworzenia niedozwolonego aliasu, ale nadal trzeba wykazać poprawność reprezentacji docelowej.

Transparent replacement powoduje, że stare nazwy, referencje i wskaźniki mogą zacząć oznaczać nowy obiekt po zastąpieniu starego. W C++23 wymagania obejmują ten sam typ z pominięciem najwyższego cv, dokładne nałożenie storage oraz ograniczenia dotyczące obiektów const i potencjalnie nakładających się podobiektów. Baza klasy i pole `[[no_unique_address]]` wymagają szczególnej ostrożności. Nie stosuj uproszczonej reguły „ten sam adres, więc ten sam obiekt”.

`std::launder` wymaga istniejącego obiektu odpowiedniego typu pod danym adresem i spełnienia ograniczeń osiągalności bajtów. Nie tworzy obiektu, nie usuwa const, nie wyrównuje adresu i nie legalizuje use-after-free. Wskaźnik zwrócony bezpośrednio przez placement new zwykle oszczędza konieczności rozważania prania starego wskaźnika. Konwersja przez liczbę całkowitą także nie zastępuje tych reguł; `uintptr_t` jest opcjonalny, a ogólny model provenance nie sprowadza się do matematyki adresów.

## Drugi przykład

~~~cpp
#include <cassert>
#include <cstddef>
#include <memory>
#include <new>
#include <string>

int main() {
    alignas(std::string) std::byte bytes[sizeof(std::string)];
    auto* text = std::construct_at(
        reinterpret_cast<std::string*>(bytes), "pierwszy");
    assert(*text == "pierwszy");
    std::destroy_at(text);
    text = std::construct_at(
        reinterpret_cast<std::string*>(bytes), "drugi");
    assert(*text == "drugi");
    std::destroy_at(text);
}
~~~

Pierwszy destruktor zwalnia zasoby napisu, ale pozostawia zewnętrzny storage. Druga konstrukcja tworzy odrębny obiekt w tych samych bajtach. W obu przypadkach korzystamy z aktualnego wyniku `construct_at`. To demonstracja mechanizmu, nie kompletny kontener: jeśli pomiędzy konstrukcją a destrukcją dodasz operację rzucającą wyjątek, potrzebny będzie strażnik RAII wywołujący destruktor przy rozwijaniu stosu.

## Porównanie i decyzje

Wybieraj `variant` lub `optional`, gdy potrzebujesz zmiany aktywnego stanu o znanym zestawie typów. Implementacje tych klas rozwiązują już problemy wyrównania, wyjątków i liczby skonstruowanych obiektów. Surowe storage ma uzasadnienie przy pisaniu kontenera, areny, interfejsu sprzętowego lub wąskiej warstwy interoperacyjności. Dokumentuj wówczas dokładnie moment uzyskania i oddania własności; nie wymagaj od każdego klienta ponownego dowodzenia lifetime.

**Ćwiczenie.** Czy po `destroy_at(text)` wolno sprawdzić `text->empty()` przed drugą konstrukcją? **Odpowiedź:** nie, żywy `std::string` już nie istnieje. Czy samo wyzerowanie tablicy bajtów skonstruuje pusty napis? Również nie; poprawny stan bibliotecznego typu powstaje przez jego konstruktor, a reprezentacja nie jest publicznym kontraktem. Czy trzeba użyć `launder` w drugim przykładzie? Nie: zapisujemy wskaźnik uzyskany z nowej konstrukcji.

Reguły wersji bazowej opisują [N4950: lifetime](https://timsong-cpp.github.io/cppwp/n4950/basic.life), [type accessibility](https://timsong-cpp.github.io/cppwp/n4950/basic.lval) i [launder](https://timsong-cpp.github.io/cppwp/n4950/ptr.launder).

### Arytmetyka wskaźników i granice obiektu

Wskaźnik one-past-the-end można tworzyć i porównywać w odpowiednich operacjach, lecz nie wolno go dereferencjonować. Arytmetyka wskaźników odnosi się do elementów tej samej tablicy; sąsiedztwo dwóch niezależnych alokacji nie scala ich w jedną tablicę. Odejmowanie wskaźników do różnych takich obiektów nie jest przenośnym sposobem wyznaczania fizycznej odległości w pamięci. Układ sąsiednich elementów trzeba odróżniać od przypadkowego układu przydziałów alokatora.

Przedłużenie życia tymczasowego obiektu przez referencję zależy od konkretnego sposobu wiązania. Przekazanie tej samej referencji dalej przez funkcję nie uruchamia przedłużenia ponownie. `const auto& ref = make_value()` może mieć inną sytuację niż referencja zwrócona z funkcji przyjmującej tymczasowy argument. Typ referencji w obu miejscach wygląda podobnie, ale to pełne wyrażenie i kontekst inicjalizacji wyznaczają rzeczywisty koniec życia.

W projektowaniu niskopoziomowym rysuj osobno lifetime storage, obiektu i widoków. Kontener może nadal istnieć po realokacji, ale wszystkie stare wskaźniki do jego elementów mogą już wisieć. Z kolei przeniesienie właściciela pamięci nie zawsze przenosi same obiekty; ich adres może pozostać stabilny, choć zmienia się obiekt odpowiedzialny za późniejsze zniszczenie.

## Powiązane tematy

- [Storage duration i lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Layout i alignment](03_layout_alignment_padding_i_triviality.md)
- [Alokatory](04_allocatory_pmr_i_new_delete.md)

