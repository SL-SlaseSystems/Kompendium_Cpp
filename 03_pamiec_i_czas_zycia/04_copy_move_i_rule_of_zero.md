[← Spis treści](../README.md)

# Copy, move i rule of zero

C++ ma semantykę wartości: obiekt można kopiować, przenosić, przypisywać i niszczyć zgodnie z jego funkcjami specjalnymi. Kopiowanie typu wartościowego powinno zachowywać jego logiczną wartość; niektóre typy, na przykład `shared_ptr`, świadomie kopiują udział w zasobie. Przeniesienie może przejąć zasoby ze źródła, a dopuszczalny stan źródła określa kontrakt typu.

~~~cpp
#include <cassert>
#include <string>
#include <utility>
#include <vector>

struct Document {
    std::string title;
    std::vector<int> pages;
};

int main() {
    Document original{"Guide", {1, 2, 3}};
    Document copy = original;
    Document moved = std::move(original);

    assert(copy.title == "Guide");
    assert(moved.pages.size() == 3);
    original = Document{}; // obiekt nadal można przypisać
}
~~~

`std::move` niczego sam nie przenosi; wykonuje rzutowanie do xvalue, umożliwiając wybór przeciążenia przyjmującego rvalue. Jeśli typ lub kontekst nie oferuje ruchu, może nadal nastąpić kopia. Nie czytaj stanu moved-from poza operacjami dozwolonymi przez kontrakt.

*Rule of zero* mówi, by zasoby reprezentować elementami, które same zarządzają swoim lifetime. Wtedy kompilator może wygenerować poprawne copy/move/destrukcję. Jeśli klasa bezpośrednio posiada surowy zasób i musi definiować destruktor, zwykle trzeba świadomie rozważyć pięć funkcji: copy constructor, copy assignment, move constructor, move assignment i destructor — to rule of five.

Zadeklarowanie niektórych funkcji specjalnych wpływa na automatyczne generowanie pozostałych. `= default` jawnie prosi o domyślne zachowanie, a `= delete` zakazuje operacji. Konstruktor przenoszący oznaczony `noexcept` pozwala kontenerom częściej przenosić elementy podczas realokacji z zachowaniem silnej gwarancji wyjątków.

## Jak to działa krok po kroku

Deklaracja `Document copy = original` tworzy nowy obiekt przez konstruktor kopiujący. Nie jest przypisaniem tylko dlatego, że zawiera znak równości. Domyślne kopiowanie klasy kopiuje kolejno bazy i pola. `string` tworzy własną wartość napisu, a `vector` kopiuje elementy do własnego bufora. Dzięki temu późniejsza modyfikacja treści kopii nie zmienia treści oryginału.

W `Document moved = std::move(original)` rzutowanie dostarcza xvalue, a rozstrzyganie przeciążeń może wybrać konstruktor przenoszący. Domyślny ruch klasy przenosi jej podobiekty zgodnie z ich własnymi operacjami. Dla `string` i `vector` może to oznaczać przejęcie bufora; dla pola `int` ruch zwykle ma taki sam efekt jak kopia. To nie jest mechaniczne przeniesienie wszystkich bajtów całej klasy.

Przypisanie działa na obiekcie, który już istnieje. Musi uwzględnić jego dotychczasowe zasoby. Konstruktor tworzy nową tożsamość obiektu, natomiast operator przypisania zmienia stan istniejącej. Ta różnica ma znaczenie dla referencji, stałych pól, gwarancji wyjątków i samoprzypisania. Destruktor kończy odpowiedzialność za aktualny stan, bez względu na to, ile wcześniejszych przypisań wykonano.

## Pogłębienie mechanizmu

Domyślny ruch nie jest automatycznie deklarowany, gdy klasa ma deklarowany przez użytkownika destruktor, konstruktor kopiujący, operator kopiujący albo operację ruchu. Nawet `~T() = default;` jest deklaracją użytkownika istotną dla tych reguł. Z kolei zadeklarowanie operacji ruchu może spowodować usunięcie domyślnych operacji kopiowania. Zawsze patrz na cały zestaw funkcji specjalnych, nie na pojedynczą dopisaną metodę.

