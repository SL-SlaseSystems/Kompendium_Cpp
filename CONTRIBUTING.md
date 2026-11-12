# Zasady rozwijania kompendium

[← Spis treści](README.md)

## Zakres i styl

Tekst jest pisany po polsku, opisowo i konkretnie. Angielski termin należy podać przy pierwszym użyciu, jeśli występuje powszechnie w dokumentacji lub diagnostyce kompilatorów. Zdania o zachowaniu języka powinny rozróżniać zachowanie zdefiniowane, implementacyjnie zdefiniowane, unspecified, indeterminate, erroneous i undefined.

Każdy rozdział tematyczny zaczyna się łączem do głównego spisu treści albo lokalnej mapy działu (`README.md`) i kończy nagłówkiem `## Powiązane tematy` z dwoma–pięcioma linkami. Rozdział główny ma co najmniej 500 słów prozy, a ekspercki 650; kod nie wlicza się do limitu. Wymagane są sekcje `Jak to działa krok po kroku`, `Pogłębienie mechanizmu`, `Drugi przykład` oraz `Porównanie i decyzje`. Każdy rozdział zawiera co najmniej dwa bloki przykładów, z których przynajmniej jeden powinien być samowystarczalnym C++23, jeśli charakter tematu na to pozwala.

## Status funkcji

- Bez dodatkowej adnotacji opis dotyczy C++23.
- Funkcja C++26 otrzymuje etykietę **C++26** i informację o dacie weryfikacji.
- Rozszerzenie Clang, GCC albo MSVC jest nazywane rozszerzeniem implementacji.
- CMake, Conan, vcpkg, Boost, Catch2 i GoogleTest są elementami ekosystemu, nie standardu ISO C++.

## Bloki kodu

Samowystarczalny przykład kompilowany przez walidator:

~~~cpp
#include <cassert>

int main() {
    assert(2 + 2 == 4);
}
~~~

Fragment zależny od zewnętrznego kontekstu, platformy albo celowo pokazujący UB:

~~~cpp,notest
int* dangling() {
    int local = 1;
    return &local; // wyłącznie przykład błędu
}
~~~

Polecenia i pseudokod używają `text`. Jeden blok `cpp` powinien być samowystarczalną jednostką translacji, zwykle z `main`. Walidator tylko kompiluje kod przez `-fsyntax-only`; nie wykonuje go.

## Dobre praktyki redakcyjne

Preferuj RAII, rule of zero, typy wartościowe, standardowe kontenery oraz jawne modele własności. Pokazując historyczny albo niskopoziomowy mechanizm, wyjaśnij, kiedy jest potrzebny i dlaczego zwykle istnieje bezpieczniejsza abstrakcja. Nie opisuj konkretnego layoutu, ABI, kolejności ewaluacji czy szerokości typu jako gwarancji przenośnego C++, jeśli standard jej nie daje.

Przed oddaniem zmian uruchom `python3 -m unittest scripts/test_verify.py -v`, a następnie `bash scripts/verify.sh`. Nowy rozdział musi zostać dodany do głównego indeksu i mapy działu, nie może być pustym szkieletem i podlega tym samym progom co istniejące rozdziały. Mapy, zadania i instrukcje laboratoriów mają odrębne wymagania opisane niżej.

Mapy `README.md` w działach podają wymagania wstępne, kompletny indeks i sprawdzalne kryteria opanowania. Zestawy w `cwiczenia/` zawierają konkretne dane lub scenariusze, zadanie do wykonania, przypadki graniczne i rozwiązania z uzasadnieniem w `details`. Nie stosuje się do nich szablonu pełnego rozdziału. Zamiast mnożyć podobne pytania, każda pozycja powinna ujawniać inne błędne założenie albo wymagać przeniesienia wiedzy na nowy przypadek.

Zmiany w `praktyka/` wymagają budowania oraz CTest w Debug i Release według instrukcji laboratoriów. Testy zachowania nie mogą polegać wyłącznie na `assert`, ponieważ `NDEBUG` je usuwa. ASan/UBSan uruchamiaj jako osobny wariant; wynik nie jest dowodem braku wyścigów. Nowe przykłady `cpp` sprawdzaj także przez wykonanie, jeżeli mają bezpieczny, samowystarczalny kontrakt; nie uruchamiaj bloków celowo zawierających UB. Raport rozróżnia weryfikację składni wszystkich bloków od wykonania wybranego zestawu.

## Powiązane tematy

- [Źródła](zrodla.md)
- [Ściąga](sciaga.md)

## Kontrola rozbudowanej ścieżki 01–30

Zestawy `ZESTAW-CWICZEN.md` i mapy działów są odrębnymi formami dydaktycznymi, więc nie wymagają sztucznego rozdmuchiwania do szablonu rozdziału. Rozdziały rozpoznaje numerowany plik w dziale lub katalogu zaawansowanym. Poprawna nawigacja prowadzi do głównego indeksu albo lokalnej mapy; mapa i główny indeks muszą obejmować istniejące rozdziały.

~~~text
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/verify_content.py --metadata-only
python3 scripts/verify_content.py --section 02_podstawy_jezyka
python3 scripts/verify_content.py --metadata-only --metrics
bash scripts/verify.sh
~~~

Tryb metadanych nie dowodzi kompilowalności. Tryb sekcji skraca kontrolę w trakcie pracy, ale odbiór wymaga całego repozytorium. Metryki wylicza narzędzie; nie należy przepisywać starych liczb do nowego raportu. Konfigurację CI można zweryfikować lokalnie, lecz zdalny wynik trzeba potwierdzić w usłudze.

Nowy przykład powinien demonstrować mechanizm z tytułu: przeplot transakcji, kontrakt pakietu, politykę deadline albo granicę ABI. Model z samymi flagami `passed = true` nie stanowi technicznego przykładu takiego mechanizmu. Sam próg słów i zielona kompilacja nie zastępują recenzji treści. Przy zastępowaniu powielanych akapitów zachowuj istniejącą ścieżkę i odsyłacze.
