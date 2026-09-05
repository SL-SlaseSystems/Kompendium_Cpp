[← Spis treści](../README.md)

# Sanitizery i debuggery

Sanitizery instrumentują program, aby wykrywać klasy błędów podczas wykonania. AddressSanitizer znajduje wiele use-after-free, buffer overflow i błędów stosu. UndefinedBehaviorSanitizer wykrywa wybrane przypadki UB. ThreadSanitizer szuka data races. MemorySanitizer śledzi niezainicjalizowane odczyty, lecz ma bardziej wymagające środowisko. Dostępność i łączenie sanitizerów zależy od platformy.

~~~text
clang++ -std=c++23 -g -O1 -fno-omit-frame-pointer \
  -fsanitize=address,undefined main.cpp -o app
./app
~~~

Instrumentowane powinny być zarówno kompilacja, jak i linkowanie. `-g` umożliwia symbolizację, `-O1` zachowuje realistyczniejszy kod niż całkowity brak optymalizacji, a frame pointers pomagają stosom wywołań. Sanitizery nie dowodzą braku UB — obserwują tylko wykonane ścieżki i wspierane klasy problemów.

~~~cpp
#include <cassert>
#include <vector>

int checked_at(const std::vector<int>& values, std::size_t index) {
    return values.at(index);
}

int main() {
    const std::vector values{10, 20};
    assert(checked_at(values, 1) == 20);
}
~~~

Debugger, np. GDB, LLDB albo debugger Visual Studio, pozwala zatrzymać program, badać stos, zmienne, pamięć i wątki. Watchpoint reaguje na zmianę pamięci. Core dump zachowuje stan po awarii. Przy optymalizacji zmienne mogą być usunięte lub przemieszczone, dlatego debug i release trzeba analizować świadomie.

## Jak to działa krok po kroku

AddressSanitizer dodaje do operacji pamięci sprawdzenia korzystające z pomocniczego stanu pamięci. Regiony za granicami alokacji lub po zwolnieniu mogą być oznaczone jako niedostępne. Dostęp do takiego miejsca powoduje raport zawierający stos błędnej operacji, a często również miejsce wcześniejszej alokacji i zwolnienia. Pierwszy zgłoszony błąd warto naprawić przed analizowaniem dalszych skutków, ponieważ po uszkodzeniu pamięci kolejne objawy mogą być wtórne.

Kompiluj wszystkie własne jednostki wymagające obserwacji z właściwą instrumentacją i linkuj przez sterownik kompilatora, który dobierze runtime. Sama flaga na końcowym linkowaniu nie doda sprawdzeń do wcześniej skompilowanych instrukcji. Dla biblioteki budowanej osobno sprawdź konfigurację tego targetu, a nie tylko ustawienia programu głównego.

Gdy raport jest zrozumiały, zamień przypadek na mały test regresyjny. Ustal rzeczywistą przyczynę: zły indeks, wygasły właściciel czy niespójny protokół synchronizacji. Dodanie opóźnienia albo zwiększenie pojemności bufora może zmienić objaw bez naprawienia reguły. Ponownie uruchom przypadek oraz istotne sąsiednie scenariusze z tym samym sanitizatorem.

## Pogłębienie mechanizmu

ASan przede wszystkim kontroluje dostępność pamięci, a nie wszystkie semantyczne wymagania kontenerów. Zapis poza `vector.size()`, lecz wewnątrz zaalokowanej pojemności, może wymagać dodatkowych adnotacji biblioteki, aby został wykryty. Brak raportu nie legalizuje takiego dostępu. Analogicznie iterator może być logicznie unieważniony, mimo że jego dawny adres leży w nadal dostępnej alokacji.

UBSan obejmuje wybrane klasy, np. pewne przepełnienia signed, niewłaściwe wyrównanie i niepoprawne operacje arytmetyczne. Nie jest pełnym interpreterem wszystkich reguł standardu. Zawijanie arytmetyki unsigned jest zwykle zachowaniem zdefiniowanym; jego dodatkowe sprawdzanie należy do innych ustawień narzędzia. Ważne jest rozróżnienie błędu domenowego od konkretnej kategorii UB wykrywanej daną flagą.

