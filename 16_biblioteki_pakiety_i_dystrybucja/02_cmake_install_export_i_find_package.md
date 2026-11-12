[← Spis treści](../README.md)

# CMake install export i find package

Pakiet CMake jest opisem wymagań biblioteki dla obcego projektu. Skopiowanie archiwum i katalogu nagłówków nie wystarcza, gdy konsument potrzebuje również odpowiedniego standardu języka, definicji kompilacji albo zależności do linkowania. Dobrze przygotowany pakiet pozwala napisać `find_package` oraz `target_link_libraries` i otrzymać te wymagania przez cel importowany. Autor biblioteki odpowiada wtedy za jeden spójny kontrakt użycia zamiast instrukcji ręcznego dopisywania ścieżek.

Poniższy przykład wymaga CMake co najmniej 3.23; opis mechanizmów odwołuje się do dokumentacji wersji 3.31. Biblioteka `Meter` udostępnia małą funkcję, ale jej konfiguracja jest taka sama jak dla większego komponentu. Istotny jest test instalacji: projekt producenta może kompilować się dzięki przypadkowym globalnym ustawieniom, których konsument nie otrzyma. Działający `add_subdirectory` nie jest zatem dowodem poprawności dystrybucji.

## Jak to działa krok po kroku

Przykład ma następujące pliki. Ścieżki są względne wobec katalogu producenta; zapisujemy je jako osobne pliki, bez etykiet z nawiasów kwadratowych. Nagłówek jest publiczny, implementacja prywatna. Użycie `STATIC` jest świadome: upraszcza uruchomienie przykładu, lecz nie usuwa zależności potrzebnych przy ostatecznym linkowaniu aplikacji.

~~~text
meter/
  CMakeLists.txt
  cmake/MeterConfig.cmake.in
  include/meter/meter.hpp
  src/meter.cpp

[include/meter/meter.hpp]
#pragma once
namespace meter { int twice(int value); }

[src/meter.cpp]
#include <meter/meter.hpp>
int meter::twice(int value) { return value * 2; }
~~~

Implementacja zakłada argument, którego podwojenie mieści się w `int`; konsument poniżej używa wartości 21. To przykład pakowania, a nie biblioteka sprawdzanej arytmetyki. Gdyby ten warunek był częścią publicznego produktu, należałoby opisać go w dokumentacji API lub zmienić typ wyniku.

~~~cmake
cmake_minimum_required(VERSION 3.23)
project(Meter VERSION 1.2.0 LANGUAGES CXX)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

add_library(meter STATIC src/meter.cpp)
add_library(Meter::meter ALIAS meter)
target_compile_features(meter PUBLIC cxx_std_23)
target_include_directories(meter PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

install(TARGETS meter EXPORT MeterTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT MeterTargets FILE MeterTargets.cmake
    NAMESPACE Meter:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Meter)

configure_package_config_file(cmake/MeterConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/MeterConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Meter)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/MeterConfigVersion.cmake
    VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/MeterConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/MeterConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Meter)
~~~

`install(TARGETS)` kopiuje artefakt i przypisuje cel do zestawu eksportu. `install(EXPORT)` generuje jego opis dla konsumenta. Alias służy pracy wewnątrz projektu, natomiast `NAMESPACE Meter::` tworzy nazwę celu importowanego przy odczycie instalacji. Nazwy mogą być jednakowe, choć pochodzą z innych mechanizmów. Plik konfiguracyjny udostępnia zestaw celów i sprawdza wymagane komponenty:

~~~cmake
# cmake/MeterConfig.cmake.in
@PACKAGE_INIT@
include("${CMAKE_CURRENT_LIST_DIR}/MeterTargets.cmake")
check_required_components(Meter)
~~~

