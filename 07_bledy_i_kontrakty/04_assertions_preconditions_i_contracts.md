[← Spis treści](../README.md)

# Assertions, preconditions i contracts

Precondition opisuje warunek, który klient musi spełnić przed wywołaniem. Postcondition opisuje zapewnienie po sukcesie, a inwariant własność utrzymywaną przez poprawne stany typu. Kontrakt istnieje niezależnie od sposobu sprawdzania: dokumentacja, typy, assertions i walidacja wejścia pełnią różne role.

~~~cpp
#include <cassert>
#include <optional>
#include <span>

std::optional<double> average(std::span<const int> values) {
    if (values.empty()) {
        return std::nullopt;
    }
    long long total = 0;
    for (int value : values) {
        total += value;
    }
    return static_cast<double>(total) / static_cast<double>(values.size());
}

int main() {
    const int values[]{2, 4, 6};
    const auto result = average(values);
    assert(result && *result == 4.0);
}
~~~

Makro `assert` jest usuwane, gdy zdefiniowano `NDEBUG`. Nie używaj go do walidacji niezaufanego wejścia, wykonywania niezbędnych efektów ubocznych ani obsługi błędu, który może legalnie zdarzyć się w produkcji. Assertion jest odpowiednie dla naruszenia wewnętrznego założenia programisty.

Silniejsze typy mogą uczynić niedozwolony stan niereprezentowalnym, np. `NonEmptySpan` skonstruowany przez walidującą fabrykę. To przenosi sprawdzenie na granicę i upraszcza wnętrze. Nie każdy warunek daje się jednak zakodować w typie bez nieproporcjonalnej złożoności.

Kontrakty językowe były proponowane i zmieniały się w toku standaryzacji. Nie opisuj wcześniejszych eksperymentalnych składni jako części C++23. W nowszym standardzie użycie contracts zależy od ostatecznie opublikowanej specyfikacji i wsparcia implementacji; bazowy kod powinien mieć własną strategię niezależną od przyszłego mechanizmu.

## Jak to działa krok po kroku

Projektowanie kontraktu zaczyna się od określenia legalnych wejść. Średnia pustego zakresu nie ma zwykłej wartości liczbowej, dlatego pierwszy przykład zwraca `nullopt`. To spodziewany wynik, nie błąd pamięci. Dla niepustego zakresu funkcja sumuje liczby i zwraca iloraz. Odrębnym warunkiem tego prostego wariantu jest reprezentowalność sumy w `long long`: bardzo długi zakres dużych wartości może go przekroczyć. Szerszy akumulator ogranicza ryzyko, lecz nie stanowi kompletnego dowodu dla dowolnego wejścia.

Następnie wybierz miejsce sprawdzenia. Dane od użytkownika trzeba walidować w kodzie wykonywanym także w wersji produkcyjnej. Wewnątrz programu można wykorzystać fakt, że konstruktor już zweryfikował wartość i przechowuje ją w typie utrzymującym inwariant. Powtarzanie kosztownego sprawdzenia na każdym poziomie nie jest konieczne, jeżeli publiczne operacje nie pozwalają złamać tego zapewnienia.

Na końcu określ zachowanie porażki. Funkcja może zwrócić expected, rzucić wyjątek lub zakończyć proces przy wewnętrznej niespójności. Sam opis „argument musi być dodatni” nie mówi jeszcze, czy błędny argument jest diagnozowany. Dla własnego API dokumentuj to jawnie. Wymagania funkcji standardowej odczytuj z jej specyfikacji; obecność sprawdzeń w jednej bibliotece w trybie debug nie tworzy dodatkowej gwarancji języka.

## Pogłębienie mechanizmu

`assert(condition)` ocenia warunek tylko wtedy, gdy asercje są aktywne. Przy zdefiniowanym `NDEBUG` wyrażenie nie jest wykonywane, więc `assert(queue.pop())` zmienia zachowanie programu między konfiguracjami. Właściwa postać oddziela operację od kontroli jej wyniku. Warunek diagnostyczny powinien być obserwacją już istniejącego stanu, bez niezbędnego zapisu, odczytu pliku ani zmiany licznika.

