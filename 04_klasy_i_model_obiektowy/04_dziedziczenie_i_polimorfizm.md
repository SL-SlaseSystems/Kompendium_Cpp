[← Spis treści](../README.md)

# Dziedziczenie i polimorfizm

Publiczne dziedziczenie modeluje relację „jest rodzajem” (*is-a*) i zachowuje kontrakt klasy bazowej. Prywatne dziedziczenie jest techniką implementacyjną, lecz kompozycja zwykle wyraża zależność czytelniej. Wielokrotne i wirtualne dziedziczenie istnieją, ale wymagają szczególnej ostrożności wobec layoutu, inicjalizacji i niejednoznaczności.

~~~cpp
#include <cassert>
#include <memory>

struct Shape {
    virtual ~Shape() = default;
    [[nodiscard]] virtual double area() const = 0;
};

class Rectangle final : public Shape {
public:
    Rectangle(double width, double height) : width_{width}, height_{height} {}
    [[nodiscard]] double area() const override { return width_ * height_; }

private:
    double width_;
    double height_;
};

int main() {
    std::unique_ptr<Shape> shape = std::make_unique<Rectangle>(3.0, 4.0);
    assert(shape->area() == 12.0);
}
~~~

Funkcja czysto wirtualna `= 0` czyni klasę abstrakcyjną. Wywołanie przez wskaźnik lub referencję do bazy wybiera override dynamicznie. Przechowywanie obiektu pochodnego przez wartość typu bazowego powoduje *object slicing*: część pochodna zostaje utracona. Polimorfizm runtime wymaga więc zwykle referencji albo wskaźnika.

Liskov Substitution Principle wymaga czegoś więcej niż poprawnej składni: typ pochodny nie powinien wzmacniać preconditions, osłabiać postconditions ani łamać inwariantów bazy. Jeśli warianty mają zamknięty zbiór i wspólne operacje, `std::variant` może być prostszą alternatywą bez hierarchii i alokacji.

## Jak to działa krok po kroku

Obiekt pochodny zawiera podobiekt bazowy. Konwersja `Rectangle*` do dostępnego, jednoznacznego `Shape*` daje dostęp do tej części interfejsu. Adres wskaźnika może wymagać dostosowania, szczególnie przy wielokrotnym dziedziczeniu. Nie należy zastępować takiej konwersji reinterpretacją bajtów tylko dlatego, że w prostym eksperymencie liczby adresów były identyczne.

W początkowym programie fabryka konstruuje `Rectangle`. `unique_ptr<Shape>` przejmuje odpowiedzialność i używa wskaźnika do bazy. Przy wywołaniu `area` typ statyczny określa dostępny interfejs, a typ dynamiczny prowadzi do implementacji `Rectangle::area`. Podczas usuwania wirtualny destruktor zapewnia rozpoczęcie sprzątania od typu najbardziej pochodnego.

Przekazanie obiektu pochodnego przez wartość parametru bazowego tworzy jednak osobny obiekt bazy. Nie jest to drugi widok na cały oryginał. Część pochodna nie trafia do parametru, a jego typ dynamiczny jest bazą. Taki slicing nie występuje przy zwykłym przekazaniu referencji do bazy, która nadal odnosi się do podobiektu w oryginalnym obiekcie.

## Pogłębienie mechanizmu

Publiczne dziedziczenie udostępnia konwersję „pochodny do bazowego” odbiorcom interfejsu. Dziedziczenie prywatne i chronione zmienia dostępność tej konwersji i elementów odziedziczonych; nie usuwa fizycznej relacji podobiektów. Nie należy mylić poziomu dostępu do metody z wirtualnością: prywatną funkcję wirtualną nadal można nadpisać, choć nie można jej dowolnie wywołać z zewnątrz.

Przy zwykłym diamencie dwie ścieżki dziedziczenia tworzą dwa podobiekty wspólnej bazy. Konwersja do tej bazy może być niejednoznaczna. Dziedziczenie wirtualne pozwala współdzielić jeden podobiekt tej bazy, którego inicjalizację wykonuje klasa najbardziej pochodna. Rozwiązuje to konkretny problem współdzielonej tożsamości, ale komplikuje konstrukcję i zwykle reprezentację. Nie jest synonimem wirtualnych metod.

