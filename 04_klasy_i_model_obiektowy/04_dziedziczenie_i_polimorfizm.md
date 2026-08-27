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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Dziedziczenie i polimorfizm”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Publiczne dziedziczenie modeluje relację podstawienia, a nie tylko ponowne użycie kodu. Kompozycja jest bezpieczniejsza, gdy typ pochodny nie potrafi zachować kontraktu klasy bazowej.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Dziedziczenie i polimorfizm” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Dziedziczenie i polimorfizm
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Dziedziczenie i polimorfizm”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Dodawaj `override` do każdej implementacji funkcji wirtualnej; kompilator wykryje różnicę sygnatur. `final` zamyka klasę lub konkretny override. Nie wywołuj funkcji wirtualnych w konstruktorach z oczekiwaniem dispatchu do klasy pochodnej.

## Powiązane tematy

- [virtual, override i RTTI](05_virtual_override_i_rtti.md)
- [enum, union i variant](06_enum_union_i_variant.md)
- [Type erasure i vtables](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

