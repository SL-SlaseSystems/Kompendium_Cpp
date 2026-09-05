[← Spis treści](../README.md)

# Layout, alignment, padding i triviality

`sizeof(T)` obejmuje storage obiektu wraz z paddingiem, a `alignof(T)` wymagane wyrównanie. Kolejność i rozmiar paddingu zależą od implementacji z wyjątkiem konkretnych gwarancji standardu. Nie serializuj obiektu przez zapis `sizeof(T)` bajtów: padding może mieć nieokreśloną zawartość, a reprezentacja zależy od ABI i endianess.

~~~cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <type_traits>

struct PacketHeader {
    std::uint32_t length;
    std::uint16_t kind;
    std::uint16_t flags;
};

int main() {
    static_assert(std::is_standard_layout_v<PacketHeader>);
    static_assert(std::is_trivially_copyable_v<PacketHeader>);
    assert(alignof(PacketHeader) >= alignof(std::uint32_t));
    assert(offsetof(PacketHeader, length) == 0);
}
~~~

Standard-layout daje ograniczone gwarancje interoperacyjności i layoutu, a trivially copyable pozwala kopiować reprezentację do tablicy `char`, `unsigned char` lub `std::byte` i z powrotem zgodnie z regułami. Nadal nie gwarantuje przenośnego formatu pliku.

`alignas` może zwiększyć wymagane wyrównanie obiektu. Over-aligned typy wymagają dopasowanej alokacji; współczesne `new` obsługuje aligned allocation, ale własne alokatory muszą propagować wymagania. `std::assume_aligned` jest obietnicą dla optymalizatora, nie runtime checkiem.

`[[no_unique_address]]` pozwala, by potencjalnie pusty element współdzielił adres z innymi danymi, lecz dokładny layout pozostaje zależny od implementacji. Empty Base Optimization także jest używany do kompresji policy objects.

`std::bit_cast` kopiuje reprezentację między trivially copyable typami o tym samym rozmiarze i jest bezpieczniejszy od aliasowania przez `reinterpret_cast`. Nie gwarantuje jednak, że każdy wzorzec bitów reprezentuje prawidłową wartość typu docelowego ani że wynik jest przenośnym formatem danych.

## Jak to działa krok po kroku

Kompilator wyznacza układ `PacketHeader`, uwzględniając wymagania pól i całego obiektu. Pierwsze pole obiektu standard-layout leży na jego początku; stąd poprawna asercja z `offsetof`. Pozostałe przesunięcia mogą zawierać padding. Końcowy padding pozwala tworzyć tablicę, w której każdy następny obiekt zaczyna się pod odpowiednio wyrównanym adresem. Rozmiar obiektu i liczba znaczących bajtów jego danych nie są zatem tym samym.

Trait `is_standard_layout` mówi o kategorii układu, a `is_trivially_copyable` o dozwolonych operacjach na reprezentacji. Te własności są niezależnymi pytaniami. Typ z prywatnymi polami może być trivially copyable, a typ z nietrywialnym konstruktorem inicjalizującym wartości może nadal mieć trywialne kopiowanie. Nie zastępuj zestawu potrzebnych własności historycznym, szerokim słowem POD.

## Pogłębienie mechanizmu

Dla obiektu trivially copyable, który nie jest potentially-overlapping subobject, można zapisać jego bajty do tablicy odpowiedniego typu znakowego lub `std::byte`, a następnie odtworzyć je, odzyskując pierwotną wartość. Podobnie kopiowanie reprezentacji między odrębnymi obiektami tego samego typu ma określone gwarancje. Nie wynika stąd legalność surowego kopiowania `std::string`: skopiowane wewnętrzne wskaźniki mogłyby spowodować podwójne zwolnienie pamięci.

`memcmp` nie jest ogólną implementacją równości obiektów. Dwie wartości mogą mieć różny padding, a wartości zmiennoprzecinkowe wymagają szczególnej semantyki dla zera i NaN. Nawet trait `has_unique_object_representations` nie ustanawia formatu sieciowego ani trwałości wskaźników po ponownym uruchomieniu programu. Serializacja powinna opisywać znaczenie pól, szerokości, kolejność bajtów i walidację wejścia, zamiast kopiować obraz procesu.

`alignas(64)` podnosi wymaganie wyrównania, jeśli implementacja obsługuje taką wartość. Nie dowodzi, że rozmiar linii cache wynosi 64 bajty, ani że dwa pola znajdą się w różnych liniach. ABI może umieszczać dodatkowe dane w klasach polimorficznych, a wynik `sizeof` zmieni się po dodaniu funkcji wirtualnej. Taką zmianę traktuj jako potencjalne zerwanie binarnej zgodności, nawet gdy publiczne nazwy metod pozostały identyczne.

