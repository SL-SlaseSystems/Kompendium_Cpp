[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Automatyzacja lokalna i pre-commit

Lokalna automatyzacja skraca drogę od błędu do informacji zwrotnej. Hook uruchamiany przed commitem może sprawdzić końce plików, formatowanie albo tanią analizę zmienionego zakresu. Nie jest jednak granicą bezpieczeństwa: użytkownik może go pominąć, środowisko może być źle skonfigurowane, a kod zewnętrzny może ominąć lokalny komputer. Te same istotne reguły muszą później działać w kontrolowanym CI.

~~~cpp
#include <cassert>
#include <string_view>

constexpr bool has_forbidden_tab(std::string_view text) {
    return text.find('\t') != std::string_view::npos;
}

int main() {
    static_assert(!has_forbidden_tab("four spaces"));
    assert(has_forbidden_tab("name\tvalue"));
}
~~~

Framework pre-commit przechowuje listę repozytoriów hooków, ich wersje oraz argumenty w pliku konfiguracyjnym. Instalacja hooka w lokalnym `.git` jest jednorazową czynnością użytkownika; wersjonowana konfiguracja opisuje wspólną politykę. To ważne rozróżnienie: świeży klon ma definicję kontroli, ale nie wykonuje arbitralnego kodu automatycznie bez decyzji programisty lub procesu CI.

## Jak to działa krok po kroku

Najpierw wybierz kontrole bardzo szybkie i deterministyczne. Usuwanie końcowych spacji, sprawdzenie końcowej nowej linii i walidacja prostych formatów dają natychmiastową wartość. Dodaj wersjonowaną konfigurację z przypiętymi wersjami hooków. Następnie użytkownik instaluje środowisko narzędzia i hook dla danego klonu. Uruchom wszystkie reguły ręcznie na całym repozytorium, zanim zaczniesz polegać na automatycznym wywołaniu.

Hook otrzymuje zwykle listę plików zakwalifikowanych do commitu. Narzędzie, które samo skanuje całe repozytorium, wymaga odpowiedniej konfiguracji przekazywania nazw. Jeśli hook poprawia plik, commit powinien zostać zatrzymany: użytkownik przegląda nowy diff i ponownie dodaje wynik do stage. Ciche zmienianie migawki w trakcie commitu utrudnia zrozumienie tego, co rzeczywiście zatwierdzono.

Pełne testy integracyjne, analiza całego projektu i wieloplatformowy build są zwykle zbyt wolne dla każdego commitu. Udostępnij osobne polecenie `check` lub skrypt, który uruchamia szerszy zestaw przed wysłaniem. Lokalny hook ma chronić krótką pętlę, a nie karać programistę za częste, małe commity.

## Pogłębienie mechanizmu

Hook jest kodem pobieranym lub uruchamianym w kontekście repozytorium. Przypinanie rewizji poprawia powtarzalność, ale przed aktualizacją nadal trzeba ocenić źródło i zmiany zależności. W środowisku o podwyższonym ryzyku można używać własnych mirrorów, sum kontrolnych i ograniczonych runnerów. Sama popularność hooka nie jest gwarancją bezpieczeństwa łańcucha dostaw.

Cache środowisk przyspiesza kolejne wywołania, więc pierwsze uruchomienie może być zauważalnie dłuższe. Dokumentacja projektu powinna podać wymagane runtime'y oraz komendę czyszczenia lub ponownej instalacji. Gdy narzędzie C++ zależy od bazy komend kompilacji, hook musi wiedzieć, jak powstał katalog build; ukryte założenie o istniejącym pliku prowadzi do różnych wyników na różnych maszynach.

Reguła może używać `language: system`, lecz wtedy wersja programu nie jest zarządzana przez framework. To bywa sensowne dla kompilatora dostarczanego przez projekt, pod warunkiem że README i presety definiują wspierany toolchain. Alternatywnie hook może izolować środowisko, kosztem czasu oraz dodatkowych pobrań. W obu wariantach błędy konfiguracji powinny kończyć proces, nie być traktowane jako sukces.

## Drugi przykład

Konfiguracja pokazuje różnicę między gotowym hookiem a lokalnym poleceniem:

~~~yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: local
    hooks:
      - id: verify-cpp-format
        name: verify C++ formatting
        entry: scripts/check-format.sh
        language: system
        files: '\.(cpp|hpp|cc|hh)$'
~~~

Numer wersji jest przykładem i przed użyciem należy wybrać zweryfikowaną, wspieraną rewizję. Lokalny skrypt powinien przyjmować ścieżki przekazane przez framework, poprawnie obsługiwać spacje w nazwach i zwracać niezerowy kod przy różnicy. Nie zapisuj w nim ścieżki z komputera autora. Pełne uruchomienie wszystkich hooków pozostaje osobną komendą developerską.

## Porównanie i decyzje

Natywne hooki Git są lekkie, ale katalog `.git/hooks` nie jest normalnie wersjonowany i każdy zespół musi rozwiązać instalację. Framework pre-commit wersjonuje deklarację oraz zarządza środowiskami wielu języków. Skrypt `check` jest najprostszy do debugowania i może spinać narzędzia C++, natomiast nie uruchomi się automatycznie bez hooka lub świadomego polecenia.

Najlepszy układ ma trzy prędkości: natychmiastowe reguły dla zmienionych plików, pełną lokalną kontrolę przed wysłaniem i niezależne CI na czystym środowisku. Duplikacja samej polityki powinna być minimalna — warstwy wywołują wspólne skrypty lub presety, zamiast utrzymywać trzy różne listy flag.

## Powiązane tematy

- [CMake Presets i Ninja](03_cmake_presets_i_ninja.md)
- [Git i praca z repozytorium](05_git_i_praca_z_repozytorium.md)
- [Dokumentacja pre-commit](https://pre-commit.com/)
