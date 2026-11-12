[← Spis treści](../README.md) · [Ścieżka nauki](../sciezka_nauki.md)

# Laboratoria: kontrakt, implementacja i próba obalenia

To trzy niewielkie projekty referencyjne, których pełną implementację i testy można przeczytać w jednym posiedzeniu. Uczą kontroli granic danych, silnych typów i zakończenia współbieżności. Przed otwarciem nagłówka przeczytaj kontrakt oraz testy i spróbuj własnej implementacji w osobnym katalogu. Potem porównaj decyzje, nie tylko wynik.

Nie są gotowymi bibliotekami do rozliczeń finansowych ani uniwersalnym executorem. Ich ograniczony zakres umożliwia przeanalizowanie wszystkich stanów. [Zadania rozszerzające](ZADANIA.md) prowadzą od implementacji do oceny projektu.

## Presety: te same warianty lokalnie i w automatyzacji

Presety w [CMakePresets.json](CMakePresets.json) wymagają CMake co najmniej 3.21, choć ręczna konfiguracja projektu nadal dopuszcza 3.20. Z katalogu `praktyka`:

~~~text
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
cmake --preset release
cmake --build --preset release
ctest --preset release
cmake --preset ubsan
cmake --build --preset ubsan
UBSAN_OPTIONS=halt_on_error=1 ctest --preset ubsan
~~~

Presety mają oddzielne katalogi budowania i nie zapisują prywatnej ścieżki SDK. Jeśli potrzebujesz lokalnego SDK, przekaż `-DCMAKE_OSX_SYSROOT=/pelna/sciezka/do/zgodnego/SDK` podczas konfiguracji albo użyj ignorowanego `CMakeUserPresets.json`. Współdzielona konfiguracja nie powinna zawierać ścieżek autora.

## Budowanie i uruchomienie

Wymagania: CMake co najmniej 3.20, kompilator z potrzebnymi funkcjami C++23, jego biblioteka standardowa, narzędzie budowania oraz Python 3 do testów procesu CLI. Brak pobieranych pakietów. Polecenia uruchamiaj z głównego katalogu kompendium.

~~~text
cmake -S praktyka -B build/praktyka-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build/praktyka-debug --config Debug
ctest --test-dir build/praktyka-debug -C Debug --output-on-failure

cmake -S praktyka -B build/praktyka-release -DCMAKE_BUILD_TYPE=Release
cmake --build build/praktyka-release --config Release
ctest --test-dir build/praktyka-release -C Release --output-on-failure
~~~

Dla generatorów wielokonfiguracyjnych konfigurację wybierają `--config` i `-C`; `CMAKE_BUILD_TYPE` dotyczy generatorów jednokonfiguracyjnych. Program `stats` znajduje się w katalogu budowania, a w generatorze wielokonfiguracyjnym w podkatalogu konfiguracji. Przykład dla generatora jednokonfiguracyjnego:

~~~text
./build/praktyka-debug/stats 10 -3 0
count=3 sum=7 min=-3 max=10
~~~

Osobny wariant z ASan i UBSan dla Clang/GCC:

~~~text
cmake -S praktyka -B build/praktyka-asan -DCMAKE_BUILD_TYPE=Debug -DKOMPENDIUM_SANITIZERS=ON
cmake --build build/praktyka-asan --config Debug
ctest --test-dir build/praktyka-asan -C Debug --output-on-failure
~~~

Jeśli macOS wybiera SDK niezgodny z używanym linkerem, wskaż w **nowym katalogu budowania** `-DCMAKE_OSX_SYSROOT=/pelna/sciezka/do/zgodnego/MacOSX.sdk`. Wersja SDK i narzędzia muszą pochodzić ze zgodnej instalacji. Nie zmieniaj globalnego `xcode-select` tylko po to, aby uruchomić przykład. Szczegóły środowiska rzeczywistego odbioru są w [raporcie](../RAPORT_KONCOWY.md).

