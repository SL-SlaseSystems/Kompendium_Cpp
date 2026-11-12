[← Spis treści](../README.md)

# Pipeline build test analyze

**Wymagania wstępne:** kompilacja i linkowanie, testy procesu, CMake oraz podstawy repozytorium Git. Pracujemy na dołączonym [workflow](../.github/workflows/verify.yml), a nie na modelu z trzema wartościami bool. Dodanie konfiguracji do repozytorium nie oznacza jeszcze udanego zdalnego przebiegu; jego wynik wymaga wykonania przez usługę CI.

Pipeline to program sterujący innymi programami. Musi przekazywać błędy i uruchamiać kolejne kroki na właściwych artefaktach. W tym repozytorium kontrola ma trzy różne produkty: wyniki testów walidatora, kontrolę dokumentów i składni przykładów oraz wykonanie laboratoriów. Każdy z nich odpowiada na inne pytanie. Pozytywny wynik pierwszego nie zastępuje dwóch pozostałych.

## Jak to działa krok po kroku

Dołączony workflow uruchamia macierz dwóch kompilatorów i dwóch konfiguracji. Poniższy fragment pokazuje te same wybory; kompletny plik zawiera także pobranie repozytorium i kroki kontroli dokumentów:

~~~yaml
strategy:
  fail-fast: false
  matrix:
    compiler: [g++, clang++]
    configuration: [Debug, Release]
env:
  CXX: ${{ matrix.compiler }}
steps:
  - name: Configure practice
    run: cmake -S praktyka -B build/praktyka -DCMAKE_BUILD_TYPE=${{ matrix.configuration }}
  - name: Build practice
    run: cmake --build build/praktyka --parallel 2 --config ${{ matrix.configuration }}
  - name: Run practice tests
    run: ctest --test-dir build/praktyka -C ${{ matrix.configuration }} --output-on-failure
~~~

Każdy job zaczyna ze świeżym workspace. Ustawione `CXX` wybiera kompilator przy pierwszej konfiguracji, a CMake zapisuje wynik w cache. Nie zmieniamy kompilatora w już skonfigurowanym katalogu jednego joba. Macierz daje cztery niezależne próby; `fail-fast: false` pozwala zachować diagnostykę pozostałych konfiguracji po porażce jednej. Nie oznacza, że błędy mają być ignorowane.

Konfiguracja wyraża graf, build wytwarza programy, a CTest je wykonuje. Jeżeli kompilacja zawiedzie, zwykłe zależności kroków zatrzymują testowanie nieaktualnego artefaktu. Test ma zwrócić niezerowy kod przy błędzie i rzeczywiście wykonać badane działanie. W laboratoriach mechanizm `check` nie znika po zdefiniowaniu `NDEBUG`, więc sprawdzenia zachowania pozostają aktywne w Release.

## Pogłębienie mechanizmu

Kontrola Markdown uruchamia kompilator z `-fsyntax-only`. Sprawdza składnię i instancjację użytego kodu, ale nie wykonuje linkowania ani programu. Wiele klas problemów pozostaje poza jej zakresem: brakujący symbol przy linkowaniu, dangling view podczas wykonania, naruszenie semantyki porównania czy zakleszczenie. Dlatego osobny projekt CMake tworzy pliki wykonywalne i uruchamia testy, a redakcyjny przegląd ocenia sens przykładów.

Testy walidatora korzystają z małych kontrolowanych repozytoriów. Wykazują m.in., że krótki zestaw ćwiczeń nie jest błędnie oceniany jak rozdział oraz że martwy link faktycznie powoduje porażkę. Są testami narzędzia, nie dowodem poprawności opisanej w książce arytmetyki czy protokołu HTTP. W raporcie wyniki muszą pozostać rozdzielone.

W macierzy ważne są rzeczywiste różnice. Dwie nazwy sterownika tego samego Apple Clang nie tworzą testu GCC i Clang. Z kolei ta sama wersja frontendu z różnymi bibliotekami standardowymi może ujawnić braki biblioteczne. Dla publicznej biblioteki ustal docelową macierz systemu, kompilatora, biblioteki i trybu standardu; ten mały workflow sprawdza tylko zadeklarowany wycinek na runnerze Ubuntu.

