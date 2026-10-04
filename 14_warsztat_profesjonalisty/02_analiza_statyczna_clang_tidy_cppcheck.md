[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Analiza statyczna: clang-tidy i Cppcheck

Kompilator odpowiada przede wszystkim na pytanie, czy program można przetłumaczyć zgodnie z wybranym językiem i opcjami. Analizator statyczny szuka dodatkowych wzorców: podejrzanego lifetime, błędnego użycia API, nieczytelnych konstrukcji albo odstępstw od polityki projektu. `clang-tidy` korzysta z infrastruktury Clang i informacji o komendzie kompilacji, a Cppcheck stanowi niezależne spojrzenie. Raport nie jest dowodem błędu; jest hipotezą wymagającą weryfikacji.

~~~cpp
#include <cassert>
#include <optional>
#include <string_view>

std::optional<int> parse_port(std::string_view text) {
    if (text.empty()) return std::nullopt;
    int value = 0;
    for (char ch : text) {
        if (ch < '0' || ch > '9') return std::nullopt;
        value = value * 10 + (ch - '0');
        if (value > 65535) return std::nullopt;
    }
    return value;
}

int main() {
    assert(parse_port("443") == 443);
    assert(!parse_port("70000"));
}
~~~

## Jak to działa krok po kroku

Najpierw doprowadź do powstania bazy komend kompilacji. Dla generatorów CMake można włączyć eksport `compile_commands.json`; plik zawiera katalog, kompilator, flagi i ścieżkę każdej jednostki translacji. Bez tych danych analizator może nie znaleźć nagłówków, nie znać makr albo przyjąć zły standard, a raport przestaje odpowiadać prawdziwemu buildowi.

Następnie wybierz niewielki zestaw kontroli. Rozpocznij od grup związanych z błędami i modernizacją, uruchom je na ograniczonym katalogu oraz zapisz konfigurację w `.clang-tidy`. Obejrzyj każde zgłoszenie. Popraw kod, jeśli reguła ujawnia rzeczywisty problem; skonfiguruj regułę, gdy projekt ma inny świadomy kontrakt; wycisz pojedynczą linię dopiero wtedy, gdy potrafisz opisać przyczynę fałszywego alarmu.

Cppcheck może działać bez pełnego modelu konkretnego kompilatora, co bywa użyteczne jako drugie narzędzie. Nadal trzeba przekazać include paths, definicje oraz wariant konfiguracji. Wynik dwóch analizatorów nie musi się pokrywać: używają innych modeli i kompromisów. Zespół powinien definiować, które poziomy zatrzymują pracę, a które trafiają do raportu informacyjnego.

## Pogłębienie mechanizmu

Analiza międzyproceduralna oraz śledzenie ścieżek są kosztowniejsze niż proste dopasowanie składni. Im szerszy model, tym dłuższe wykonanie i większe ryzyko, że narzędzie nie zna zachowania biblioteki zewnętrznej. Adnotacje, poprawne `const`, jawny ownership i małe funkcje ułatwiają zarówno człowiekowi, jak i analizatorowi ustalenie przepływu danych.

Automatyczne poprawki clang-tidy są wygodne, lecz pozostają zmianą kodu. Uruchamiaj je na czystej gałęzi, przeglądaj diff i wykonuj testy. Niektóre poprawki są lokalne, inne zmieniają nagłówki, przeciążenia albo typy i mogą wpłynąć na ABI. Narzędzie nie zna biznesowego znaczenia publicznego kontraktu.

Stabilność raportu zależy od wersji analizatora i biblioteki standardowej. Dlatego konfiguracja powinna być wersjonowana razem z informacją o wspieranym toolchainie. Wprowadzając analizę do starszego projektu, warto utworzyć bazę znanych problemów albo ograniczyć kontrolę do zmienianych plików. Cel to nie wiecznie zielony raport przez masowe wyciszenia, tylko stopniowe zmniejszanie ryzyka.

## Drugi przykład

Mała konfiguracja łatwo ujawnia intencję i koszt:

~~~yaml
---
Checks: >
  -*,
  bugprone-*,
  performance-*,
  modernize-use-nullptr
WarningsAsErrors: 'bugprone-*'
HeaderFilterRegex: 'src/|include/'
FormatStyle: file
...
~~~

Polecenie uruchom na jednym pliku z bazą kompilacji, a potem na całym celu. Jeżeli nagłówek jest analizowany wielokrotnie przez różne jednostki, raport może się powtarzać. Narzędzia uruchamiające wiele plików potrafią równoleglić pracę, lecz w lokalnym hooku lepiej sprawdzać tylko zmieniony zakres. Pełna analiza należy do polecenia developerskiego i CI.

## Porównanie i decyzje

Ostrzeżenia kompilatora są najtańszą pierwszą warstwą i powinny być włączone. clang-tidy dobrze współdzieli semantykę z Clang i oferuje transformacje. Cppcheck dodaje niezależny model, ale podwaja część konfiguracji. Sanitizery wykrywają problemy podczas konkretnego wykonania, a testy sprawdzają zamierzone zachowanie. Warstwy są komplementarne; nie zastępują się wzajemnie.

Nie ustawiaj wszystkich ostrzeżeń jako błędów dla zależności zewnętrznych. Oddziel nagłówki projektu od systemowych oraz analizuj kod, nad którym zespół ma kontrolę. Własny kod może mieć rygorystyczną bramkę, podczas gdy raport z zależności służy obserwacji i aktualizacji.

## Powiązane tematy

- [Formatowanie](01_formatowanie_clang_format_editorconfig.md)
- [Automatyzacja lokalna](06_automatyzacja_lokalna_i_pre_commit.md)
- [Dokumentacja narzędzi Clang](https://clang.llvm.org/docs/ClangTools.html)
