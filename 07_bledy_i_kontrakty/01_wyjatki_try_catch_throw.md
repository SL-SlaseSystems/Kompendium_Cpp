[← Spis treści](../README.md)

# Wyjątki: try, catch i throw

Wyjątek oddziela zwykły wynik od rzadkiej ścieżki błędu. `throw` tworzy obiekt wyjątku, a wykonanie szuka pasującego `catch`, rozwijając stos i niszcząc kompletne obiekty automatyczne po drodze. Jeśli nie znajdzie handlera, program kończy się przez `std::terminate`.

~~~cpp
#include <cassert>
#include <stdexcept>
#include <string_view>

int parse_port(std::string_view text) {
    if (text == "80") {
        return 80;
    }
    throw std::invalid_argument{"nieobsługiwany port"};
}

int main() {
    try {
        (void)parse_port("abc");
        return 1;
    } catch (const std::invalid_argument& error) {
        assert(std::string_view{error.what()} == "nieobsługiwany port");
    }
}
~~~

Łap wyjątki przez `const&`, aby uniknąć kopii i object slicing. Handlery są sprawdzane w kolejności, więc typy bardziej szczegółowe umieszczaj przed bazowym `std::exception`. `catch (...)` łapie dowolny wyjątek, ale powinien zwykle posprzątać, zalogować na granicy procesu albo ponownie rzucić przez `throw;`.

Wyjątki są odpowiednie, gdy funkcja nie może spełnić zwykłego kontraktu, a błąd ma propagować przez wiele warstw. Nie są dobrym zamiennikiem normalnego rozgałęzienia, np. „nie znaleziono elementu” w częstej ścieżce. Projekty bez wyjątków wymagają konsekwentnej alternatywy i muszą uwzględnić, że wiele elementów standardowej biblioteki może rzucać.

Nie rzucaj wskaźników ani typów niekopiowalnych. Hierarchia błędów powinna przenosić stabilną informację, a nie zmuszać klienta do parsowania tekstu `what()`. Na granicy API używanego przez kod C przechwytuj wyjątki i tłumacz je na uzgodniony wynik. Samo `extern "C"` nie jest specyfikacją `noexcept`, ale obcy kod nie zapewnia przenośnego protokołu obsługi wyjątków C++.

## Jak to działa krok po kroku

Wywołanie `parse_port("abc")` nie zwraca wartości zastępczej. `throw` inicjalizuje obiekt wyjątku, a dalsze instrukcje tej ścieżki zostają pominięte. Mechanizm obsługi szuka najbliższego dynamicznie otaczającego handlera z pasującym typem. Nie musi on znajdować się w tej samej funkcji: może otaczać wywołanie kilka poziomów wyżej. Dopasowanie wyjątków nie jest zwykłym overload resolution i nie wykonuje dowolnych konwersji definiowanych przez użytkownika.

Po znalezieniu handlera opuszczane zakresy sprzątają skonstruowane obiekty automatyczne w odwrotnej kolejności zakończenia konstrukcji. To właśnie pozwala `unique_ptr`, kontenerom i strażnikom blokad działać bez powtarzania cleanup w każdej gałęzi. Jeżeli konstruktor obiektu rzuci, destruktor tego nieukończonego obiektu nie zostanie wywołany; zostaną jednak zniszczone jego już skonstruowane pola i klasy bazowe. Surowy uchwyt pozyskany w ciele konstruktora bez osłony RAII może wtedy wyciec.

Handler działa już po sprzątnięciu opuszczonych zakresów. Po jego normalnym zakończeniu sterowanie przechodzi za cały blok `try` z handlerami, a nie wraca do instrukcji, która rzuciła. Wyjątki nie są mechanizmem wznowienia przerwanej operacji. Ponowienie wymaga jawnej pętli i stanu, dla którego operacja może być bezpiecznie wykonana ponownie.

## Pogłębienie mechanizmu

