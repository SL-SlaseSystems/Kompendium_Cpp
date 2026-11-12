[← Spis treści](../README.md)

# Regresje git bisect i reprodukcja

Regresja to obserwowalna własność, która działała w znanym stanie i przestała działać w późniejszym. Zanim zaczniemy przeglądać historię, potrzebujemy testu rozróżniającego te dwa stany. „Czasem pojawia się błąd” jest opisem problemu, lecz zbyt słabym predykatem dla automatycznego wyszukiwania. Najpierw utrwalamy dane, środowisko i oczekiwane zachowanie. Dopiero potem `git bisect` może zawężać zbiór podejrzanych zmian.

Narzędzie znajduje granicę między wynikami testu w grafie historii. Nie wyjaśnia mechanizmu błędu i nie gwarantuje, że wskazany commit jest jedyną przyczyną. Zmiana może ujawnić wcześniejszy błąd, wejść w interakcję z konfiguracją albo jedynie zmienić prawdopodobieństwo wyścigu. Wynik bisection jest bardzo użyteczną hipotezą popartą historią, którą trzeba potwierdzić na wskazanym commicie i jego rodzicu.

## Jak to działa krok po kroku

Przygotowujemy reprodukcję poza repozytorium: niezmienny plik wejściowy, skrypt sterujący i zapis wersji narzędzi. W raporcie umieszczamy identyfikator commita, kompilator, flagi, wersje zależności, system i komendę wykonania. Dla problemu losowego zachowujemy ziarno oraz warunki współbieżności. Sekrety i rzeczywiste dane użytkowników zastępujemy minimalnym zestawem zachowującym objaw. Suma kontrolna danych pozwala wykryć przypadkową zmianę reprodukcji podczas długiego dochodzenia.

Następnie uruchamiamy identyczny test na obu końcach zakresu. Dobry commit musi przejść, a zły odtworzyć wybrany objaw. Nie wystarcza informacja, że poprzednie wydanie „było stabilne”: mogło być budowane innym kompilatorem albo korzystać z innej usługi. Jeśli stary kod nie daje się zbudować w obecnym środowisku, trzeba odtworzyć dawny toolchain lub jawnie oznaczyć brak możliwości oceny.

Aby zachować bieżące zmiany, tworzymy osobny worktree z odłączonym `HEAD`. Poniższe nazwy tagów są przykładowe i należy wybrać istniejące granice własnego problemu. Ścieżka skryptu jest bezwzględna, ponieważ kolejne checkouty nie powinny podmieniać samego testu.

~~~sh
good_ref=v1.4.0
bad_ref=v1.5.0
scratch=$(mktemp -d)
repro_tree="$scratch/tree"
git worktree add --detach "$repro_tree" "$bad_ref"
git -C "$repro_tree" bisect start "$bad_ref" "$good_ref"
git -C "$repro_tree" bisect run sh /absolute/repro/check-regression.sh
git -C "$repro_tree" bisect log > /absolute/repro/bisect.log
git -C "$repro_tree" bisect reset
~~~

Po zapisaniu potrzebnych artefaktów i sprawdzeniu `git -C "$repro_tree" status --short` można usunąć worktree przez `git worktree remove "$repro_tree"`. Nie potrzeba `reset --hard` ani czyszczenia katalogu, w którym użytkownik pracuje nad inną zmianą. Worktree ma osobne pliki robocze, ale korzysta ze wspólnego repozytorium; nie stanowi izolacji dla zewnętrznej bazy, cache czy konta chmurowego. Szczegóły opisuje [dokumentacja git-worktree](https://git-scm.com/docs/git-worktree).

## Pogłębienie mechanizmu

Skrypt przekazany do `git bisect run` jest klasyfikatorem. Kod zakończenia `0` oznacza dobry stan, `1` może oznaczać wykrytą regresję, a `125` brak możliwości przetestowania danego commita. Technicznie inne wartości od 1 do 127, z wyjątkiem 125, również oznaczają zły stan. Wartości poza tym zakresem przerywają automatyczny przebieg. Dlatego brak polecenia, zwykle sygnalizowany przez powłokę kodem 127, nie powinien przypadkowo oznaczać znalezienia regresji. Reguły podaje [git-bisect](https://git-scm.com/docs/git-bisect).

Poniższy kompletny skrypt POSIX zakłada, że projekt ma cel `regression_probe`. Program ten przyjmuje utrwalony plik wejściowy i zwraca dokładnie `0` dla poprawnego zachowania, `1` dla badanego objawu oraz `2` dla błędu infrastruktury. Katalog kompilacji powstaje poza źródłami od nowa dla każdego commita, więc stary cache CMake nie zatruwa kolejnych wyników.

~~~sh
#!/bin/sh
# /absolute/repro/check-regression.sh
set -u
fixture=/absolute/repro/input.bin
command -v cmake >/dev/null 2>&1 || exit 128
[ -r "$fixture" ] || exit 128
build_dir=$(mktemp -d) || exit 128
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM

if ! cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=Release; then
    exit 125
fi
if ! cmake --build "$build_dir" --target regression_probe; then
    exit 125
fi
"$build_dir/regression_probe" --input "$fixture"
result=$?
case "$result" in
    0) exit 0 ;;
    1) exit 1 ;;
    2) exit 128 ;;
    *) exit 128 ;;
esac
~~~

`125` nie oznacza „raczej dobrze”. Pominięcie commitów w pobliżu granicy może pozostawić kilka nierozróżnialnych kandydatów. Wtedy raportujemy zbiór możliwości albo poprawiamy środowisko i powtarzamy test. Jeżeli badanym problemem jest właśnie przerwane budowanie, nie wolno klasyfikować każdej awarii kompilacji jako `125`: określony oczekiwany błąd powinien oznaczać zły stan. Klasyfikacja musi odpowiadać pytaniu eksperymentu.

