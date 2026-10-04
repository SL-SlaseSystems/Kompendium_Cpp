[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Git i praca z repozytorium

Git przechowuje graf commitów wskazujących na kompletne migawki drzewa. Gałąź jest przesuwanym odwołaniem do commitu, a staging area pozwala zbudować następną migawkę niezależnie od wszystkich zmian w katalogu roboczym. Ten model pomaga tworzyć małe, logiczne zmiany: można poprawić dwa problemy w tym samym pliku, a zatwierdzić je osobno po świadomym wyborze fragmentów.

~~~cpp
#include <cassert>
#include <string>
#include <string_view>

std::string normalized_branch(std::string_view name) {
    std::string result;
    for (char ch : name) {
        result += ch == ' ' ? '-' : ch;
    }
    return result;
}

int main() {
    assert(normalized_branch("fix parser") == "fix-parser");
}
~~~

Nazwy i komunikaty nie naprawią chaotycznej zmiany, ale ułatwiają nawigację. Dobry commit ma jeden możliwy do wyjaśnienia cel, zawiera potrzebne testy i pozostawia repozytorium w działającym stanie. Jego treść opisuje powód oraz istotny kompromis, których sam diff nie ujawnia. Historia jest wtedy narzędziem diagnostycznym, a nie tylko archiwum.

## Jak to działa krok po kroku

Przed pracą sprawdź status i aktualną gałąź. Po edycji obejrzyj diff katalogu roboczego, uruchom wąskie testy, a następnie wybierz do stage tylko zamierzony zakres. Ponownie obejrzyj diff staged, ponieważ to właśnie on trafi do commitu. Dopiero wtedy zapisz komunikat. Po commicie sprawdź status, aby przypadkowe pliki, dane lub artefakty buildu nie zostały bez opieki.

Interaktywny stage pozwala wybierać hunki, lecz nie jest zamiennikiem dobrego planu. Jeśli jeden fragment wymaga sztucznego rozcinania linii, najpierw uporządkuj zmianę w katalogu roboczym. Pliki wygenerowane oraz katalogi build powinny mieć jasno ustaloną politykę. Ignorowanie nie usuwa pliku już śledzonego i nie chroni sekretu, który wcześniej znalazł się w historii.

Przed wysłaniem gałęzi zsynchronizuj się z bazą zgodnie z zasadami zespołu. Rebase odtwarza własne commity na nowej bazie i zmienia ich identyfikatory; merge tworzy commit łączący historie. Nie przepisuj publicznej historii współdzielonej bez koordynacji. Po rozwiązaniu konfliktu przeczytaj cały wynik, nie tylko usuń znaczniki, i uruchom testy obejmujące obie strony zmiany.

## Pogłębienie mechanizmu

Commit identyfikuje zawartość, rodziców i metadane. Zmiana rodzica podczas rebase daje nowy identyfikator nawet przy podobnym patchu. To tłumaczy, dlaczego wymuszone wysłanie może odłączyć pracę innej osoby. Jeżeli polityka dopuszcza przepisywanie własnej gałęzi, stosuj bezpieczniejszą kontrolę oczekiwanego stanu zdalnego zamiast ślepego nadpisania.

Konflikt tekstowy oznacza, że Git nie potrafił automatycznie połączyć fragmentów; brak konfliktu nie dowodzi poprawności semantycznej. Dwie gałęzie mogą niezależnie zmienić protokół, nazwy lub kolejność inicjalizacji w różnych plikach. Dlatego po integracji potrzebne są testy i review zachowania, a nie wyłącznie zielony wynik operacji Git.

Bisect wykorzystuje graf historii do zawężania pierwszego złego commitu. Działa najlepiej, gdy każdy krok się buduje i ma pojedynczy cel. Można zautomatyzować test, ale jego kod wyjścia musi rozróżniać dobry, zły i niemożliwy do sprawdzenia stan. Historia z wielkimi, mieszanymi commitami zmniejsza wartość tej techniki.

## Drugi przykład

Przepływ przed commitem powinien być jawny i możliwy do zatrzymania:

~~~bash
git status --short
git diff
git add -p
git diff --cached
cmake --build --preset dev-debug
ctest --preset dev-debug
git commit
~~~

To przykład kolejności, nie skrypt do bezrefleksyjnego kopiowania. Nazwy presetów muszą istnieć w projekcie, a test może wymagać innego polecenia. Ważne są punkty kontroli: zobaczenie zmian przed stage, zobaczenie dokładnej migawki przed commitem i weryfikacja na tej samej konfiguracji, którą dokumentuje repozytorium.

Opis pull requestu powinien podać problem, zakres, sposób weryfikacji i ryzyko. Zrzut ekranu może uzupełniać zmianę interfejsu, ale nie zastępuje testu. Jeżeli migracja wymaga kilku wdrożeń, opisz kolejność i możliwość wycofania. Recenzent ma wtedy warunki do oceny rozwiązania, zamiast rekonstruować intencję z nazw plików.

## Porównanie i decyzje

Merge zachowuje topologię integracji, rebase tworzy liniową opowieść własnej pracy, a squash scala wiele kroków w jeden commit. Żadna strategia nie jest zawsze najlepsza. Liczy się spójna polityka, ochrona współdzielonej historii i to, czy finalne commity są użyteczne przy review, revert oraz bisect.

Duży commit bywa uzasadniony mechaniczną migracją, ale powinien być oddzielony od zmian zachowania. Małe commity nie mogą natomiast pozostawiać kodu celowo nieskompilowanego tylko po to, by zmniejszyć liczbę linii. Jednostką jest kompletna decyzja, nie arbitralny rozmiar diffu.

## Powiązane tematy

- [Formatowanie](01_formatowanie_clang_format_editorconfig.md)
- [Automatyzacja lokalna](06_automatyzacja_lokalna_i_pre_commit.md)
- [Oficjalna dokumentacja Git](https://git-scm.com/docs)
