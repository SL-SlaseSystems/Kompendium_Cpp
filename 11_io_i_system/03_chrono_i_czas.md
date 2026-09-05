[← Spis treści](../README.md)

# chrono i czas

Biblioteka `<chrono>` rozdziela zegar, punkt czasu i duration. `steady_clock` jest monotoniczny i nadaje się do mierzenia odstępów. `system_clock` wiąże się z czasem kalendarzowym i może zostać skorygowany. `high_resolution_clock` jest aliasem zależnym od implementacji i nie gwarantuje monotoniczności.

~~~cpp
#include <cassert>
#include <chrono>

using namespace std::chrono_literals;

int main() {
    constexpr auto timeout = 250ms;
    constexpr auto interval = 2s + 500ms;
    static_assert(timeout.count() == 250);
    static_assert(std::chrono::duration_cast<std::chrono::milliseconds>(interval).count() == 2500);

    const auto start = std::chrono::steady_clock::now();
    const auto end = std::chrono::steady_clock::now();
    assert(end >= start);
}
~~~

Duration ma reprezentację i period. Dodawanie różnych jednostek wykorzystuje wspólny typ, a `duration_cast` wykonuje jawną konwersję, potencjalnie obcinając część ułamkową. Literały `ms`, `s`, `min` poprawiają czytelność i zapobiegają przekazywaniu „gołej liczby” o niejasnej jednostce.

C++20 rozszerzył chrono o calendar i time zones. Dostępność bazy stref, jej aktualizacja i wsparcie biblioteki zależą od środowiska. Czas lokalny może być niejednoznaczny lub nieistniejący przy zmianie DST; przechowuj zdarzenia jako jednoznaczny punkt czasu i konwertuj do strefy na granicy prezentacji.

Timeouty powinny używać deadline opartego o steady clock, aby spurious wakeup i kolejne pętle nie wydłużały limitu. Nie zakładaj dokładności harmonogramu równej rozdzielczości typu; system może wznowić wątek później.

## Jak to działa krok po kroku

Zacznij od określenia, co reprezentuje wartość: długość odcinka czy pozycję na osi konkretnego zegara. `500ms` to odcinek. `steady_clock::now()` to punkt czasu. Różnica dwóch punktów tego samego zegara daje odcinek, a dodanie odcinka do punktu daje nowy punkt. Taki model zapobiega przypadkowemu dodawaniu dwóch dat lub porównywaniu niepowiązanych zegarów.

Przy timeout najpierw wyznacz `deadline = steady_clock::now() + timeout`. W pętli oczekiwania wracaj do tego samego deadline. Gdy za każdym przebudzeniem rozpoczynasz od nowa pełne `wait_for(timeout)`, kolejne pobudki mogą wielokrotnie odsunąć zakończenie. Samo osiągnięcie deadline nie gwarantuje dokładnego momentu wznowienia wątku: do wykonania potrzebny jest jeszcze czas procesora.

## Pogłębienie mechanizmu

Typ `duration<Rep, Period>` przechowuje liczbę taktów w `Rep`; `Period` określa długość taktu jako ułamek sekundy. `count()` zwraca samą liczbę i traci informację o jednostce w typie wyniku. Nie przekazuj jej dalej jako niezinterpretowanego `int`, jeżeli odbiorca może przyjąć bezpośrednio `milliseconds` lub inny typ czasu.

Konwersja na jednostkę grubszą może tracić dokładność. Dla reprezentacji całkowitych `duration_cast` obcina w kierunku zera. To szczególnie ważne dla ujemnych odcinków: obcięcie nie jest zaokrągleniem w dół. `floor`, `ceil` i `round` pozwalają wyrazić konkretną politykę. Oprócz precyzji kontroluj zakres reprezentacji, ponieważ przeliczenie ogromnej wartości na nanosekundy może się nie mieścić.

Kalendarz i arytmetyka czasu trwania rozwiązują różne problemy. `days{1}` opisuje odcinek 24 godzin, ale przejście do następnego dnia kalendarzowego w lokalnej strefie może obejmować inny czas rzeczywisty przy zmianie DST. „Spotkanie jutro o 9:00” wymaga daty, lokalnej godziny i strefy; „spróbuj ponownie za 30 sekund” wymaga odcinka i zegara monotonicznego.

## Drugi przykład

~~~cpp
#include <chrono>

using namespace std::chrono_literals;

int main() {
    constexpr auto delta = -1500ms;
    static_assert(std::chrono::duration_cast<std::chrono::seconds>(delta) == -1s);
    static_assert(std::chrono::floor<std::chrono::seconds>(delta) == -2s);
    static_assert(std::chrono::ceil<std::chrono::seconds>(delta) == -1s);
    constexpr auto sum = 2s + 250ms;
    static_assert(sum == 2250ms);
    constexpr std::chrono::year_month_day leap_day{
        std::chrono::year{2024}, std::chrono::month{2}, std::chrono::day{29}};
    static_assert(leap_day.ok());
}
~~~

Wyniki są sprawdzane podczas kompilacji i nie zależą od szybkości komputera. `year_month_day` może reprezentować niepoprawną datę, dlatego samo skonstruowanie pól nie zastępuje `ok()`. To analogiczne do parsera, który odczytał trzy liczby, ale jeszcze nie ustalił, czy tworzą datę kalendarzową.

## Porównanie i decyzje

Do pomiaru czasu działania i limitów używaj `steady_clock`. Do zapisywania znaczników zdarzeń, które mają znaczenie poza jednym procesem, używaj odpowiednio określonej skali czasu, często opartej na `system_clock`, i dokumentuj format. Nie serializuj surowych bajtów `time_point`: wybierz jednostkę, epokę, szerokość reprezentacji oraz zasady dotyczące sekund przestępnych.

Do testów logiki terminów wstrzykuj źródło czasu lub przekazuj `now` jako argument. Test, który usypia wątek na sekundę i liczy na idealny harmonogram, jest wolny i podatny na obciążenie maszyny. Kontrolowany zegar pozwala sprawdzić moment tuż przed granicą, dokładnie na niej i po niej bez oczekiwania.

## Ćwiczenie z odpowiedzią

Czy `duration_cast<seconds>(-1500ms)` daje `-2s`? Nie, daje `-1s`. Jeśli dzielisz oś czasu na przedziały i potrzebujesz dolnej granicy, wybierz `floor`. Następnie wyjaśnij, dlaczego dodanie `24h` do punktu czasu nie jest zawsze tym samym co wybór tej samej lokalnej godziny następnego dnia: przepisy strefowe zmieniają odwzorowanie lokalnego kalendarza na oś czasu.

Źródła: [C++23, duration_cast](https://timsong-cpp.github.io/cppwp/n4950/time.duration.cast), [biblioteka chrono](https://timsong-cpp.github.io/cppwp/n4950/time).

## Powiązane tematy

- [Benchmarki](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [condition_variable](../10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)
- [C++20](../12_wspolczesny_cpp/03_cpp20.md)

