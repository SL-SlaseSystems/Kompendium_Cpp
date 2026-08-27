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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Architektura i dependency injection”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz ustanowienie kontraktu typu, rozdzielenie interfejsu od implementacji, wykonanie operacji i zmierzenie kosztu na granicy abstrakcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie domenowe od mechanizmu implementacyjnego, publiczne ABI od prywatnego layoutu i hipotezę wydajności od pomiaru. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź przykładowe użycie API, rozmiar i layout typu, symbole biblioteki, profil CPU oraz liczbę alokacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projektowanie C++ łączy semantykę wartości, własność, stabilność ABI i koszt abstrakcji. Dobra abstrakcja utrudnia niewłaściwe użycie, ale pozostawia kompilatorowi wystarczającą informację do optymalizacji. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Dependency injection przekazuje zależność przez konstruktor lub funkcję zamiast wybierać globalny singleton wewnątrz logiki. Interfejs może być konceptem, wartością funkcyjną albo polimorficzną bazą zależnie od potrzeb kompilacji i runtime.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Architektura i dependency injection” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Architektura i dependency injection
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Architektura i dependency injection”, oceniaj łatwość poprawnego użycia, value semantics, stabilność kontraktu, koszt kompilacji i zmierzona wydajność krytycznej ścieżki. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Testy jednostkowe](../09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
- [Value semantics i type erasure](02_value_semantics_i_type_erasure.md)
- [Dziedziczenie](../04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)