Pole `[[no_unique_address]]` jest potentially-overlapping subobject, również gdy nie jest puste. Implementacja może wykorzystywać jego tail padding do przechowywania innych danych. Nie wolno zatem bez dodatkowego dowodu kopiować `sizeof(pole)` bajtów takiego podobiektu jak niezależnego kompletnego obiektu. Dwa puste podobiekty tego samego typu podlegają ponadto ograniczeniom tożsamości adresów; atrybut nie obiecuje zawsze zerowego kosztu przestrzennego.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <type_traits>

struct Reading { int channel; double value; };
int main() {
    static_assert(std::is_trivially_copyable_v<Reading>);
    Reading source{3, 4.5};
    std::array<std::byte, sizeof(Reading)> saved{};
    std::memcpy(saved.data(), &source, sizeof source);
    source = {9, 1.0};
    std::memcpy(&source, saved.data(), sizeof source);
    assert(source.channel == 3 && source.value == 4.5);
}
~~~

Najpierw kopiujemy reprezentację żywego obiektu do tablicy bajtów. Następnie zmieniamy jego pola zwykłym przypisaniem, a na końcu odtwarzamy dokładnie zapisane bajty. Kod nie interpretuje paddingu i nie przesyła danych na inną platformę. Nie zakłada też konkretnego `sizeof(Reading)`; rozmiar jest obliczony dla bieżącej implementacji. Gwarancja dotyczy odzyskania wartości w tym kontrolowanym scenariuszu.

## Porównanie i decyzje

Przestawienie pól od największego do najmniejszego często zmniejsza padding, ale najpierw sprawdź raport układu i rzeczywisty rozmiar. W interfejsie publicznym taka zmiana może zmieniać offsety i ABI. W kodzie obliczeniowym osobne tablice pól mogą dać większą korzyść niż minimalizacja `sizeof` pojedynczego obiektu. Rozmiar nie mierzy liczby transferów cache potrzebnych przez konkretny algorytm.

**Ćwiczenie.** Czy `static_assert(sizeof(Header) == 8)` udowadnia przenośność protokołu? **Odpowiedź:** sprawdza jedynie rozmiar w bieżącej konfiguracji. Nie sprawdza kolejności bajtów, znaczenia bitów ani poprawności wszystkich reprezentacji. Czy packed struct rozwiązuje problem? Atrybut pakowania jest rozszerzeniem i może tworzyć niewyrównane pola; nadal nie ustala endianowości ani stabilności typów. Format bajtowy należy zdefiniować niezależnie od układu obiektu.

Źródła: [N4950: reprezentacja typów](https://timsong-cpp.github.io/cppwp/n4950/basic.types), [alignment](https://timsong-cpp.github.io/cppwp/n4950/basic.align) i [bit_cast](https://timsong-cpp.github.io/cppwp/n4950/bit.cast).

### Układ klasy a ewolucja interfejsu

Dodanie nawet pustego pola może zmienić rozmiar klasy, jej alignment lub klasyfikację przekazywania argumentów w ABI. Publiczna funkcja przyjmująca taką klasę przez wartość może wtedy wymagać innego kodu wywołania. Sprawdzanie wyłącznie listy eksportowanych symboli nie ujawni całej zmiany. Zestaw testów zgodności powinien obejmować reprezentację typów, sygnatury i scenariusz współpracy starego klienta z nową biblioteką.

C++23 wzmacnia określone gwarancje kolejności niestatycznych składowych, ale nie gwarantuje braku przerw między polami ani identycznego układu dla różnych kompilatorów. `offsetof` jest najprostszy do przenośnego użycia dla standard-layout; jego stosowanie do innych klas jest conditionally-supported. Dziedziczenie wirtualne i funkcje wirtualne powinny od razu skłaniać do konsultacji konkretnego ABI, zamiast obliczania offsetów z intuicji.

Jeśli aplikacja wymaga konkretnego rozmiaru ramki sieciowej, utwórz tablicę bajtów tego rozmiaru i jawnie koduj pola. Wtedy test rozmiaru sprawdza format, a nie przypadkowy układ klasy. Wewnętrzna klasa może korzystać z wygodnych typów i dodatkowych inwariantów, a adapter formatu odpowiada za obcięcie, zakres i endianowość każdego pola.

Bit-fields wymagają osobnej analizy: implementacja określa szczegóły przydziału i rozmieszczenia bitów, a pól bitowych nie można adresować jak zwykłych składowych. Nie stanowią więc przenośnego sposobu opisania bitów w pakiecie. Jawne maski i przesunięcia na typach unsigned lepiej oddzielają znaczenie protokołu od layoutu kompilatora.

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [FFI i interoperacyjność](13_odr_moduly_ffi_i_interoperacyjnosc.md)
- [SIMD i cache](14_simd_wektoryzacja_cache_i_optymalizacja.md)