## Laboratorium A. Ścisły parser i statystyki CLI

**Kod:** [parser](include/strict_integer.hpp), [program](src/stats.cpp), [testy parsera](tests/parser_test.cpp), [testy procesu](tests/cli_test.py).

`parse_integer(string_view)` zwraca `variant<int, ParseError>`. Sukces oznacza, że cały niepusty ciąg jest dziesiętnym zapisem wartości mieszczącej się w `int`. Dopuszczone są minus i zera wiodące, odrzucone plus, białe znaki, prefiksy i sufiksy. `-0` oznacza zero. Osadzone NUL jest częścią wejścia, nie terminatorem. Reguły te są **polityką parsera**, a nie uniwersalną definicją prawidłowej liczby użytkownika.

Trzy klasy błędu: brak dopasowania, przekroczenie zakresu i niezużyty sufiks. Jeśli zachodzi kilka problemów, obowiązuje kolejność: brak dopasowania, zakres, sufiks. `from_chars` pozwala rozpoznać prefiks liczbowy, dlatego brak kontroli `ptr == end` byłby błędem kontraktu. Puste wejście jest sprawdzane przed tworzeniem końcowego wskaźnika; domyślny pusty `string_view` nie musi mieć niezerowego `data()`.

CLI przyjmuje argumenty liczbowe, a wynik drukuje dopiero po sprawdzeniu wszystkich. Niepoprawny argument oznacza kod wyjścia 2, diagnostykę na stderr i brak częściowego raportu na stdout. Suma ma typ `long long` i sprawdzenie zakresu przed dodaniem. Nie wyznaczamy średniej, żeby nie przemycić nieustalonej polityki zaokrąglania.

**Spróbuj obalić:** podaj `12x`, pusty argument, bardzo długą liczbę i wartość graniczną typu. Usuń w swojej kopii kontrolę sufiksu: istniejące testy powinny wykryć regresję. Czy odróżniasz gramatykę liczby od ograniczeń aplikacji, np. dopuszczalnego zakresu portów?

## Laboratorium B. Pieniądze i jednostki

**Kod:** [Money](include/money.hpp), [testy](tests/money_test.cpp).

`Money<Currency>` przechowuje całkowitą liczbę jednostek najmniejszych w `int64_t`. `Money<PLN>` i `Money<EUR>` to różne typy. Konstruktor jest explicit. Metoda `add` przyjmuje tylko pieniądze tej samej waluty i zwraca `optional<Money>`: brak wyniku oznacza przepełnienie. Nie ma niejawnej wymiany walut, mnożenia przez double ani założenia, że ujemne saldo jest zabronione.

Kontrola dodawania bada granice **przed** wykonaniem operacji. Dla dodatniego drugiego składnika sprawdza `a > max - b`, dla ujemnego `a < min - b`. Te odejmowania są wykonywane tylko w gałęziach, w których mieszczą się w typie. Nie wolno najpierw dodać i potem testować, czy wynik „zawinął”, bo signed overflow jest UB.

Wartości porównują się według reprezentacji, co tu odpowiada zadeklarowanemu znaczeniu. `static_assert` w testach sprawdza zarówno obliczenie compile-time, jak i brak mieszania walut. Zwykłe testy zachowania korzystają z rzucającego `check`, więc działają także przy zdefiniowanym `NDEBUG`.

**Spróbuj obalić:** minimum plus minus jeden, maksimum plus jeden, minimum plus maksimum. Następnie zaprojektuj rabat i ustal, kto wybiera sposób zaokrąglania. Sama zmiana typu z float na int nie rozwiązuje wszystkich problemów domeny finansowej.

## Laboratorium C. Ograniczona kolejka i zakończenie pracy

**Kod:** [BoundedQueue](include/bounded_queue.hpp), [testy](tests/queue_test.cpp).