Automatyczny test powinien sprawdzać wybrany objaw, nie dowolne niezerowe zakończenie programu. Awaria DNS nie dowodzi regresji parsera. Dla problemu z wyścigiem wiele powtórzeń poprawia wykrywalność, lecz brak awarii nadal nie daje pewności. Ustalmy z góry liczbę prób, kryterium oraz stan „niejednoznaczny”. Przypadkowe klasyfikowanie kolejnych commitów może skierować algorytm do zupełnie niewłaściwej części historii.

## Drugi przykład

Czasami checkout w ogóle nie jest potrzebny: chcemy zbudować migawkę źródeł w jednorazowym katalogu. Opcja `--no-checkout` przesuwa wtedy `BISECT_HEAD`, a skrypt pobiera jego zawartość przez `git archive`. To przydatne, gdy testy tworzą wiele plików albo narzędzia generujące nie potrafią pracować poza źródłami.

~~~sh
# W osobnym worktree diagnostycznym:
git bisect start --no-checkout "$bad_ref" "$good_ref"
git bisect run bash /absolute/repro/check-archive.sh
git bisect log > /absolute/repro/archive-bisect.log
git bisect reset
~~~

Skrypt poniżej jest alternatywą dla poprzedniego. Uruchamia ten sam sterownik po rozpakowaniu migawki. Wymaga Bash ze względu na `pipefail`; dzięki temu awaria `git archive` nie zostanie zamaskowana sukcesem ostatniego procesu potoku.

~~~sh
#!/bin/bash
# /absolute/repro/check-archive.sh
set -u -o pipefail
snapshot=$(mktemp -d) || exit 128
trap 'rm -rf "$snapshot"' EXIT HUP INT TERM
commit=$(git rev-parse --verify BISECT_HEAD) || exit 128
if ! git archive "$commit" | tar -x -C "$snapshot"; then
    exit 128
fi
cd "$snapshot" || exit 128
sh /absolute/repro/check-regression.sh
exit $?
~~~

Archiwum nie zawiera automatycznie pełnej zawartości submodułów ani obiektów przechowywanych poza repozytorium. Pliki generowane i zależności trzeba odtworzyć zgodnie z daną rewizją. Narzędzia korzystające z `git describe` również wymagają uwagi, bo migawka nie ma katalogu `.git`. Ten wariant jest właściwy tylko wtedy, gdy sposób materializacji źródeł zachowuje warunki reprodukcji.

Po wskazaniu granicy zapisujemy log bisection oraz weryfikujemy podejrzany commit i jego rodzica na świeżych katalogach budowania. Porównujemy zmianę z objawem i formułujemy mechanizm, na przykład nieprawidłowe unieważnienie iteratora. Poprawka powinna zawierać test regresyjny zawodzący przed naprawą. Samo cofnięcie podejrzanego commita może potwierdzić korelację, ale nie zawsze wyjaśni interakcję z pozostałymi zmianami.

Historia z merge commitami wymaga doprecyzowania pytania. Domyślne wyszukiwanie może wejść do gałęzi, której pośrednie rewizje nie były samodzielnie wydawane. Jeżeli interesuje nas moment włączenia regresji do głównej linii, opcja `--first-parent` może wskazać merge jako granicę. To inny eksperyment niż szukanie pierwotnej zmiany na gałęzi; po znalezieniu merge można osobno zbadać jego rodziców. Nie wybieramy tej opcji tylko po to, aby ukryć niewygodne wyniki budowania.

Do zgłoszenia warto dołączyć małe archiwum reprodukcji z instrukcją jednego uruchomienia i oczekiwanym rezultatem. Osoba analizująca błąd nie powinna odtwarzać ścieżek autora ani szukać brakującego pliku wejściowego w logach. Po zminimalizowaniu danych ponownie sprawdzamy obie granice historii: uproszczenie reprodukcji mogło przypadkowo zmienić badany problem.

## Porównanie i decyzje

Ręczne `bisect good` i `bisect bad` sprawdzają się przy małej liczbie kosztownych ocen wymagających analizy człowieka. `bisect run` daje powtarzalność i zachowuje jednolite kryterium, ale wymaga starannie zaprojektowanego klasyfikatora. Ograniczenie wyszukiwania do ścieżek przyspiesza pracę tylko wtedy, gdy rzeczywiście wiadomo, gdzie powstała przyczyna. Błąd w konfiguracji, zależności lub generatorze może leżeć poza katalogiem z wadliwą funkcją.

**Zadanie 1.** Stary commit nie kompiluje się, ponieważ nie wspiera aktualnego kompilatora. Czy zwrócić `1`?

<details><summary>Rozwiązanie</summary>

Jeżeli szukamy regresji działania programu, taka rewizja jest nieprzetestowana, więc zwracamy `125` albo odtwarzamy wspierany toolchain. Gdy pytaniem jest zgodność z tym konkretnym kompilatorem, błąd budowania może być właściwym kryterium złego stanu. Najpierw ustalamy pytanie.

</details>

**Zadanie 2.** Jeden z dziesięciu przebiegów dobrego commita kończy się błędem usługi zewnętrznej. Jak przygotować bisection parsera?

<details><summary>Rozwiązanie</summary>

Usuń zależność od żywej usługi przez utrwaloną odpowiedź albo lokalny kontrolowany serwer. Oddziel awarię infrastruktury od błędu parsowania. Potwierdź powtarzalne wyniki na obu granicach, zanim uruchomisz automatyczne wyszukiwanie.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Strategia debugowania i MRE](01_strategia_debugowania_i_mre.md)
- [Git i praca z repozytorium](../14_warsztat_profesjonalisty/05_git_i_praca_z_repozytorium.md)
