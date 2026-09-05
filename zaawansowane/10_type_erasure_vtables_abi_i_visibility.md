[← Spis treści](../README.md)

# Type erasure, vtables, ABI i visibility

Type erasure przechowuje wartość konkretnego typu za jednolitym interfejsem runtime. Implementacja zwykle zawiera storage oraz tablicę funkcji wykonujących destroy, move, copy i operacje domenowe. `std::function`, `std::any` i wiele bibliotekowych wrapperów korzysta z odmian tego wzorca.

~~~cpp
#include <cassert>
#include <memory>
#include <utility>

class AnyArea {
    struct Interface {
        virtual ~Interface() = default;
        virtual double area() const = 0;
        virtual std::unique_ptr<Interface> clone() const = 0;
    };

    template<class T>
    struct Model final : Interface {
        explicit Model(T value) : value_{std::move(value)} {}
        double area() const override { return value_.area(); }
        std::unique_ptr<Interface> clone() const override {
            return std::make_unique<Model>(*this);
        }
        T value_;
    };

public:
    template<class T>
    AnyArea(T value) : self_{std::make_unique<Model<T>>(std::move(value))} {}
    AnyArea(const AnyArea& other) : self_{other.self_->clone()} {}
    AnyArea(AnyArea&&) noexcept = default;
    AnyArea& operator=(AnyArea other) noexcept { self_.swap(other.self_); return *this; }
    double area() const { return self_->area(); }

private:
    std::unique_ptr<Interface> self_;
};

struct Square { double side; double area() const { return side * side; } };

int main() {
    AnyArea shape = Square{3.0};
    assert(shape.area() == 9.0);
}
~~~

Ten prosty erasure używa wirtualnej hierarchii wewnętrznej i alokuje każdy model. Produkcyjna wersja może dodać small-buffer optimization, move-only wariant i tabelę zwykłych function pointers. Każda optymalizacja komplikuje alignment, exception safety oraz reguły aktywnego obiektu.

Vtable, vptr, name mangling i układ baz są elementami ABI implementacji, nie wymaganym mechanizmem standardu. Itanium C++ ABI jest używany przez wiele systemów uniksowych, a MSVC ma inny model. Nawet przy tym samym ABI flagi, wersja runtime i biblioteka standardowa mogą zmieniać zgodność.

Visibility ogranicza eksport symboli z shared library. Ukrycie implementacyjnych nazw zmniejsza tablice dynamiczne i powierzchnię ABI, ale wymaga atrybutów lub opcji platformowych. Publiczne wyjątki, RTTI i inline templates również wpływają na granicę.

## Jak to działa krok po kroku

Konstruktor `AnyArea` dedukuje `Square`, tworzy `Model<Square>` i zapisuje wskaźnik do interfejsu. Konkretna wartość nadal istnieje; wymazany został jedynie jej typ z publicznego interfejsu wrappera. `shape.area()` przekazuje wywołanie przez interfejs do implementacji modelu, która zna `Square` i wywołuje jego zwykłą metodę. Użytkownik `Square` nie musi dziedziczyć po bibliotecznej klasie bazowej.

Kopia wrappera wywołuje `clone`, tworząc nowy model i kopiując wartość. Dzięki temu dwie kopie nie współdzielą ukradkiem mutowalnego obiektu. Przeniesienie `unique_ptr` przekazuje własność modelu bez kopiowania `Square`. Przypisanie przez wartość przygotowuje kopię lub przeniesienie przed wejściem do ciała, a następnie wykonuje niezgłaszający wyjątków swap. Wyjątek przy tworzeniu parametru nie zmienia dotychczasowej wartości obiektu docelowego.

## Pogłębienie mechanizmu

Type erasure musi określić pełny zestaw operacji, nie tylko wywołanie domenowe. Potrzebuje zniszczenia, odpowiedniego przeniesienia, opcjonalnego kopiowania i zwykle reprezentacji pustego stanu. W przykładzie obiekt po przeniesieniu ma pusty `self_`; wywołanie na nim `area()` lub kopiowanie bez obsługi pustki byłoby błędem. Uproszczony kontrakt dopuszcza po przeniesieniu destrukcję i ponowne przypisanie; produkcyjna klasa może jawnie obsłużyć pusty stan lub zabronić takich operacji warunkiem wstępnym.

Small-buffer optimization przechowuje małe modele wewnątrz wrappera. Warunkiem nie jest sam rozmiar: potrzebne jest dostateczne wyrównanie oraz odpowiednia gwarancja przenoszenia, jeżeli wrapper obiecuje `noexcept` move. Model duży, nadmiernie wyrównany albo potencjalnie rzucający podczas przenoszenia może wymagać alokacji. Zamiana aktywnej reprezentacji lokalnej i dynamicznej musi poprawnie zarządzać lifetime; bytewise swap nie działa dla każdego modelu.

