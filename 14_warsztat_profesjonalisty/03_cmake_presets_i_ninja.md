[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# CMake Presets i Ninja

Plik `CMakeLists.txt` opisuje graf celów, lecz nie powinien kodować każdego wyboru konkretnej maszyny. CMake Presets zapisują nazwane sposoby konfiguracji, budowania i testowania. Dzięki temu człowiek i automatyzacja wywołują ten sam wariant bez kopiowania długiej listy `-D`. Ninja jest szybkim wykonawcą grafu wygenerowanego przez CMake; nie zastępuje modelu celów ani wyszukiwania zależności.

~~~cpp
#include <cassert>
#include <span>

constexpr int maximum(std::span<const int> values) {
    int result = values.front();
    for (int value : values) {
        if (value > result) result = value;
    }
    return result;
}

int main() {
    const int data[]{4, 1, 9, 2};
    assert(maximum(data) == 9);
}
~~~

Wersjonowany `CMakePresets.json` zawiera wspólne, przenośne założenia projektu. `CMakeUserPresets.json` służy lokalnym rozszerzeniom, na przykład ścieżce do prywatnego toolchainu; zwykle jest ignorowany przez Git. Sekrety nie powinny trafiać do żadnego presetu w repozytorium. Nawet lokalny plik może przypadkowo zostać udostępniony, więc tokeny najlepiej dostarczać przez mechanizm środowiska wykonawczego.

## Jak to działa krok po kroku

CMake najpierw konfiguruje projekt: czyta skrypty, wykrywa toolchain i generuje pliki systemu budowania w osobnym katalogu. Potem faza build uruchamia generator, na przykład Ninja. Preset konfiguracji nadaje nazwę generatorowi, katalogowi binarnemu, typowi buildu oraz wartościom cache. Preset budowania wskazuje konfigurację bazową i opcjonalny cel. Preset testowy może z kolei opisać CTest.

Zacznij od jednego wariantu `dev-debug`. Wybierz katalog binarny oparty na nazwie presetu, ustaw Ninja i eksport bazy komend kompilacji. Uruchom `cmake --preset dev-debug`, następnie `cmake --build --preset dev-debug` albo osobny preset buildu. Od tej chwili README może podawać krótkie, stabilne polecenia zamiast zależnej od powłoki instrukcji.

Jeżeli potrzebujesz kompilatora wskazanego przez pakiet lub SDK, użyj pliku toolchain i ujawnij go jako kontrolowany parametr. Nie zapisuj absolutnej ścieżki autora w wspólnym presecie. Wspólny plik może definiować ukryty preset bazowy, a presety systemowe dziedziczyć po nim i dodawać tylko różnice.

## Pogłębienie mechanizmu

Cache CMake pamięta wyniki wykrywania i opcje. Zmiana generatora, toolchainu lub istotnej konfiguracji w tym samym katalogu binarnym może pozostawić niespójny stan. Osobny katalog na preset upraszcza diagnozę i pozwala usunąć wyłącznie artefakty konkretnego wariantu. Źródła pozostają nietknięte, ponieważ budowanie odbywa się poza drzewem źródłowym.

Ninja działa dobrze, gdy graf ma wiele małych kroków, ale szybkość nie naprawia źle wyrażonych zależności. W CMake zależności propaguj przez cele: `target_link_libraries`, `target_include_directories` i wymagania kompilacji z odpowiednim zakresem. Globalne flagi utrudniają ponowne użycie biblioteki, a ręczne polecenia bez poprawnych `DEPENDS` prowadzą do nieodtwarzalnych rezultatów.

W projektach wielokonfiguracyjnych typ buildu może być wybierany podczas kompilacji, a nie konfiguracji. Nie zakładaj więc bez sprawdzenia, że każda platforma interpretuje `CMAKE_BUILD_TYPE` identycznie. Presety powinny odzwierciedlać wspierany generator i być testowane na docelowych środowiskach.

## Drugi przykład

Minimalny preset wspólny może wyglądać tak:

~~~json
{
  "version": 6,
  "configurePresets": [
    {
      "name": "dev-debug",
      "displayName": "Development Debug",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/out/build/${presetName}",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": true
      }
    }
  ],
  "buildPresets": [
    { "name": "dev-debug", "configurePreset": "dev-debug" }
  ]
}
~~~

Wersję schematu dobierz do minimalnej wspieranej wersji CMake, zamiast bez potrzeby używać najnowszej funkcji. Po zapisaniu pliku wyświetl listę presetów, skonfiguruj świeży katalog i sprawdź, czy baza komend trafia do oczekiwanego miejsca. Jeśli IDE wymaga linku do `compile_commands.json`, niech będzie to lokalna wygoda, nie ukryty warunek budowania.

## Porównanie i decyzje

Presety są interfejsem użytkownika do CMake, natomiast funkcje i cele w `CMakeLists.txt` opisują sam projekt. Skrypt powłoki bywa potrzebny do orkiestracji wielu narzędzi, lecz nie powinien przepisywać logiki wariantów. Ninja jest dobrym domyślnym generatorem lokalnym, jeśli jest dostępny, ale biblioteka nie powinna wymagać go bez technicznej potrzeby.

Preset wspólny powinien być deterministyczny i bezpieczny do publikacji. Preset użytkownika może dziedziczyć ustawienia oraz dodawać ścieżki zależne od hosta. Jeżeli wariant jest wymagany w CI, przenieś jego istotne opcje do wersjonowanego pliku, aby lokalne odtworzenie nie wymagało zgadywania.

## Powiązane tematy

- [Organizacja projektu CMake](../08_budowanie_i_organizacja/README.md)
- [Analiza statyczna](02_analiza_statyczna_clang_tidy_cppcheck.md)
- [Podręcznik interakcji CMake](https://cmake.org/cmake/help/latest/guide/user-interaction/index.html)
