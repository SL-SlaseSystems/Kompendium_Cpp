[← Spis treści](../README.md)

# Funkcje specjalne i operatory

Funkcje specjalne sterują domyślną konstrukcją, kopiowaniem, przenoszeniem i destrukcją. Kompilator może je zadeklarować automatycznie, lecz zależności między regułami są subtelne. Najprostszy projekt korzysta z rule of zero: pola same mają poprawną semantykę wartości, więc klasa nie pisze ręcznie żadnej z pięciu operacji zasobowych.

~~~cpp
#include <cassert>
#include <compare>

class Point {
public:
    Point(int x, int y) : x_{x}, y_{y} {}

    Point operator+(const Point& other) const {
        return {x_ + other.x_, y_ + other.y_};
    }

    auto operator<=>(const Point&) const = default;

    [[nodiscard]] int x() const noexcept { return x_; }
    [[nodiscard]] int y() const noexcept { return y_; }

private:
    int x_;
    int y_;
};

int main() {
    const Point result = Point{1, 2} + Point{3, 4};
    assert((result == Point{4, 6}));
}
~~~

Przeciążony operator powinien zachowywać intuicję operatora. `+` zwykle nie zmienia operandów i zwraca wartość, `+=` modyfikuje lewy operand i zwraca `*this`. Nie można zmienić priorytetu, łączności ani liczby operandów operatora. Co najmniej jeden operand musi mieć typ klasowy lub enum.

Domyślne `operator<=>` może wygenerować porównania leksykograficzne pól, a `operator==` zostaje odpowiednio dostarczony. Semantyka pola musi jednak odpowiadać tożsamości logicznej typu. Nie generuj porównania z przypadkowego cache lub uchwytu implementacyjnego.

Assignment powinien obsługiwać samoprzypisanie zgodnie z kontraktem. Idiom copy-and-swap bywa prosty i bezpieczny wyjątkowo, ale może wprowadzić zbędny koszt. Najpierw wykorzystaj poprawne operacje pól, a ręczną optymalizację poprzyj pomiarem.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Funkcje specjalne i operatory”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Zadeklarowanie części funkcji specjalnych wpływa na automatyczne generowanie pozostałych. Przeciążony operator powinien zachowywać oczekiwaną semantykę, a operatory symetryczne często korzystają z nieczłonkowskiej funkcji lub hidden friend.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Funkcje specjalne i operatory” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Funkcje specjalne i operatory
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Funkcje specjalne i operatory”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
- [Value semantics](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
