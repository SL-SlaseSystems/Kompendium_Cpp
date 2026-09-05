[← Spis treści](../README.md)

# Conan, vcpkg i zależności

C++ nie ma jednego standardowego menedżera pakietów. Conan i vcpkg są popularnymi narzędziami ekosystemu, ale mają inne modele wersji, binariów, rejestrów i integracji. CMake potrafi odnaleźć lub budować zależności, lecz sam nie rozwiązuje wszystkich problemów zarządzania wersjami i wariantami ABI.

~~~text
# Przykładowa intencja w CMake po dostarczeniu pakietu przez menedżer:
find_package(fmt CONFIG REQUIRED)
target_link_libraries(app PRIVATE fmt::fmt)
~~~

Imported target `fmt::fmt` powinien nieść include paths, wymagane definicje i właściwości linkowania. To bezpieczniejsze niż ręczne składanie ścieżek do plików. Dokładne polecenie instalacji i nazwa targetu zależą od pakietu oraz wybranego menedżera.

Zależność binarna musi pasować pod względem architektury, kompilatora, runtime library, trybu debug/release, opcji ABI i często wersji biblioteki standardowej. Sam zgodny numer semantyczny nie gwarantuje zgodności binarnej. Reproducible build wymaga zablokowania wersji receptur, źródeł, opcji i toolchainu.

Biblioteka header-only usuwa krok linkowania, ale nie jest pozbawiona kosztów: może zwiększać czas kompilacji, liczbę instancjacji i ryzyko ODR przy niespójnych makrach konfiguracyjnych. FetchContent upraszcza małe projekty, lecz pobieranie podczas konfiguracji utrudnia środowiska hermetyczne i audyt supply chain.

## Jak to działa krok po kroku

Proces korzystania z pakietu ma kilka oddzielnych wyników. Najpierw manifest lub receptura określa żądane biblioteki i wersje. Menedżer rozwiązuje graf zależności, wybiera warianty oraz pobiera albo buduje pakiety. Następnie generuje lub dostarcza integrację z CMake. Dopiero `find_package` odnajduje gotowy pakiet i tworzy imported target, z którego korzysta aplikacja.

W Conan 2 profil opisuje ustawienia środowiska, takie jak system, architektura, kompilator i tryb budowania. Przy kompilacji krzyżowej rozróżnia się kontekst build, na którym działają narzędzia, oraz host, dla którego powstaje kod aplikacji. Generator uruchamiany w procesie budowania musi działać na komputerze budującym; jego biblioteki wynikowe mogą być przeznaczone dla innej architektury. Zmieszanie tych kontekstów daje błędy, których sama zmiana include path nie naprawi.

W vcpkg manifest opisuje zależności projektu, a triplet wybiera istotne cechy docelowego wariantu, między innymi architekturę i model linkowania. Toolchain integruje wyszukiwanie pakietów z CMake. Instalacja pakietu w cache nie powoduje jeszcze, że dowolny katalog budowania zobaczy go automatycznie. Konfiguracja projektu musi używać zgodnej integracji i właściwego wariantu.

## Pogłębienie mechanizmu

Wersja źródłowa, rewizja receptury i wariant binarny są odrębnymi osiami. Ta sama wersja biblioteki może dawać różne binaria dla Debug, Release, różnych opcji, bibliotek standardowych lub ustawień runtime. Zgodny nagłówek z niezgodnym binarium potrafi skompilować się poprawnie, a następnie powodować błędy linkowania lub niepoprawne wykonanie. Szczególnie ryzykowne są makra zmieniające layout typów i przekazywanie obiektów biblioteki standardowej przez niezgodne granice ABI.

Lockfile Conan utrwala wybrane informacje o rozwiązywaniu wersji i rewizji grafu; nie zastępuje wersjonowania profili, opcji i samego kompilatora. Baseline vcpkg wiąże domyślne wersje portów z określoną rewizją rejestru. Manifest bez utrwalonego baseline może z czasem rozwiązać się inaczej. Po aktualizacji zależności przeglądaj różnicę grafu, nie tylko jedną bezpośrednio zmienioną nazwę pakietu.