Tablica wskaźników do funkcji i klasy wirtualne to dwie implementacje podobnej abstrakcji. Standard określa zachowanie virtual dispatch, ale nie wymaga fizycznego vptr na początku obiektu ani konkretnego formatu vtable. Dziedziczenie wielokrotne może wymagać korekt adresu `this`, a kompilator może zdevirtualizować wywołanie, gdy zna dynamiczny typ. Liczba odczytów pamięci w pojedynczym ABI nie jest przenośną miarą kosztu C++.

ABI obejmuje również sposób zwracania wartości, przekazywania argumentów, rozwijania stosu przy wyjątkach, identyfikacji RTTI i alokacji. Ukrycie prywatnych symboli nie usuwa zależności od ABI typów występujących w sygnaturze. `std::function<void()>` może mieć odmienny layout w libc++ i libstdc++; przekazywanie go przez granicę niezależnie budowanych pluginów wymaga uzgodnionego toolchainu. PIMPL ogranicza zmiany reprezentacji klasy, ale nie ustanawia automatycznej zgodności między kompilatorami.

## Drugi przykład

~~~cpp
#include <cassert>
#include <functional>

struct Counter {
    int value = 0;
    int operator()() { return ++value; }
};
int main() {
    std::function<int()> first = Counter{};
    auto second = first;
    assert(first() == 1);
    assert(first() == 2);
    assert(second() == 1);
    int shared = 0;
    std::function<int()> borrowed = [&shared] { return ++shared; };
    auto another = borrowed;
    assert(borrowed() == 1 && another() == 2);
}
~~~

Pierwsze kopiowanie kopiuje obiekt `Counter`, więc liczniki rozwijają się niezależnie. Drugie kopiuje lambdę zawierającą referencję, więc oba wrappery odnoszą się do tego samego `shared`. Wymazanie typu nie zmienia semantyki kopiowania ani własności modelu. Obiekt przechowujący callable przez wartość może nadal zawierać pożyczone referencje, których lifetime należy zabezpieczyć osobno.

## Porównanie i decyzje

`variant` sprawdza się przy zamkniętej liście typów i pozwala odwiedzać wszystkie alternatywy. Type erasure pozwala przyjmować nowe typy bez rozszerzania listy, ale zamyka zestaw dostępnych operacji w interfejsie. Szablon zachowuje konkretny typ i możliwości inliningu kosztem instancjacji oraz zależności kompilacyjnych. Wybór dotyczy miejsca, w którym ma przebiegać granica abstrakcji, a nie ogólnej wyższości jednej techniki.

**Ćwiczenie.** Czy skopiowanie `std::function` gwarantuje niezależność zasobów używanych przez funkcję? **Odpowiedź:** kopiuje callable, którego pola mogą współdzielić zasoby albo referencje. Czy typ z `unique_ptr` może być zwykłym celem kopiowalnego `std::function`? Zwykle nie spełnia wymagań kopiowalności; C++23 oferuje `move_only_function` dla odpowiedniego kontraktu. Pusty stan i wywołanie pustego wrappera mają różne reguły w tych dwóch klasach.

Źródła: [N4950: function wrappers](https://timsong-cpp.github.io/cppwp/n4950/func.wrap) oraz [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html).

### Pożyczone i posiadające wymazanie typu

Nie każdy wrapper wymazujący typ musi posiadać model. Widok funkcji może przechowywać wskaźnik do istniejącego callable i wskaźnik do funkcji pośredniczącej. Unika alokacji i kopiowania modelu, ale wymaga, aby callable przeżył wszystkie wywołania widoku. Przekazanie takiego widoku do synchronicznego algorytmu jest inną umową niż zapisanie go jako callbacka wykonywanego później. Rozróżnienie powinno być widoczne w nazwie i dokumentacji typu.

Własny wrapper kopiowalny powinien ograniczać konstruktor do modeli spełniających jego wymagania. Inaczej próba przechowania modelu move-only ujawni błąd dopiero wewnątrz implementacji `clone`. Concept może sprawdzić kopiowanie i typ wyniku `area`, ale nie dowiedzie semantycznie, że powierzchnia jest nieujemna lub nie zmienia modelu. Te własności pozostają kontraktem domenowym.

Na granicy biblioteki dynamicznej funkcje pośredniczące mogą znajdować się w kodzie pluginu. Nawet gdy model pozostaje w żywej pamięci, wyładowanie biblioteki usuwa kod potrzebny do wywołania lub zniszczenia wrappera. Zasada lifetime obejmuje zatem także moduł z kodem implementacji. Menedżer pluginów musi utrzymać bibliotekę załadowaną tak długo, jak istnieją zależne od niej modele.

Koszt wymazania typu warto rozbić na utworzenie wrappera, wywołanie i zniszczenie. Alokacja modelu może dominować w krótkim zadaniu, natomiast w wielokrotnie uruchamianym kosztownym callbacku narzut pojedynczego pośredniego wywołania może być nieistotny. Benchmark mierzący tylko puste wywołania nie odpowiada automatycznie zachowaniu rzeczywistego obciążenia aplikacji.

## Powiązane tematy

- [Value semantics i type erasure](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
- [virtual i RTTI](../04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
- [ODR, moduły i FFI](13_odr_moduly_ffi_i_interoperacyjnosc.md)
