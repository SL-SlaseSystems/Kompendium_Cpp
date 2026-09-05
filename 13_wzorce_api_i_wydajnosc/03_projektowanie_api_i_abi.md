[← Spis treści](../README.md)

# Projektowanie API i ABI

Publiczne API obejmuje nazwy, typy, preconditions, ownership, błędy, złożoność i zachowanie współbieżne. ABI obejmuje binarną reprezentację: calling convention, layout, name mangling, vtables, wyjątki i runtime. Zgodność źródłowa nie gwarantuje binarnej, a standard C++ nie definiuje uniwersalnego ABI.

~~~cpp
#include <cassert>
#include <limits>
#include <stdexcept>
#include <span>
#include <string>
#include <string_view>
#include <utility>

class Report {
public:
    explicit Report(std::string title) : title_{std::move(title)} {}
    [[nodiscard]] std::string_view title() const & noexcept { return title_; }
    [[nodiscard]] std::string title() && { return std::move(title_); }
    [[nodiscard]] std::string title() const && { return title_; }
    [[nodiscard]] int sum(std::span<const int> values) const {
        int result = 0;
        for (int value : values) {
            if ((value > 0 && result > std::numeric_limits<int>::max() - value) ||
                (value < 0 && result < std::numeric_limits<int>::min() - value)) {
                throw std::overflow_error("sum outside int range");
            }
            result += value;
        }
        return result;
    }

private:
    std::string title_;
};

int main() {
    const Report report{"Q1"};
    const int values[]{20, 22};
    assert(report.title() == "Q1" && report.sum(values) == 42);
}
~~~

Parametr `string` przez wartość jest dobry, gdy obiekt przejmuje dane; klient może skopiować lvalue lub przenieść rvalue. `string_view` jest dobry dla synchronicznego odczytu bez przechowania, a `span` dla ciągłego zakresu. Widok zwracany z lvalue wiąże lifetime z `Report`; wywołanie na rvalue zwraca posiadający napis. Sumowanie sprawdza zakres przed każdym dodaniem i zgłasza `overflow_error`, zamiast dopuszczać signed overflow.

Minimalizuj publiczne zależności i liczbę typów ujawnionych w nagłówku. Dodanie pola private zmienia layout i może złamać ABI klientów; PImpl pomaga, ale nie rozwiązuje wszystkich zmian. Eksport symboli kontroluj atrybutami lub mapą visibility specyficzną dla platformy.

Stabilna granica pluginu często używa C ABI, opaque handles, jawnych wersji struktur i funkcji do tworzenia/niszczenia po tej samej stronie runtime. Nie przenoś standardowych kontenerów ani wyjątków przez granicę kompilatorów o nieustalonym ABI.

## Jak to działa krok po kroku

Projektuj sygnaturę od perspektywy wywołującego. Jeśli operacja tylko czyta tekst podczas wywołania, `string_view` komunikuje tani widok. Jeśli przechowuje tekst po powrocie, musi skopiować dane lub przyjąć ich właściciela. Następnie określ wynik: wartość może żyć niezależnie, ale referencja lub widok wiążą się z czasem życia innego obiektu i jego przyszłymi modyfikacjami.

Dopisz wymagania dotyczące błędu, zakresu danych i współbieżności. `noexcept` mówi o wyjątkach opuszczających funkcję, nie o braku błędów, overflow czy data race. Sygnatura sumująca dowolny zakres `int` wymaga reguły dla wyniku poza zakresem. Publiczny kontrakt powinien pozwolić klientowi spełnić wymagania bez czytania implementacji.

## Pogłębienie mechanizmu

Zgodność źródłowa oznacza możliwość ponownego skompilowania klienta. Zgodność binarna oznacza współpracę istniejących artefaktów w ustalonej konfiguracji. Dodanie przeciążenia może zmienić wybór funkcji lub spowodować niejednoznaczność po rekompilacji. Dodanie prywatnego pola może zachować wywołania źródłowe, ale zmienić rozmiar i przesunięcia w pamięci. „Private” nie oznacza niewidzialności dla ABI.

Domyślne argumenty są używane w miejscu wywołania. Zmiana ich wartości w nagłówku nie musi zmienić zachowania starego klienta bez przebudowania. Podobnie kod inline może pozostawać w istniejących plikach binarnych. Aktualizacja samej biblioteki dynamicznej nie zawsze aktualizuje całą semantykę publicznego API.

Przy granicy pluginów określ właściciela każdej alokacji, wersję interfejsu i sposób przekazywania błędu. `extern "C"` wpływa na language linkage; nie standaryzuje automatycznie layoutu każdej struktury, szerokości typów i konwencji całej platformy. Opaque handle plus funkcja niszcząca po stronie biblioteki ogranicza zależność klienta od jej wewnętrznych klas.

## Drugi przykład

~~~cpp
#include <cassert>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

class Label {
    std::string text_;
public:
    explicit Label(std::string text) : text_{std::move(text)} {}
    std::string_view text() const & noexcept { return text_; }
    std::string text() && { return std::move(text_); }
    std::string text() const && { return text_; }
};

int main() {
    const Label named{"trwaly obiekt"};
    auto view = named.text();
    auto owned = Label{"tymczasowy obiekt"}.text();
    static_assert(std::is_same_v<decltype(view), std::string_view>);
    static_assert(std::is_same_v<decltype(owned), std::string>);
    assert(view == "trwaly obiekt");
    assert(owned == "tymczasowy obiekt");
}
~~~

Wywołanie na lvalue zwraca widok, a na rvalue wartość posiadającą tekst. Osobne `const &&` uwzględnia także niemodyfikowalny obiekt tymczasowy, z którego tekst trzeba skopiować. Ten projekt ogranicza typowy błąd widoku do już zniszczonego tymczasowego właściciela. Nadal można błędnie przechować widok z `named` dłużej niż samo `named`, więc dokumentacja lifetime pozostaje potrzebna.

## Porównanie i decyzje

Dla wewnętrznego API rekompilowanego razem z aplikacją zwykłe typy standardowe często zapewniają najlepszą czytelność. Dla dostarczanej biblioteki binarnej określ wspierane kombinacje kompilatora, biblioteki, flag i platform. Dla granicy procesów użyj formatu komunikacji, a nie zależności od layoutu obiektów w jednym procesie.

Silne typy domenowe, na przykład oddzielne `UserId` i `InvoiceId`, pomagają odrzucić zamianę argumentów, której dwa parametry `uint64_t` nie wykryją. `[[nodiscard]]` przypomina o wyniku wymagającym uwagi, ale zwykle jest mechanizmem diagnostycznym, a nie niemożliwym do obejścia przymusem. Projektuj typy tak, aby prawidłowe użycie było łatwe do zapisania.

## Ćwiczenie z odpowiedzią

Dlaczego `auto text = Report{"Q1"}.title();` jest groźne, jeśli `title` zwraca zawsze `string_view`? Tymczasowy `Report` kończy życie po pełnym wyrażeniu, a `text` przechowuje już tylko widok. Kopia widoku nie kopiuje napisu. Rozwiązaniem jest wartość, zakaz takiego wywołania lub przeciążenia zależne od kategorii obiektu.

Źródło przykładowego, konkretnego ABI: [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html). Jego reguły nie są uniwersalną gwarancją ISO C++.

## Powiązane tematy

- [PImpl](01_rule_of_zero_pimpl_i_non_virtual_interface.md)
- [ABI i visibility](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