TSan śledzi konflikty dostępów i synchronizację między wątkami. Standardowa osobna konfiguracja `-fsanitize=thread` nie jest łączona z ASan w jednym typowym buildzie Clang. Zmiana harmonogramu przez instrumentację jest naturalna; test musi sprawdzać protokół, a nie milisekundowe opóźnienia. Własne prymitywy synchronizacji i nieinstrumentowane biblioteki wymagają uwzględnienia ograniczeń narzędzia.

MemorySanitizer śledzi niezainicjalizowane wartości i wymaga odpowiednio przygotowanych zależności oraz wspieranej platformy. Nie zakładaj jego dostępności na macOS tylko dlatego, że działa ASan. Debugger daje inną możliwość: zatrzymanie na konkretnej instrukcji i obserwację rzeczywistego stanu. Przy optymalizacji pojedyncza linia źródła nie odpowiada zawsze jednemu uporządkowanemu fragmentowi instrukcji maszynowych.

## Drugi przykład

Poniższy program ma zdefiniowane zachowanie i zgłasza kontrolowany wyjątek. Pozwala przećwiczyć debugger bez polegania na przypadkowym objawie undefined behavior.

~~~cpp
#include <cassert>
#include <cstddef>
#include <stdexcept>
#include <vector>

int read_item(const std::vector<int>& values, std::size_t index) {
    return values.at(index);
}

int main() {
    const std::vector<int> values{10, 20};
    bool rejected = false;
    try {
        (void)read_item(values, values.size());
    } catch (const std::out_of_range&) {
        rejected = true;
    }
    assert(rejected);
}
~~~

~~~text
clang++ -std=c++23 -g -O0 example.cpp -o example
lldb ./example
(lldb) breakpoint set --name read_item
(lldb) run
(lldb) frame variable index values
(lldb) thread backtrace
(lldb) next
(lldb) continue
~~~

Po zatrzymaniu indeks wynosi dwa, a kontener ma dwa elementy, więc dozwolone indeksy to zero i jeden. `at` kontroluje wymaganie i rzuca. ASan nie powinien raportować błędu pamięci dla tego poprawnego programu. Zastąpienie `at` przez `operator[]` usunęłoby walidację i naruszyło kontrakt; to zmiana semantyki, a nie tylko usunięcie kosztownego sprawdzenia.

Watchpoint przydaje się, gdy wiadomo, która zmienna jest nadpisywana, ale nie wiadomo gdzie. Wymaga adresu żyjącego obiektu i podlega ograniczeniom sprzętowym. Przy błędzie występującym poza debuggerem zbierz core dump wraz z dokładnie odpowiadającym binarium i symbolami. Inna kompilacja może mieć inne adresy i nie pozwala wiarygodnie odczytać stosu.

## Porównanie i decyzje

Zaczynaj od narzędzia odpowiadającego klasie objawu: ASan dla pamięci, TSan dla wyścigów, debugger dla konkretnego stanu i przepływu. Uruchamiaj sanitizery na testach o reprezentatywnych wejściach, bo samo zbudowanie instrumentowanego programu niczego jeszcze nie wykrywa. Mierz wydajność osobno: instrumentacja zmienia czas i pamięć, więc jej wyniki nie reprezentują konfiguracji produkcyjnej.

**Ćwiczenie.** Program przechodzi tysiąc testów pod ASan. Czy można uznać go za pozbawiony data races? **Odpowiedź:** nie. ASan nie jest narzędziem do pełnej analizy wyścigów, a testy pokrywają ograniczone wykonania. Potrzebny jest dowód synchronizacji oraz właściwa konfiguracja TSan tam, gdzie jest wspierana.

Źródła: [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html), [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html), [MemorySanitizer](https://clang.llvm.org/docs/MemorySanitizer.html), [samouczek LLDB](https://lldb.llvm.org/use/tutorial.html).

## Powiązane tematy

- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)
- [Atomiki i model pamięci](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
- [Fuzzing](05_fuzzing_i_property_based_testing.md)
