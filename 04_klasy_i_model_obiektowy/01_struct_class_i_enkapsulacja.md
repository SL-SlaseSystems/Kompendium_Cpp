[← Spis treści](../README.md)

# struct, class i enkapsulacja

`struct` i `class` definiują ten sam rodzaj typu klasowego. Różnią się domyślnym dostępem: w `struct` elementy i dziedziczenie są publiczne, w `class` prywatne. Konwencja często używa `struct` dla prostych agregatów i `class` dla typu chroniącego inwariant, ale język nie narzuca takiego podziału.

~~~cpp
#include <cassert>
#include <stdexcept>

class Percentage {
public:
    explicit Percentage(int value) : value_{value} {
        if (value < 0 || value > 100) {
            throw std::out_of_range{"percentage"};
        }
    }

    [[nodiscard]] int value() const noexcept {
        return value_;
    }

private:
    int value_;
};

int main() {
    const Percentage progress{75};
    assert(progress.value() == 75);
}
~~~

Prywatne pole nie jest celem samym w sobie. Enkapsulacja pozwala utrzymać inwariant i zmieniać reprezentację bez zmiany publicznego kontraktu. Konstruktor weryfikuje zakres, a metoda `value()` gwarantuje odczyt poprawnej wartości. `explicit` blokuje przypadkową konwersję z `int`.

Metoda z końcowym `const` ogranicza modyfikację niestatycznych pól przez `this`; logiczna niezmienność jest dodatkowym kontraktem projektu. Nie oznacza automatycznej thread safety. Element `mutable` może być modyfikowany w metodzie const, co jest użyteczne dla cache lub mutexa, ale nie powinno służyć omijaniu projektu typu.

Publiczne pola są rozsądne w pasywnym agregacie, który nie ma ukrytego inwariantu. Mechaniczne gettery i settery dla każdego pola nie zapewniają znaczącej enkapsulacji. Projektuj operacje domenowe, które utrzymują poprawny stan.

## Jak to działa krok po kroku

Klasa definiuje reprezentację i zbiór operacji, które wolno wykonywać na obiekcie. W przykładzie `Percentage` wejściowy `int` jest najpierw używany do inicjalizacji pola. Następnie konstruktor sprawdza zakres. Jeżeli wartość jest niepoprawna, wyjątek uniemożliwia ukończenie konstrukcji. Wywołujący nie otrzymuje więc poprawnie skonstruowanego `Percentage` z wartością spoza dopuszczalnego przedziału.

Po pomyślnej konstrukcji metoda `value()` jedynie odczytuje pole. Nie ma metody zwracającej modyfikowalne `int&`, dzięki której odbiorca mógłby ominąć kontrolę. Samo oznaczenie pola jako `private` nie wystarczyłoby, gdyby publiczny getter oddawał nieograniczony zapis do tego pola. Enkapsulację ocenia się po możliwościach całego interfejsu.

`explicit` zapobiega użyciu konstruktora jako przypadkowej konwersji niejawnej. `Percentage{75}` jasno sygnalizuje stworzenie nowego rodzaju wartości, a funkcja oczekująca `Percentage` nie przyjmie po prostu dowolnego `int` przez taką konwersję. Jest to szczególnie użyteczne, kiedy kilka liczb ma to samo przedstawienie, lecz inne znaczenie, na przykład procent, indeks i identyfikator.

## Pogłębienie mechanizmu

Kontrola dostępu działa podczas kompilacji i dotyczy deklaracji. Metoda klasy może odczytywać prywatne pola innego obiektu tej samej klasy; `private` nie oznacza „dostępne wyłącznie przez ten konkretny egzemplarz”. Przyjaźń `friend` udostępnia wybranej funkcji lub klasie dostęp do reprezentacji. Nie jest automatycznie wzajemna, dziedziczona ani przechodnia. Może służyć dobrze kontrolowanej współpracy, na przykład implementacji operatora porównania.