`throw;` ponownie zgłasza aktualnie obsługiwany obiekt wyjątku, zachowując jego dynamiczny typ. `throw error;`, gdy `error` ma typ referencji do klasy bazowej, tworzy nowy wyjątek z wyrażenia o statycznym typie bazowym i może obciąć część pochodną. Samo `throw;` bez aktywnego wyjątku wywołuje `terminate`. Referencja uzyskana w `catch` nie jest trwałym wynikiem: nie zachowuj jej po zakończeniu obsługi bez mechanizmu posiadającego obiekt wyjątku.

Do przechowania i późniejszego ponownego zgłoszenia służą `exception_ptr`, `current_exception` oraz `rethrow_exception`. To między innymi podstawa przekazywania błędu przez future. Wyjątek rzucony w funkcji startowej wątku nie trafia sam do `catch` wokół utworzenia wątku. Musi zostać przechwycony w pracowniku i przekazany odpowiednio zsynchronizowanym kanałem.

Jeżeli podczas rozwijania stosu destruktor wypuści kolejny wyjątek, zostaje wywołane `terminate`. Destruktor może wewnętrznie wykonać operację rzucającą i ją obsłużyć, ale nie powinien wypuszczać porażki sprzątania. Przy braku pasującego handlera standard dopuszcza implementacyjny wybór, czy nastąpi rozwijanie stosu przed `terminate`; nie projektuj odzyskiwania ważnych danych z założeniem, że wtedy wszystkie destruktory na pewno się wykonają.

## Drugi przykład

Ten program pokazuje zarówno automatyczne sprzątnięcie, jak i zachowanie typu przy ponownym rzuceniu. Licznik nie jest globalny i pozwala sprawdzić stan po wejściu do zewnętrznego handlera.

~~~cpp
#include <cassert>
#include <stdexcept>

struct Failure : std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct Activity {
    int& count;
    explicit Activity(int& n) : count(n) { ++count; }
    ~Activity() { --count; }
};

void operation(int& count) {
    Activity activity{count};
    try {
        throw Failure{"operation failed"};
    } catch (const std::exception&) {
        assert(count == 1);
        throw;
    }
}

int main() {
    int active = 0;
    bool caught = false;
    try {
        operation(active);
    } catch (const Failure&) {
        caught = true;
        assert(active == 0);
    }
    assert(caught);
}
~~~

Wewnętrzny handler nie opuścił jeszcze zakresu `activity`, więc licznik wynosi jeden. Ponowne zgłoszenie opuszcza funkcję i uruchamia destruktor, zanim zewnętrzny handler zobaczy porażkę. Zmiana `throw;` na `throw error;` po nazwaniu parametru bazowego zmieniłaby typ nowego wyjątku i zewnętrzny `catch(Failure)` nie byłby właściwym odbiorcą.

## Porównanie i decyzje

Umieszczaj handlery tam, gdzie można wykonać decyzję: ponowić żądanie, wycofać transakcję, przetłumaczyć błąd na protokół lub zakończyć zadanie. Łapanie na każdym poziomie tylko po to, aby zalogować i ponownie rzucić, produkuje wielokrotne komunikaty bez dodatkowego odzyskiwania. Tekst `what()` służy człowiekowi; decyzje programu powinny zależeć od typu lub strukturalnych pól błędu.

**Ćwiczenie.** Konstruktor pozyskał plik w polu RAII, a następnie budowa drugiego pola rzuciła. Czy potrzebny jest `catch` w konstruktorze do zamknięcia pliku? **Odpowiedź:** nie, ukończone pole zostanie zniszczone automatycznie. Handler bywa potrzebny do tłumaczenia wyjątku, ale nie zastępuje własności zasobów przez pola. Sam obiekt docelowy nie został skutecznie skonstruowany.

Źródła reguł: [C++23: obsługa wyjątków](https://timsong-cpp.github.io/cppwp/n4950/except), [dopasowanie handlerów](https://timsong-cpp.github.io/cppwp/n4950/except.handle), [terminate](https://timsong-cpp.github.io/cppwp/n4950/except.terminate).

## Powiązane tematy

- [Exception safety i noexcept](02_raii_exception_safety_i_noexcept.md)
- [optional, expected i kody błędów](03_optional_expected_i_kody_bledow.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