Cache binarny przyspiesza powtarzalne budowanie, ale klucz cache musi poprawnie uwzględniać wymagane cechy wariantu. Cache nie jest także źródłem prawdy o tym, dlaczego pakiet zbudowano z określonymi opcjami. Receptury, profile, manifesty, lockfile i konfigurację toolchainu powinno dać się odtworzyć w czystym środowisku. Taki test wykrywa zależność od przypadkowo zainstalowanej biblioteki systemowej.

Menedżer pakietów może wykonywać receptury i systemy budowania zależności. Wybór zaufanego rejestru, kontrola integralności źródeł oraz sprawdzenie licencji są konkretną częścią włączenia cudzej biblioteki do produktu. Nie wymagają pisania własnego menedżera; wymagają utrwalenia pochodzenia i świadomej aktualizacji. Biblioteka header-only również jest kodem wykonywanym w aplikacji, mimo braku osobnego archiwum przy linkowaniu.

## Drugi przykład

Poniższy wariant pokazuje Conan 2 i integrację przez CMakeToolchain oraz CMakeDeps. Wersja fmt jest przykładowo przypięta; nie jest deklaracją najnowszego wydania ani rekomendacją wersji dla nowego produktu.

~~~text
# conanfile.txt
[requires]
fmt/11.0.2

[generators]
CMakeDeps
CMakeToolchain

# CMakeLists.txt
cmake_minimum_required(VERSION 3.28)
project(package_example LANGUAGES CXX)
find_package(fmt CONFIG REQUIRED)
add_executable(app main.cpp)
target_compile_features(app PRIVATE cxx_std_23)
target_link_libraries(app PRIVATE fmt::fmt)

# main.cpp
#include <fmt/format.h>
int main() { fmt::print("answer = {}\n", 42); }

# Pierwsze wykrycie profilu należy przejrzeć przed użyciem:
conan profile detect
conan install . --output-folder=build --build=missing -s build_type=Release
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake \
    -DCMAKE_BUILD_TYPE=Release
cmake --build build
~~~

Przy tym układzie wygenerowany toolchain znajduje się w katalogu `build`, a względna ścieżka jest rozpatrywana w kontekście konfiguracji CMake. Jeśli receptura korzysta z własnego layoutu, miejsce generatorów może być inne: czytaj rzeczywisty wynik `conan install`. Dla generatora wielokonfiguracyjnego wybór Release następuje także przy budowaniu, a instalowane konfiguracje pakietów muszą odpowiadać używanemu wariantowi.

## Porównanie i decyzje

Conan daje rozbudowany model receptur i pakietów binarnych, przydatny również dla bibliotek wewnętrznych. vcpkg pasuje do pracy opartej na portach, manifestach i integracji toolchain. `FetchContent` może wystarczyć dla niewielkiej, kontrolowanej zależności budowanej ze źródeł, ale trzeba przypiąć jej identyfikator i rozważyć dostęp sieci podczas konfiguracji. Żaden z tych mechanizmów nie gwarantuje sam zgodności ABI całego procesu.

**Ćwiczenie.** Dlaczego przypięcie tylko `fmt/11.0.2` nie jest pełnym opisem powtarzalnego buildu? **Odpowiedź:** pozostają rewizje receptury, zależności przechodnie, opcje, profile, kompilator, biblioteka standardowa i środowisko budowania. Numer wersji określa jedną część wejścia. Dobra procedura utrwala resztę i potrafi wykonać czyste odtworzenie bez korzystania z nieudokumentowanego stanu maszyny.

Źródła: [Conan 2 i CMake](https://docs.conan.io/2/tutorial/consuming_packages/build_simple_cmake_project.html), [lockfiles Conan](https://docs.conan.io/2/tutorial/versioning/lockfiles.html), [manifesty vcpkg](https://learn.microsoft.com/en-us/vcpkg/concepts/manifest-mode), [wersjonowanie vcpkg](https://learn.microsoft.com/en-us/vcpkg/users/versioning).

## Powiązane tematy

- [CMake](05_cmake.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
- [Testowanie](../09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