`static_assert` sprawdza wyrażenie stałe podczas kompilacji i nie zależy od `NDEBUG`. Nadaje się do właściwości typów, rozmiarów ustalonych w kompilacji i konfiguracji szablonów. Nie sprawdzi numeru portu przeczytanego z sieci. Concepts także filtrują interfejs na podstawie typów i poprawności wyrażeń, lecz nie dowodzą, że komparator jest przechodni albo że użytkownik nie zniszczy bufora pod widokiem.

C++23 `[[assume(condition)]]` jest założeniem przekazanym implementacji, a nie mechanizmem sprawdzania. Wyrażenie nie jest normalnie wykonywane, a naruszenie założenia prowadzi do undefined behavior. Nie używaj go do zastąpienia walidacji bezpieczeństwa. Kompilator może wykorzystać założenie do usunięcia gałęzi, przez co błędne wejście będzie działać jeszcze mniej przewidywalnie.

Klasy powinny odzyskiwać inwariant przed przekazaniem sterowania klientowi. Wewnętrzna operacja może przejściowo zmieniać kilka pól, ale wyjątek nie może pozostawić publicznie dostępnego obiektu w stanie niezgodnym z zadeklarowaną gwarancją. Dlatego kontrakty łączą się bezpośrednio z RAII i exception safety, a nie są jedynie komentarzami dopisywanymi do sygnatur.

## Drugi przykład

Fabryka waliduje liczbę raz i zwraca typ, którego zwykłe publiczne operacje nie umożliwiają utworzenia portu spoza zakresu. Asercja pozostaje narzędziem testowym.

~~~cpp
#include <cassert>
#include <optional>

class Port {
    int value_;
    explicit Port(int value) : value_(value) {}
public:
    static std::optional<Port> make(int value) {
        if (value < 1 || value > 65535) return std::nullopt;
        return Port{value};
    }
    int value() const noexcept { return value_; }
};

int connect_to(Port port) {
    return port.value(); // miejsce właściwej operacji sieciowej
}

int main() {
    const auto port = Port::make(443);
    assert(port && connect_to(*port) == 443);
    assert(!Port::make(0));
    assert(!Port::make(65536));
    static_assert(sizeof(int) >= 2);
}
~~~

Nie jest potrzebny setter przyjmujący dowolne `int`, ponieważ zniszczyłby zapewnienie typu. Kopiowanie poprawnego Port zachowuje inwariant. Przykład wymaga, aby implementacyjny `int` reprezentował używane stałe; w API przenoszącym dokładnie 16 bitów warto rozważyć odpowiedni typ bez znaku wraz z walidacją przed zawężeniem. Walidowanie dopiero po rzutowaniu mogłoby zaakceptować zawiniętą liczbę.

## Porównanie i decyzje

Silny typ opłaca się, gdy sprawdzana własność przechodzi przez wiele funkcji. Dla pojedynczego użycia prosty warunek może być czytelniejszy. Asercje wykrywają pomyłki autora, walidacja obsługuje legalnie błędne dane zewnętrzne, a statyczne ograniczenia usuwają część pomyłek jeszcze przed uruchomieniem. C++23 nie zawiera osobnej składni językowych contracts; przykłady nie zakładają późniejszych rozwiązań.

**Ćwiczenie.** Czy `assert(index < size); return data[index];` jest kompletną bezpieczną obsługą indeksu przesłanego przez użytkownika? **Odpowiedź:** nie. Po wyłączeniu asercji brak kontroli granicy. Potrzebny jest zwykły warunek lub sprawdzające API, a wybrany sposób zgłaszania porażki powinien należeć do kontraktu funkcji.

Źródła reguł: [C++23: assert](https://timsong-cpp.github.io/cppwp/n4950/assertions), [static_assert](https://timsong-cpp.github.io/cppwp/n4950/dcl.pre), [atrybut assume](https://timsong-cpp.github.io/cppwp/n4950/dcl.attr.assume).

## Powiązane tematy

- [optional i expected](03_optional_expected_i_kody_bledow.md)
- [Enkapsulacja](../04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)
