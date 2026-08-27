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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Type erasure, vtables, ABI i visibility”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Value semantics oznacza, że kopia reprezentuje niezależną wartość z przewidywalną równością. Type erasure ukrywa konkretny typ za wspólnym kontraktem przez wskaźnik funkcji, vtable lub mały bufor.
- Vtable i key function są elementami ABI implementacji, nie normatywną reprezentacją standardu. Ukryta visibility zmniejsza publiczną powierzchnię symboli i umożliwia optymalizacje, ale musi być spójna z eksportowanym API.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Type erasure, vtables, ABI i visibility” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Type erasure, vtables, ABI i visibility
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Type erasure, vtables, ABI i visibility”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Value semantics i type erasure](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
- [virtual i RTTI](../04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
- [ODR, moduły i FFI](13_odr_moduly_ffi_i_interoperacyjnosc.md)