Nagłówki mają inny adres w drzewie źródeł i w instalacji. `BUILD_INTERFACE` wskazuje lokalny katalog potrzebny podczas kompilacji producenta. `INSTALL_INTERFACE` opisuje ścieżkę względem prefiksu instalacji, dzięki czemu eksport nie utrwala prywatnej ścieżki autora. Nie wpisujemy tam katalogów nagłówków zewnętrznych bibliotek; ich wymagania powinny pochodzić z ich własnych celów. Te zasady wyjaśnia [przewodnik eksportu CMake 3.31](https://cmake.org/cmake/help/v3.31/guide/importing-exporting/index.html).

## Pogłębienie mechanizmu

Modyfikatory `PRIVATE`, `PUBLIC` i `INTERFACE` określają dwa kierunki użycia. `PRIVATE` jest potrzebne do zbudowania celu, `INTERFACE` jego konsumentom, a `PUBLIC` obu stronom. Jeśli publiczny nagłówek używa typu z zależności, zwykle jej wymagania muszą być publiczne. Prywatne szczegóły implementacji nie powinny natomiast narzucać konsumentowi przypadkowych flag diagnostycznych. Szczególnie niebezpieczne są globalne `include_directories` i `link_directories`: lokalnie maskują brak deklaracji przy konkretnym celu.

Dla biblioteki statycznej nawet prywatna zależność do linkowania może być potrzebna końcowej aplikacji. Archiwum nie jest gotowym wykonywalnym plikiem i nie wchłania automatycznie innych archiwów. Eksport może zapisać zależność przez cel, również z ograniczeniem do linkowania. Konfiguracja pakietu musi zapewnić istnienie takiego celu przed załadowaniem eksportu. Nie należy wnioskować z samego słowa `PRIVATE`, że można pominąć zależność w dystrybucji.

Plik wersji odpowiada na pytanie, czy żądana wersja pakietu jest akceptowana według zadeklarowanej polityki. `SameMajorVersion` uznaje zgodność w obrębie głównej wersji przy spełnieniu wymagania wersji, lecz nie analizuje ABI ani znaczenia funkcji. To obietnica autora. Zmiana układu publicznej klasy może naruszyć zgodność binarną mimo wygenerowanego pliku wersji. Dokładne reguły i ograniczenia generatorów opisuje [CMakePackageConfigHelpers 3.31](https://cmake.org/cmake/help/v3.31/module/CMakePackageConfigHelpers.html).

Wielokonfiguracyjny generator wymaga wskazania konfiguracji przy budowaniu i instalowaniu. Dlatego poniższe polecenia używają `--config Release`; dla generatora jednokonfiguracyjnego wybieramy dodatkowo `CMAKE_BUILD_TYPE=Release` przy konfiguracji. W produkcji trzeba też ustalić zachowanie bibliotek współdzielonych, RPATH, symboli eksportowanych oraz zgodność konfiguracji runtime. Sam eksport CMake nie rozwiązuje tych zagadnień platformy.

## Drugi przykład

Niezależny konsument znajduje pakiet w trybie `CONFIG`, co jasno wybiera konfigurację dostarczoną przez producenta. Nie używa `add_subdirectory`, nagłówków z katalogu źródłowego ani ręcznej ścieżki do archiwum. Plik `consumer/main.cpp` jest kompletnym programem. Blok oznaczono `cpp,notest`, ponieważ wymaga nagłówka oraz biblioteki z wieloplikowego projektu Meter; sprawdzamy go przez zbudowanie i uruchomienie całego niezależnego konsumenta, zgodnie z poleceniami poniżej.

~~~cpp,notest
#include <meter/meter.hpp>

int main() {
    return meter::twice(21) == 42 ? 0 : 1;
}
~~~

~~~cmake
# consumer/CMakeLists.txt
cmake_minimum_required(VERSION 3.23)
project(MeterConsumer LANGUAGES CXX)
find_package(Meter 1.2 CONFIG REQUIRED)
add_executable(consumer main.cpp)
target_link_libraries(consumer PRIVATE Meter::meter)
~~~

Przykładowa sesja zakłada katalogi `meter` i `consumer` obok siebie. Prefiks jest celowo osobnym katalogiem. Po instalacji zmieniamy jego nazwę i dopiero wtedy konfigurujemy konsumenta. To wykrywa część błędów relokacji oraz przypadkowych bezwzględnych ścieżek.

~~~sh
cmake -S meter -B meter-build -DCMAKE_BUILD_TYPE=Release
cmake --build meter-build --config Release
cmake --install meter-build --config Release --prefix "$PWD/stage"
mv stage relocated
cmake -S consumer -B consumer-build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$PWD/relocated"
cmake --build consumer-build --config Release
./consumer-build/consumer
~~~

Dla generatora wielokonfiguracyjnego plik wykonywalny może leżeć w `consumer-build/Release`. Mocniejszy test przenosi samą instalację do oddzielnego zadania CI, które nie otrzymuje źródeł producenta ani jego katalogu budowania. Budowanie obu projektów w jednym środowisku pozwala niechcący znaleźć brakujące pliki przez cache lub zmienne otoczenia.

Jeżeli `meter` korzysta z `Threads::Threads`, producent wywołuje `find_package(Threads REQUIRED)` i wiąże cel przez `target_link_libraries`. Konfiguracja instalowanego pakietu musi znaleźć zależność przed wczytaniem eksportu:

~~~cmake
@PACKAGE_INIT@
include(CMakeFindDependencyMacro)
find_dependency(Threads)
include("${CMAKE_CURRENT_LIST_DIR}/MeterTargets.cmake")
check_required_components(Meter)
~~~

`find_dependency` przekazuje właściwe zachowanie `QUIET` i `REQUIRED` z zewnętrznego wyszukiwania oraz kończy przetwarzanie konfiguracji, gdy zależności brakuje. Opisuje to [CMakeFindDependencyMacro 3.31](https://cmake.org/cmake/help/v3.31/module/CMakeFindDependencyMacro.html). W przypadku cudzej biblioteki wersję i wymagane komponenty podajemy zgodnie z rzeczywistym kontraktem pakietu.

Relokowalność sprawdzamy dla całego opublikowanego zestawu, również plików danych i bibliotek współdzielonych. Generator wyrażeń nie naprawi bezwzględnej ścieżki wpisanej ręcznie do własnego pliku konfiguracji. Dobrą kontrolą jest wyszukanie ścieżki źródeł oraz katalogu budowania w zainstalowanych plikach tekstowych, a następnie próba konsumpcji po przeniesieniu prefiksu. Wciąż potrzebny jest test wykonania aplikacji, bo pomyślne linkowanie nie dowodzi, że loader znajdzie bibliotekę współdzieloną na maszynie odbiorcy.

Pakiet nie powinien też publikować wszystkich opcji użytych podczas jego budowania. Flagi ostrzeżeń, ścieżka do lokalnego SDK i ustawienia narzędzi analizy zwykle należą do producenta. Wymagania interfejsu obejmują natomiast rzeczy potrzebne konsumentowi do poprawnego skompilowania nagłówków oraz połączenia kodu. Rozdzielenie tych kategorii pozwala konsumentowi zachować własną politykę diagnostyczną i uniknąć zależności od układu katalogów autora.

## Porównanie i decyzje

`add_subdirectory` integruje kod źródłowy z bieżącym grafem budowania. `find_package(CONFIG)` konsumuje opublikowany opis pakietu. Pierwsze rozwiązanie jest wygodne w monorepo, drugie sprawdza granicę dystrybucji. Warto testować oba, gdy biblioteka wspiera oba tryby. Bezpośrednie przekazanie pliku `.a` usuwa informacje o wymaganiach i przenosi odpowiedzialność na użytkownika; cel importowany zachowuje je w grafie zależności.

**Zadanie 1.** Konsument buduje się tylko wtedy, gdy istnieje źródłowy katalog producenta. Gdzie szukać błędu?

<details><summary>Rozwiązanie</summary>

Sprawdź eksportowane `INTERFACE_INCLUDE_DIRECTORIES`, wygenerowany config i publiczne zależności. Instalacja nie powinna wskazywać źródeł autora. Użyj względnego `INSTALL_INTERFACE`, zainstaluj publiczne nagłówki i powtórz test w odizolowanym konsumencie.

</details>

**Zadanie 2.** Publiczny nagłówek zawiera `Vendor::Value`, lecz `Vendor::core` jest podłączony prywatnie. Co poprawić?

<details><summary>Rozwiązanie</summary>

Wymagania potrzebne do interpretacji publicznego nagłówka muszą dotrzeć do konsumenta, zwykle przez zależność `PUBLIC`. Config powinien wykonać `find_dependency(Vendor CONFIG ...)` przed importem celów. Potwierdź zmianę osobnym projektem bez ręcznych ścieżek do Vendor.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Typy bibliotek i struktura pakietu](01_typy_bibliotek_i_struktura_pakietu.md)
- [Wersjonowanie ABI i publikacja artefaktów](05_wersjonowanie_abi_i_publikacja_artefaktow.md)