Nie każdy typ musi być kopiowalny. Klasa zawierająca `unique_ptr` i bez ręcznych funkcji specjalnych naturalnie jest przenoszalna, ale niekopiowalna. To też rule of zero: kompilator wyprowadza zakaz kopiowania z odpowiedzialności pola. Gdy potrzebna jest kopia logiczna, trzeba określić, czy oznacza klonowanie zasobu, współdzielenie, czy nową tożsamość.

`std::move` zachowuje kwalifikację `const`. Ze stałego `string` otrzymujemy `const string&&`, które zwykle nie pasuje do konstruktora `string(string&&)`. Pozostaje konstruktor kopiujący przyjmujący `const string&`. Dodanie `std::move` nie dowodzi więc ani braku kopiowania, ani poprawy wydajności. Również `is_move_constructible` bada możliwość konstrukcji z rvalue, którą może spełnić konstruktor kopiujący.

Od C++17 zwracanie prvalue tego samego typu, na przykład `return T{...};`, może konstruować bezpośrednio obiekt wynikowy bez wymogu dostępnego kopiowania lub ruchu. Zwrócenie nazwanej lokalnej zmiennej umożliwia NRVO, ale go nie gwarantuje. `return std::move(local);` zwykle odbiera tę możliwość. Najczęściej pisz `return local;` i pozwól regułom zwrotu dobrać właściwe zachowanie.

`noexcept` ruchu pomaga kontenerom utrzymać gwarancje podczas przenoszenia elementów do nowego bufora. Jeśli ruch może rzucać, a kopia jest dostępna, wektor może kopiować. Dla niekopiowalnego typu z rzucającym ruchem niektóre operacje mają słabsze gwarancje. Deklarowanie nieprawdziwego `noexcept` zamienia wyjątek w zakończenie programu, więc nie jest bezpłatną optymalizacją.

## Drugi przykład

Właściciel pojedynczego zasobu nie potrzebuje żadnej ręcznej funkcji specjalnej. Dostępność operacji wynika z `unique_ptr`, a przeniesione źródło ma tu konkretnie zagwarantowany stan pusty.

~~~cpp
#include <cassert>
#include <memory>
#include <type_traits>
#include <utility>

struct Job {
    std::unique_ptr<int> payload;
};

int main() {
    static_assert(!std::is_copy_constructible_v<Job>);
    static_assert(std::is_nothrow_move_constructible_v<Job>);
    Job first{std::make_unique<int>(42)};
    Job second = std::move(first);
    assert(first.payload == nullptr);
    assert(*second.payload == 42);
    first = Job{std::make_unique<int>(9)};
    assert(*first.payload == 9);
}
~~~

## Porównanie i decyzje

Nie narzucaj zasady „po ruchu wszystko jest puste” dowolnym klasom. Standardowe typy biblioteczne zwykle gwarantują stan ważny, ale nieokreślony, o ile nie podano mocniejszego warunku; własny typ wymaga własnego kontraktu. Dla `unique_ptr` pustość po zwykłej konstrukcji przenoszącej jest określona. Dla dowolnego typu należy sprawdzić, które operacje mają spełnione preconditions.

**Ćwiczenie.** Klasa ma `std::vector<int>` jako jedyne pole. Dopisano destruktor tylko po to, aby wypisać komunikat. Czy automatycznie zachowała taki sam zestaw operacji ruchu?

**Odpowiedź.** Nie. Deklaracja destruktora blokuje domyślne deklarowanie ruchu. Konstrukcja z rvalue może nadal działać przez kopiowanie. Należy usunąć zbędny destruktor albo świadomie zadeklarować potrzebne operacje i sprawdzić ich semantykę, zamiast wnioskować z samej kompilowalności wywołania.

Źródła: [konstrukcja kopiująca i przenosząca](https://timsong-cpp.github.io/cppwp/n4950/class.copy.ctor), [eliminacja kopiowania](https://timsong-cpp.github.io/cppwp/n4950/class.copy.elision), [stan po przeniesieniu biblioteki](https://timsong-cpp.github.io/cppwp/n4950/lib.types.movedfrom).

## Powiązane tematy

- [Funkcje specjalne](../04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
- [Value categories i forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Rule of zero i PImpl](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)