Metoda z końcowym `const` otrzymuje dostęp przez `this` do stałego obiektu i nie może zwyczajnie zmieniać jego niestatycznych pól, poza `mutable`. To reguła typów, a nie dowód braku skutków ubocznych: metoda może modyfikować zmienną globalną lub obiekt wskazywany przez pole wskaźnikowe. Logiczna stałość oznacza silniejszą umowę, którą projektant powinien utrzymywać. Cache w `mutable` powinien zachowywać obserwowalne wyniki i uwzględniać synchronizację.

Agregat umożliwia inicjalizację swoich elementów bez wywoływania zwykłego konstruktora użytkownika. W C++23 ograniczenia agregatu obejmują między innymi brak konstruktorów deklarowanych przez użytkownika, brak prywatnych i chronionych bezpośrednich pól oraz brak funkcji wirtualnych. Samo słowo `struct` nie gwarantuje agregatowości. Dopisanie `Point() = default` jako deklaracji konstruktora może odebrać ten status.

Designated initializers od C++20 pozwalają zapisać `Point{.x = 1, .y = 2}` dla odpowiedniego agregatu. W C++ oznaczenia muszą odpowiadać kolejności deklaracji pól; nie jest to dowolne przestawianie nazw znane z niektórych innych języków. Pominięte pola są inicjalizowane według reguł agregatu i ewentualnych inicjalizatorów domyślnych.

Prywatność nie ukrywa fizycznej reprezentacji przed kompilacją klienta, jeżeli definicja klasy znajduje się w publicznym nagłówku. Dodanie pola może zmienić rozmiar i ABI. Jeśli wymagane jest oddzielenie reprezentacji binarnej, potrzebna jest dodatkowa technika, na przykład PImpl. To inne wymaganie niż kontrola dozwolonych operacji w kodzie źródłowym.

## Drugi przykład

Operacja domenowa chroni zależność między wartościami lepiej niż dwa niezależne settery. Przedział nigdy nie zmienia granic w taki sposób, który pozostawia go odwróconym.

~~~cpp
#include <cassert>
#include <stdexcept>

class Interval {
    int low_;
    int high_;
public:
    Interval(int low, int high) : low_{low}, high_{high} {
        if (low > high) throw std::invalid_argument{"reversed interval"};
    }
    bool contains(int value) const noexcept {
        return low_ <= value && value <= high_;
    }
    void replace(int low, int high) {
        if (low > high) throw std::invalid_argument{"reversed interval"};
        low_ = low;
        high_ = high;
    }
};

int main() {
    Interval interval{2, 8};
    try {
        interval.replace(10, 3);
    } catch (const std::invalid_argument&) {
        assert(interval.contains(5));
    }
    interval.replace(4, 6);
    assert(!interval.contains(3));
}
~~~

Sprawdzenie obu nowych granic następuje przed pierwszą zmianą. Ponieważ przypisania `int` nie rzucają, nieudana operacja pozostawia poprzedni przedział. Gdyby pola były bardziej złożonymi typami, należałoby ponownie przeanalizować możliwość wyjątku między przypisaniami.

## Porównanie i decyzje

Wybieraj agregat z publicznymi polami dla niezależnych danych o prostym znaczeniu. Wybieraj klasę chroniącą reprezentację, gdy poprawność wymaga zależności między polami lub kontrolowanych przejść stanu. Nazwij operację zgodnie z działaniem użytkownika, zamiast automatycznie generować getter i setter dla każdej składowej.

**Ćwiczenie.** Czy `class` ze wszystkimi polami publicznymi jest zawsze lepiej enkapsulowany niż `struct` z prywatnymi polami i kontrolowanymi metodami?

**Odpowiedź.** Nie. Po jawnej deklaracji poziomów dostępu oba słowa dają te same możliwości. O ochronie inwariantu decydują dozwolone operacje, a nie domyślny dostęp wybranego słowa kluczowego.

Źródła: [kontrola dostępu](https://timsong-cpp.github.io/cppwp/n4950/class.access), [agregaty](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.aggr), [przyjaźń](https://timsong-cpp.github.io/cppwp/n4950/class.friend).

## Powiązane tematy

- [Konstruktory i destruktory](02_konstruktory_i_destruktory.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
- [Assertions i preconditions](../07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)