`BoundedQueue<T>` obsługuje wielu producentów i konsumentów. `push(T)` blokuje przy pełnej kolejce i zwraca false po zamknięciu. `pop()` blokuje przy pustej otwartej kolejce. Po zamknięciu odbiera istniejące elementy w kolejności FIFO, a `nullopt` oznacza dopiero stan zamknięta i pusta. `close()` jest idempotentne. Zmiana stanu i operacje na kontenerze są chronione jednym mutexem.

Typ elementu musi być nothrow move constructible i nothrow destructible. Dzięki temu przeniesienie odbieranego elementu nie pozostawia kolejki z częściowo przeniesionym frontem po wyjątku. Kontener `deque` może jednak alokować; pojemność ogranicza **liczbę oczekujących elementów**, nie daje gwarancji pracy bez alokacji ani real-time. Koszt argumentów oczekujących producentów i zasobów wewnątrz `T` jest odrębny. Jeśli dodanie rzuci, kolejka przekazuje powiadomienie kolejnemu producentowi i ponownie rzuca wyjątek. Samo RAII zwolniłoby mutex, lecz mogłoby pozostawić wolne miejsce bez obudzenia pozostałych oczekujących. Nie gwarantujemy odzyskania wartości argumentu przekazanego do nieudanego `push`.

Zamknięcie budzi producentów i konsumentów. Zwykły stop request w `jthread` nie zastąpi tej operacji. Właściciel odpowiada za `close` oraz dołączenie wszystkich wątków przed destrukcją kolejki. Test wielu producentów sprawdza dostarczenie każdego numeru dokładnie raz, a nie tylko zgodność sumy, która mogłaby ukryć duplikat i brak innej wartości.

Powiadomienie następuje po odblokowaniu mutexu; samo powiadomienie nie publikuje danych. Bezpieczeństwo wynika z dostępu do chronionego stanu i predykatów wait. Nie obiecujemy sprawiedliwości planowania ani określonej kolejności obsługi oczekujących wątków. FIFO opisuje elementy przyjęte do kolejki.

**Spróbuj obalić:** zamknij pustą kolejkę z konsumentem oraz pełną z producentem. Przy wyścigu `close` i `push` wynik zależy od tego, która operacja zmieni stan pod mutexem pierwsza. To dozwolony wybór protokołu, nie dowód data race.

## Co wyniki testów dowodzą

CTest uruchamia trzy programy testowe C++ i zestaw testów CLI. Timeout chroni uruchomienie przed bezterminowym zawieszeniem, ale nie jest synchronizacją aplikacji. Testy nie używają sleep jako dowodu uporządkowania. Scenariusze budzenia obejmują również legalny przypadek, gdy zamknięcie nastąpi przed wejściem drugiej strony w wait; nie gwarantują odtworzenia każdego przeplotu.

ASan i UBSan wykrywają określone klasy problemów w faktycznie wykonanych ścieżkach. Nie dowodzą braku data race ani deadlock. ThreadSanitizer uruchamia się osobno, bez łączenia z ASan; dostępność zależy od platformy. Dowód poprawności protokołu nadal wymaga analizy stanów, relacji synchronizacji i lifetime.

W lokalnym odbiorze z 12 listopada 2026 testy Debug, Release i osobne UBSan przeszły. Łączony wariant ASan/UBSan zbudował się, lecz wykonywanie zatrzymywało się przy inicjalizacji ASan; identycznie zachowywał się minimalny program z pustym `main`. Próba poza sandboxem również zakończyła się timeoutem. Nie uznajemy tego wariantu za zaliczony. To ograniczenie lokalnego runtime wymagające osobnej diagnozy toolchainu, bez dowodu, że problem pochodzi z kodu laboratoriów.

Źródła: [C++23 from_chars](https://timsong-cpp.github.io/cppwp/n4950/charconv.from.chars), [condition_variable](https://timsong-cpp.github.io/cppwp/n4950/thread.condition.condvar), [CTest add_test](https://cmake.org/cmake/help/v3.20/command/add_test.html), [ASan](https://clang.llvm.org/docs/AddressSanitizer.html), [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html).
