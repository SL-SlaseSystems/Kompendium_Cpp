[← Spis treści](../README.md)

# Rule of zero, PImpl i Non-Virtual Interface

Rule of zero mówi, że klasa aplikacyjna nie powinna ręcznie zarządzać zasobem, jeśli może przechować gotowy typ RAII. Automatycznie generowane copy/move/destrukcja zachowują wtedy semantykę pól. Kod jest krótszy, a exception safety wynika z kompozycji.

PImpl (*pointer to implementation*) przenosi prywatną reprezentację do niekompletnego typu za `unique_ptr`. Zmniejsza zależności nagłówka i może ograniczyć część zmian ABI, ale dodaje alokację, indirection, kod boilerplate oraz konieczność zdefiniowania destruktora tam, gdzie implementacja jest kompletna.

~~~cpp
#include <cassert>
#include <limits>
#include <stdexcept>

class Processor {
public:
    int process(int value) {
        validate(value);
        return do_process(value);
    }

    virtual ~Processor() = default;

private:
    static void validate(int value) {
        if (value < 0 || value > std::numeric_limits<int>::max() / 2) {
            throw std::out_of_range("value outside supported range");
        }
    }
    virtual int do_process(int value) = 0;
};

class Doubler final : public Processor {
private:
    int do_process(int value) override { return value * 2; }
};

int main() {
    Doubler doubler;
    assert(doubler.process(21) == 42);
}
~~~

Non-Virtual Interface (NVI) udostępnia publiczną niewirtualną metodę pilnującą kontraktu i wywołuje private/protected virtual customization point. Dzięki temu walidacja, logowanie i inwariant nie są duplikowane przez klasy pochodne. NVI nie jest potrzebny w każdej hierarchii; proste interface-only base może mieć publiczne pure virtual metody.

## Jak to działa krok po kroku

Najpierw oddziel odpowiedzialność domenową od własności zasobu. Klasa opisująca dokument powinna przechowywać `string` i `vector`, a nie samodzielnie odtwarzać ich alokację i kopiowanie. Jeżeli potrzebujesz ukryć reprezentację przed klientem biblioteki, umieść ją w osobnej klasie implementacyjnej i pozostaw w publicznej klasie właściciela tej implementacji.

Przy PImpl deklaracja zagnieżdżonego `Impl` wystarcza, aby zadeklarować `unique_ptr<Impl>`. Domyślny deleter wymaga jednak kompletnego typu tam, gdzie realizowane jest usuwanie. Dlatego definicję destruktora umieszcza się w pliku implementacji po definicji `Impl`. W praktyce także konstruktor i odpowiednie operacje przenoszenia definiuj w miejscu z pełną reprezentacją, aby ścieżki sprzątania były poprawne.

W NVI wywołanie klienta trafia najpierw do niewirtualnego interfejsu. Ten sprawdza dane i wspólne warunki, a dopiero potem wywołuje wirtualny etap specjalistyczny. Klasa pochodna dostarcza operację, ale nie omija normalną drogą kontroli na wejściu.

## Pogłębienie mechanizmu

Rule of zero nie jest nakazem bezwzględnego braku destruktorów. Wrapper PImpl często potrzebuje jawnej deklaracji destruktora dla niekompletnego typu. To z kolei wpływa na automatyczne generowanie operacji przenoszenia. Jeśli typ ma być move-only, zadeklaruj ten kontrakt świadomie i sprawdź, czy użytkownik może legalnie przechowywać go w kontenerze.

PImpl nie zapewnia głębokiej kopii automatycznie. `unique_ptr` usuwa kopiowanie; jeśli obiekt domenowy ma być kopiowalny, musisz określić, jak skopiować `Impl` oraz jak zachować gwarancję wyjątków przypisania. Zmiana właściciela na `shared_ptr` zmienia semantykę na współdzielenie i nie jest neutralnym sposobem przywrócenia kopiowalności.

PImpl ogranicza zależności reprezentacji i może zachować rozmiar publicznej klasy przy zmianach prywatnych pól implementacji. Nie stabilizuje sam z siebie nazw eksportowanych funkcji, konwencji wywołania, polityki wyjątków ani ABI standardowego typu użytego w sygnaturze. Stabilność binarna wymaga określonego środowiska i zakresu dozwolonych zmian.

## Drugi przykład

Poniżej część deklaracyjna i implementacyjna znajdują się w jednej jednostce, aby przykład można było skompilować samodzielnie. W projekcie rozdziela się je na nagłówek i plik `.cpp`.

~~~cpp
#include <cassert>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

class Widget {
    struct Impl;
    std::unique_ptr<Impl> impl_;
public:
    explicit Widget(std::string label);
    ~Widget();
    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;
    Widget(const Widget&) = delete;
    Widget& operator=(const Widget&) = delete;
    std::string label() const;
};

struct Widget::Impl { std::string label; };
Widget::Widget(std::string label) : impl_{std::make_unique<Impl>(Impl{std::move(label)})} {}
Widget::~Widget() = default;
Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;
std::string Widget::label() const {
    if (!impl_) throw std::logic_error("Widget bez implementacji po przeniesieniu");
    return impl_->label;
}

int main() {
    Widget first{"panel"};
    Widget second{std::move(first)};
    assert(second.label() == "panel");
    first = Widget{"odtworzony"};
    assert(first.label() == "odtworzony");
}
~~~

Po przeniesieniu `first` może być zniszczony i przypisany ponownie. Wywołanie `label` ma jawnie określony błąd dla pustej implementacji. Zwracanie napisu przez wartość usuwa zależność czasu życia wyniku od `Widget`, kosztem możliwej kopii.

## Porównanie i decyzje

Stosuj rule of zero w typach wartościowych, PImpl na granicy wymagającej ukrycia reprezentacji, a NVI tam, gdzie rozszerzenia mają przechodzić przez wspólny kontrakt. To trzy rozwiązania różnych problemów; nie trzeba wprowadzać ich jednocześnie do każdej klasy. Dla małej struktury punktu dwuwymiarowego PImpl zwykle zwiększa koszt i złożoność bez istotnej korzyści.

Wirtualny customization point może rzucać albo otrzymać dodatkowe ograniczenia. Wspólny wrapper musi określać także stan obiektu po błędzie, a nie tylko wykonywać walidację przed wywołaniem. Wywoływanie wirtualnego etapu z konstruktora nie uruchamia automatycznie zachowania jeszcze nieskonstruowanej części pochodnej.

## Ćwiczenie z odpowiedzią

Dlaczego domyślne `= default` przy destruktorze w publicznym nagłówku może sprawiać problem z PImpl? Jego instancjacja może wymagać wywołania deletera, gdy `Impl` jest nadal niekompletne. Sama możliwość zadeklarowania wskaźnika do niekompletnego typu nie dowodzi możliwości usunięcia wskazywanego obiektu w tym miejscu.

Źródło wymagań deletera: [C++23, default_delete](https://timsong-cpp.github.io/cppwp/n4950/unique.ptr.dltr.dflt). Idiomy projektowe nie są odrębnymi słowami kluczowymi języka.

## Powiązane tematy

- [Copy, move i rule of zero](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [virtual i RTTI](../04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
- [Projektowanie API i ABI](03_projektowanie_api_i_abi.md)