Klasa abstrakcyjna nie może być tworzona jako kompletny obiekt, ale jej podobiekt może istnieć wewnątrz typu pochodnego. Funkcja czysto wirtualna może mieć definicję, a czysto wirtualny destruktor musi ją mieć, ponieważ bierze udział w sprzątaniu baz. Oznaczenie `= 0` opisuje abstrakcyjny kontrakt, nie zawsze brak jakiegokolwiek ciała.

Podstawialność obejmuje zachowanie, a nie tylko typy. Jeżeli baza obiecuje zapis dowolnego poprawnego dokumentu, pochodna odrzucająca część tych dokumentów bez przewidzianego sposobu błędu łamie kontrakt. Jeśli baza zapewnia, że operacja nie rzuca, override nie może poluzować specyfikatora wyjątków. Inne wymagania semantyczne, takie jak zachowanie stanu po niepowodzeniu, trzeba uzgodnić w dokumentacji i testach.

Wirtualne wywołanie nie wymaga dynamicznej alokacji. Lokalny obiekt pochodny przekazany przez referencję również zachowuje polimorfizm. Alokacja jest zwykle potrzebna wtedy, gdy różne typy muszą być przechowywane pod wspólnym właścicielem o niezależnym czasie życia. To osobna decyzja od wyboru dispatchu.

## Drugi przykład

Dwie funkcje przyjmują tę samą rodzinę typów w różny sposób. Wersja przez wartość tworzy bazę, a wersja referencyjna zachowuje dynamiczny typ źródła.

~~~cpp
#include <cassert>
#include <string_view>

struct Device {
    virtual ~Device() = default;
    virtual std::string_view name() const { return "device"; }
};
struct Sensor : Device {
    std::string_view name() const override { return "sensor"; }
};

std::string_view by_value(Device device) { return device.name(); }
std::string_view by_reference(const Device& device) { return device.name(); }

int main() {
    Sensor sensor;
    assert(by_value(sensor) == "device");
    assert(by_reference(sensor) == "sensor");
    const Device& base = sensor;
    assert(base.name() == "sensor");
}
~~~

Program nie alokuje obiektu przez `new`. Różnica wynika wyłącznie z konstrukcji parametru i rodzaju dostępu. W realnym interfejsie często warto zapobiegać przypadkowemu kopiowaniu bazy polimorficznej, na przykład ograniczając dostęp do jej operacji kopiowania.

## Porównanie i decyzje

Własność polimorficznego obiektu i możliwość jego skopiowania trzeba zaprojektować oddzielnie. Wirtualna funkcja `clone` może zwracać nowy `unique_ptr<Base>` zachowujący właściwy typ dynamiczny. Samo kopiowanie wskaźnika daje jedynie kolejnego obserwatora, a kopiowanie `shared_ptr` kolejnego współwłaściciela tego samego obiektu. Żadna z tych operacji nie jest automatycznie głęboką kopią pochodnej wartości.

Używaj kompozycji, kiedy obiekt korzysta z innego obiektu jako części implementacji. Wybierz publiczną hierarchię, gdy odbiorcy mają operować przez stabilny wspólny kontrakt, a nowe typy mogą dochodzić niezależnie. Dla zamkniętego zestawu wariantów `variant` umożliwia jawne, wyczerpujące rozpatrywanie typów. Szablony nadają się, gdy wybór typu jest znany podczas kompilacji i nie potrzebujesz wspólnego runtime'owego magazynu.

**Ćwiczenie.** Czy `std::vector<Base>` przechowa pełne obiekty `Derived`, jeżeli wywołasz `push_back` z obiektem pochodnym?

**Odpowiedź.** Nie. Elementami tego kontenera są obiekty `Base`, więc nastąpi konstrukcja wartości bazowej i slicing. Dla otwartej hierarchii można użyć wektora właścicieli `unique_ptr<Base>`, a dla znanego zestawu typów wektora odpowiedniego `variant`.

Źródła: [klasy pochodne](https://timsong-cpp.github.io/cppwp/n4950/class.derived), [klasy abstrakcyjne](https://timsong-cpp.github.io/cppwp/n4950/class.abstract), [funkcje wirtualne](https://timsong-cpp.github.io/cppwp/n4950/class.virtual).

## Powiązane tematy

- [virtual, override i RTTI](05_virtual_override_i_rtti.md)
- [enum, union i variant](06_enum_union_i_variant.md)
- [Type erasure i vtables](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

