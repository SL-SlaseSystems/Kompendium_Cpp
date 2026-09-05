[← Spis treści](../README.md)

# Architektura i dependency injection

Dependency injection oznacza dostarczenie zależności z zewnątrz zamiast tworzenia ich głęboko w logice. W C++ zależność może być wartością, referencją do interfejsu, template parametrem albo funkcją. Wybór dynamicznego lub statycznego polimorfizmu powinien wynikać z granicy zmienności, nie z mody.

~~~cpp
#include <cassert>
#include <string>
#include <string_view>

struct Logger {
    virtual ~Logger() = default;
    virtual void write(std::string_view message) = 0;
};

class Service {
public:
    explicit Service(Logger& logger) : logger_{logger} {}
    void run() { logger_.write("run"); }

private:
    Logger& logger_; // niewłaścicielska; logger musi żyć dłużej
};

class RecordingLogger final : public Logger {
public:
    void write(std::string_view message) override { last = message; }
    std::string last;
};

int main() {
    RecordingLogger logger;
    Service service{logger};
    service.run();
    assert(logger.last == "run");
}
~~~

Composition root tworzy konkretne zależności i składa aplikację w jednym miejscu, zwykle blisko `main`. Logika domenowa zna abstrakcje, nie system konfiguracji. Referencja jasno komunikuje brak null i niewłasność, ale wymaga stabilnego lifetime. `unique_ptr<Interface>` oznacza przejęcie własności, a `shared_ptr` tylko rzeczywiście współdzielone życie.

Template injection usuwa virtual dispatch i ułatwia optymalizację, lecz może zwiększać kompilację oraz sprzężenie nagłówków. Type erasure zachowuje wartość i runtime wybór. Funkcja lub lambda jest często najprostszą zależnością dla pojedynczej operacji.

Nie twórz interfejsu dla każdej klasy. Oddzielaj granice I/O, czasu, losowości i usług zewnętrznych, ponieważ zmieniają się lub utrudniają testy. Wewnętrzne, stabilne obliczenia mogą pozostać zwykłymi typami wartościowymi.

## Jak to działa krok po kroku

W pierwszym programie `RecordingLogger` powstaje przed `Service`. Serwis przechowuje referencję, więc nie tworzy ani nie niszczy loggera. `run()` wywołuje operację interfejsu, a dynamiczny typ wybiera zapis do pamięci testu. Po zakończeniu `main` obiekty są niszczone w odwrotnej kolejności, co odpowiada zależności lifetime.

W większej aplikacji rozrysuj graf zależności. Właściciele powinni powstawać przed obserwatorami, a zakończenie operacji asynchronicznych powinno nastąpić przed zniszczeniem usług, z których korzystają. Composition root jest miejscem składania tych zależności. Jeśli obiekt sam pobiera wszystko z globalnego rejestru, jego konstruktor przestaje ujawniać rzeczywiste wymagania.

## Pogłębienie mechanizmu

Dependency injection nie wymaga kontenera DI ani dziedziczenia. Parametr funkcji może dostarczyć źródło czasu, a wartość obiektu funkcyjnego politykę przeliczania. Wirtualny interfejs jest przydatny, gdy implementacje trzeba wybierać podczas wykonania. Szablon pasuje, gdy wybór jest znany przy kompilacji. Referencja do konkretnego typu również jest wstrzyknięciem zależności, jeśli wywołujący ją dostarcza.

Ważna jest granica efektów. Obliczenie ceny na podstawie danych może być zwykłą funkcją, a pobieranie kursu z sieci osobną zależnością. Test obliczenia nie potrzebuje wtedy uruchamiania klienta HTTP. Nie oznacza to rezygnacji z testów integracyjnych: adapter sieciowy nadal trzeba sprawdzić względem rzeczywistego protokołu.

Fake zwracający kontrolowane dane pozwala sprawdzić wynik, podczas gdy mock często weryfikuje sekwencję interakcji. Nadmierne sprawdzanie wewnętrznej kolejności wywołań może utrudnić poprawne refaktoryzacje. Testuj tę sekwencję tylko wtedy, gdy sama stanowi wymaganie, na przykład zatwierdzenie po udanym zapisie, a nie przed nim.

## Drugi przykład

~~~cpp
#include <cassert>
#include <chrono>
#include <utility>

using Clock = std::chrono::steady_clock;

template<class Now>
class Deadline {
    Now now_;
    Clock::time_point end_;
public:
    Deadline(Now now, Clock::duration timeout)
        : now_{std::move(now)}, end_{now_() + timeout} {}
    bool expired() const { return now_() >= end_; }
};

int main() {
    using namespace std::chrono_literals;
    auto current = Clock::time_point{};
    Deadline deadline{[&current] { return current; }, 5s};
    assert(!deadline.expired());
    current += 4999ms;
    assert(!deadline.expired());
    current += 1ms;
    assert(deadline.expired());
}
~~~

Test kontroluje czas przez referencję do lokalnej wartości i nie usypia wątku. Granica jest jawna: termin jest przekroczony także przy równości. Lambda oraz `current` żyją przez cały okres użycia `Deadline`. W kodzie aplikacji tę samą rolę może pełnić lambda zwracająca `steady_clock::now()`. Szablon nie narzuca globalnego mechanizmu konfiguracji czasu.

## Porównanie i decyzje

Przekazanie przez wartość daje serwisowi własną zależność, referencja zapewnia obserwację obiektu żyjącego gdzie indziej, a `unique_ptr` przekazuje wyłączną własność. `shared_ptr` ma sens wtedy, gdy różni uczestnicy rzeczywiście ustalają wspólny koniec życia. Jego użycie do każdej zależności może ukryć cykle i uniemożliwić przewidywalną kolejność sprzątania.

Interfejs powinien opisywać potrzebę klienta. Jeżeli serwis potrzebuje jedynie odczytu bieżącego czasu, nie wstrzykuj ogromnego obiektu aplikacji zawierającego sieć, bazę i konfigurację. Mała zależność ogranicza sprzężenie i liczbę stanów testu. Jednocześnie nie rozbijaj stabilnej funkcji matematycznej na sztuczne interfejsy wyłącznie dla formalnej zgodności ze wzorcem.

## Ćwiczenie z odpowiedzią

Czy zastąpienie lambdy `[&current]` przez `[current]` zachowa działanie testu? Nie: kopia będzie stale zwracać początkowy czas, więc zmiany zewnętrznej zmiennej przestaną wpływać na deadline. Czy użycie referencji zawsze jest lepsze? Nie, bo wymaga dostatecznie długiego życia `current`. Dobór własności wynika z zamierzonego zachowania, a nie nazwy wzorca.

Dodatkowe kryteria projektowania interfejsów i zarządzania zasobami: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Przykład pokazuje jedną możliwą architekturę, nie obowiązkowy model języka.

## Powiązane tematy

- [Testy jednostkowe](../09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
- [Value semantics i type erasure](02_value_semantics_i_type_erasure.md)
- [Dziedziczenie](../04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)

