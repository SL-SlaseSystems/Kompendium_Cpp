[← Spis treści](../README.md)

# CMake Presets i Ninja

**Wymagania wstępne:** cele CMake, rozdzielenie konfiguracji od budowania oraz podstawy CTest. Punktem odniesienia jest rzeczywisty projekt [laboratoriów](../praktyka/README.md). Ręczne budowanie wymaga CMake 3.20; dołączone presety używają schematu wersji 3 i wymagają CMake 3.21.

Preset jest nazwanym zestawem ustawień. Nie zastępuje grafu zależności w `CMakeLists.txt`, a Ninja jest jednym z narzędzi wykonujących graf wygenerowany przez CMake. Te trzy role warto rozdzielić: projekt określa cele i ich wymagania, preset wybiera konfigurację, a backend wykonuje zlecone kompilacje. Zmiana jednego elementu nie naprawia błędu w pozostałych.

## Jak to działa krok po kroku

W repozytorium znajduje się kompletny [CMakePresets.json](../praktyka/CMakePresets.json). Warianty debug, release i ubsan korzystają z osobnych katalogów. Pole `binaryDir` jest liczone względem projektu, a zmienna `presetName` pozwala oddzielić artefakty każdego wariantu bez kopiowania całego opisu. Poniższe polecenia wykonuj z katalogu `praktyka`:

~~~text
cmake --list-presets
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
~~~

Pierwsze polecenie pokazuje konfiguracje dostępne w aktualnym projekcie. Drugie uruchamia konfigurację i generowanie. Trzecie kompiluje aktualne źródła, czwarte wykonuje zarejestrowane testy. CTest nie jest zamiennikiem budowania: jeżeli pominiesz build po zmianie źródeł, możesz przetestować stary plik wykonywalny. Dlatego kroki mają ustaloną zależność i są wykonywane również przez CI.

Wynik konfiguracji zawiera ścieżkę kompilatora, rozpoznaną bibliotekę i generator. Sprawdzaj ją przed interpretacją problemu jako błędu C++. W tym środowisku domyślny SDK i linker wymagały dopasowania; podanie właściwego SDK jako lokalnego parametru rozwiązywało problem linkowania. Wspólny preset nie powinien utrwalać tej prywatnej ścieżki dla wszystkich czytelników.

## Pogłębienie mechanizmu

Dziedziczenie presetów pozwala współdzielić ustawienia bez powtarzania. Wersja release zmienia typ konfiguracji, a ubsan dodaje ustawienia sanitizera. Właściwości projektu, takie jak wymaganie C++23 albo zależność od biblioteki wątków, pozostają przy celach. Nie przenoś ich wyłącznie do presetu: użytkownik konfigurujący projekt ręcznie również musi otrzymać poprawny graf.

Przy generatorze jednokonfiguracyjnym typowy wybór Debug/Release trafia do `CMAKE_BUILD_TYPE`. Generator wielokonfiguracyjny przechowuje wiele konfiguracji w jednym build tree; wybór następuje podczas budowania i testowania. Dlatego dołączone build presets i test presets mają pole `configuration`. Nazwanie katalogu „release” samo nie dowodzi użycia optymalizacji ani usunięcia asercji.

Cache CMake jest stanem konkretnego build tree. Przechowuje m.in. wynik wykrywania kompilatora i opcje projektu. Dla innego kompilatora lub generatora zakładaj nowy katalog, zamiast liczyć, że nadpisanie jednej zmiennej unieważni wszystkie wcześniejsze założenia. Wersjonowanie presetów umożliwia odtworzenie intencji konfiguracji, lecz nadal trzeba wskazać toolchain, platformę i zależności, aby porównywać wyniki.

Presety nie instalują automatycznie Ninja. Jeśli chcesz go wypróbować, po instalacji wykonaj z głównego katalogu repozytorium osobną konfigurację:

~~~text
cmake -S praktyka -B build/ninja-debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/ninja-debug
ctest --test-dir build/ninja-debug --output-on-failure
~~~

Nie używaj tego samego katalogu, który został wcześniej skonfigurowany dla Makefiles. Ninja wykonuje zależności opisane przez generator; brakujące zależności plików generowanych nadal są błędem projektu. Szybsze uruchamianie błędnego grafu nie zapewnia poprawnego incremental build.

## Drugi przykład

Lokalny plik `CMakeUserPresets.json` może dodać ustawienia konkretnej maszyny. Jest ignorowany przez Git i automatycznie współpracuje z wersjonowanym plikiem projektu. Przykład, umieszczony w katalogu `praktyka`, dodaje własny katalog bez zmiany wspólnego presetu:

~~~json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "local-debug",
      "inherits": "debug",
      "binaryDir": "${sourceDir}/../build/local-debug",
      "cacheVariables": { "CMAKE_EXPORT_COMPILE_COMMANDS": true }
    }
  ]
}
~~~

Konfigurację wybierasz przez `cmake --preset local-debug`. Budowanie tego lokalnego wariantu można wykonać przez jego katalog, a jeśli regularnie go używasz, dopisać odpowiadające mu lokalne build/test presets. Nie zapisuj haseł ani tokenów w cache. Baza komend kompilacji pomaga narzędziom edytora, ale możliwość jej wygenerowania zależy od generatora; nie jest ogólną własnością każdego backendu CMake.

## Porównanie i decyzje

Użyj presetów, gdy kilka osób lub CI ma powtarzać te same konfiguracje. Użyj osobnego pliku toolchain dla istotnych ustawień platformy, kompilatora i sysroot, zwłaszcza przy cross-compilation. Prosty parametr `-D` nadal jest właściwy dla jednorazowego eksperymentu, o ile zapiszesz go razem z wynikiem. Unikaj własnego skryptu, który drugi raz implementuje całą logikę konfiguracji CMake.

**Ćwiczenie 1.** Testy Release przechodzą, chociaż parser zwraca błędny wynik. Jak odróżnić problem konfiguracji od testu usuniętego przez `NDEBUG`?

<details><summary>Rozwiązanie</summary>

Sprawdź komendy budowania i uruchamiany plik, a następnie wprowadź kontrolowaną wadę w kopii. Test ma jawnie zakończyć się niezerowym kodem również w Release. Asercja standardowa nie jest wystarczającym mechanizmem sprawdzania testów, gdy można ją wyłączyć.

</details>

**Ćwiczenie 2.** Dlaczego odziedziczony preset kompilatora nie powinien używać katalogu Debug skonfigurowanego innym kompilatorem?

<details><summary>Rozwiązanie</summary>

Dziedziczenie JSON nie usuwa cache, istniejących obiektów ani wyników wykrywania toolchainu. Oddziel katalogi według istotnych konfiguracji. Czysty nowy build pozwala odróżnić błąd źródła od pozostałości poprzedniego środowiska.

</details>

Źródła: [wersjonowany opis presetów CMake 3.21](https://cmake.org/cmake/help/v3.21/manual/cmake-presets.7.html), [generatory Ninja](https://cmake.org/cmake/help/v3.21/generator/Ninja.html).

## Powiązane tematy

- [CMake](../08_budowanie_i_organizacja/05_cmake.md)
- [Laboratoria i rzeczywiste presety](../praktyka/README.md)
- [Pipeline build/test/analyze](../26_ci_cd_i_release_engineering/01_pipeline_build_test_analyze.md)
