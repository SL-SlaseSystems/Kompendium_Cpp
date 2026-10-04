[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Formatowanie: clang-format i EditorConfig

Formatowanie ma usuwać decyzje, które nie wnoszą informacji do przeglądu kodu. `clang-format` rozumie składnię C++ i układa tokeny według wersjonowanej polityki `.clang-format`. EditorConfig działa poziom wyżej: przekazuje obsługującym go edytorom zasady takie jak kodowanie, wcięcia, końce linii i końcowa nowa linia. Narzędzia uzupełniają się, ale żadne nie ocenia poprawności algorytmu.

~~~cpp
#include <array>
#include <cassert>

constexpr int sum(std::array<int, 4> values) {
    int result = 0;
    for (int value : values) {
        result += value;
    }
    return result;
}

int main() {
    static_assert(sum({1, 2, 3, 4}) == 10);
    assert(sum({2, 4, 6, 8}) == 20);
}
~~~

Najważniejsza decyzja wdrożeniowa brzmi: formatowanie jest deterministyczną transformacją, czy tylko wskazówką edytora? W projekcie zespołowym plik polityki powinien być wersjonowany, a kontrola używać tej samej wersji narzędzia. Duża aktualizacja wersji może zmienić wynik nawet bez modyfikacji konfiguracji, dlatego taki krok warto wykonać w osobnym commicie.

## Jak to działa krok po kroku

Zacznij od stylu bazowego bliskiego praktyce zespołu, na przykład LLVM, Google albo Chromium. Polecenie `clang-format -style=llvm -dump-config` pokazuje pełną konfigurację, lecz nie trzeba jej kopiować w całości. Krótszy plik z `BasedOnStyle` oraz świadomymi wyjątkami łatwiej przeglądać. Następnie uruchom formatowanie na jednym pliku, obejrzyj diff i dopiero później rozszerz zakres.

`.editorconfig` zaczyna się zwykle od `root = true`, aby wyszukiwanie zasad zakończyło się w katalogu projektu. Sekcje dopasowane do rozszerzeń mogą określać `charset = utf-8`, `end_of_line = lf`, `insert_final_newline = true` i szerokość wcięcia. Nie duplikuj w nim każdej opcji clang-format. EditorConfig odpowiada za podstawową postać pliku, natomiast formatter za składnię języka.

Kontrola w trybie tylko do odczytu powinna kończyć się błędem, gdy wynik różni się od pliku. Współczesny clang-format udostępnia opcje przeznaczone do takiego sprawdzania. Jeżeli środowisko ma starszą wersję, porównaj wynik bez nadpisywania źródła. Zawsze zachowuj kod wyjścia, bo to on pozwala zatrzymać lokalny skrypt lub późniejsze CI.

## Pogłębienie mechanizmu

Formatter analizuje tokeny i częściową strukturę programu, ale nie ma pełnej wiedzy semantycznej kompilatora. Makra, wygenerowany kod, osadzone DSL-e i nietypowe konstrukcje mogą wymagać wyłączenia fragmentu. Dyrektywy wyłączające formatowanie stosuj lokalnie i z komentarzem; szerokie wyłączenie katalogu może ukryć zwykły kod aplikacji.

Nie łącz pierwszego masowego formatowania z refaktoryzacją. Taki diff utrudnia ustalenie, które linie zmieniły zachowanie. Najpierw zatwierdź mechaniczną zmianę, a potem logikę. `git blame` ma wtedy mniej szumu, a review może skupić się na właściwym ryzyku. Podobnie aktualizację wersji formattera traktuj jako migrację polityki, nie drobną poprawkę narzędziową.

Editor może formatować przy zapisie, ale repozytorium nie powinno ufać wyłącznie ustawieniom jednej osoby. Deweloper ma otrzymać szybką pętlę, a niezależne polecenie kontrolne ma odtwarzać wynik na każdym wspieranym systemie.

## Drugi przykład

Minimalna polityka projektu jest czytelniejsza od setek odziedziczonych opcji:

~~~yaml
# .clang-format
BasedOnStyle: LLVM
IndentWidth: 4
ColumnLimit: 100
SortIncludes: CaseSensitive
DerivePointerAlignment: false
PointerAlignment: Left
~~~

Towarzyszący `.editorconfig` może stosować cztery spacje dla C++, a dwa dla YAML. Przed dodaniem automatycznej poprawy uruchom formatowanie w trybie sprawdzającym na reprezentatywnych plikach: nagłówku z templates, implementacji, teście i pliku z makrami. Jeżeli wynik jest zaskakujący, najpierw zmień małą opcję lub uprość kod, zamiast dopisywać liczne wyjątki.

## Porównanie i decyzje

EditorConfig zapewnia wspólny fundament także dla Markdown, CMake i plików danych. clang-format jest właściwym narzędziem do składni C/C++. Ręczny przewodnik stylu nadal opisuje nazewnictwo i decyzje projektowe, których formatter nie może wymusić. Najlepszy zestaw jest mały: automatyzuje mierzalne reguły i pozostawia review kwestie znaczenia.

Formatowanie całego repozytorium upraszcza stan docelowy, lecz generuje duży jednorazowy diff. Formatowanie tylko zmienianych plików ogranicza szum, ale przez pewien czas utrzymuje dwa style. Wybór zależy od wielkości kodu, aktywnych gałęzi oraz kosztu konfliktów.

## Powiązane tematy

- [Analiza statyczna](02_analiza_statyczna_clang_tidy_cppcheck.md)
- [Git i praca z repozytorium](05_git_i_praca_z_repozytorium.md)
- [Oficjalna dokumentacja clang-format](https://clang.llvm.org/docs/ClangFormat.html)