Timeout joba i timeout testu chronią zasoby wykonawcy, lecz nie są metodą synchronizacji programu. Test kolejki nadal potrzebuje poprawnego close/drain i dołączenia wątków. Dla scenariusza zewnętrznej usługi przygotuj kontrolowany serwer albo wydzielony test integracyjny. Nie zastępuj awarii sieci losowym sleep i nie interpretuj sporadycznej porażki jako normalnego kosztu testowania.

## Drugi przykład

Reprodukcja lokalna powinna używać tych samych kroków i tej samej konfiguracji. Z katalogu głównego repozytorium, z obsługiwanym kompilatorem w PATH:

~~~text
python3 -m unittest discover -s scripts -p 'test_*.py' -v
CXX=clang++ bash scripts/verify.sh
cmake -S praktyka -B build/repro-clang-release -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build build/repro-clang-release --config Release
ctest --test-dir build/repro-clang-release -C Release --output-on-failure
~~~

Nie porównuj tych wyników z innym kompilatorem ukrytym w starym cache. Zapisz wersję narzędzia, dokładny commit, polecenie i pełną diagnostykę pierwszego błędu. Dla problemów zależnych od danych zachowaj minimalny przypadek reprodukujący. Lokalne powodzenie na macOS nie jest dowodem powodzenia joba na Ubuntu; do czasu wykonania usługi plik workflow pozostaje sprawdzoną konfiguracją, a nie zielonym odznaczeniem.

Wersje zewnętrznych akcji mają znaczenie dla odtwarzalności. W dołączonym pliku akcja checkout jest przypięta do konkretnego commitu odpowiadającego wydaniu 4.2.2, a poświadczenia nie pozostają zapisane do późniejszych poleceń Git. Przypięcie jest decyzją o aktualizacji zależności: trzeba świadomie zmieniać identyfikator po przeglądzie nowej wersji. Nie daje ono automatycznego dowodu poprawności całego łańcucha narzędzi.

## Porównanie i decyzje

Szybkie kontrole uruchamiaj wcześnie, a kosztowne warianty według realnego ryzyka. Sanitizery mają własne konfiguracje; ich dostępność i zgodność runtime trzeba sprawdzić osobno. Lokalny ASan zatrzymywał się także dla pustego main, więc nie jest raportowany jako zaliczony. Samo dopisanie flagi w YAML nie rozwiązuje problemu środowiska.

**Ćwiczenie 1.** CI uruchomiło CTest po zmianie parsera, ale nie wykonało build. Dlaczego zielony wynik może być bezwartościowy?

<details><summary>Rozwiązanie</summary>

CTest może uruchomić wcześniejszy plik wykonywalny. Skieruj kroki do tego samego katalogu, wykonaj build i przerwij przepływ po jego błędzie. Potwierdź skuteczność testu kontrolowaną regresją w kopii źródeł.

</details>

**Ćwiczenie 2.** Dwie konfiguracje przechodzą, jedna zawodzi. Czy usunięcie tej komórki macierzy jest naprawą?

<details><summary>Rozwiązanie</summary>

Tylko świadome zakończenie wsparcia i zmiana kontraktu mogą uzasadniać usunięcie. Najpierw rozpoznaj brak funkcji, błąd programu albo wadę środowiska. Zapisz reprodukcję i skoryguj kod, konfigurację lub deklarowany zakres wsparcia.

</details>

Źródła: [składnia workflow](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [macierze jobów](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations), [przypięte wydanie checkout](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683).

## Powiązane tematy

- [Presety CMake](../14_warsztat_profesjonalisty/03_cmake_presets_i_ninja.md)
- [Macierze platform](02_macierze_kompilatorow_i_platform.md)
- [Rzeczywiste testy laboratoriów](../praktyka/README.md)
