# Zasady rozwijania kompendium

[← Spis treści](README.md)

## Zakres i styl

Tekst jest pisany po polsku, opisowo i konkretnie. Angielski termin należy podać przy pierwszym użyciu, jeśli występuje powszechnie w dokumentacji lub diagnostyce kompilatorów. Zdania o zachowaniu języka powinny rozróżniać zachowanie zdefiniowane, implementacyjnie zdefiniowane, unspecified, indeterminate, erroneous i undefined.

Każdy rozdział tematyczny zaczyna się łączem „← Spis treści” prowadzącym do nadrzędnego `README.md` i kończy nagłówkiem `## Powiązane tematy` z dwoma–pięcioma linkami. Rozdział główny ma co najmniej 500 słów prozy, a ekspercki 650; kod nie wlicza się do limitu. Wymagane są sekcje `Jak to działa krok po kroku`, `Pogłębienie mechanizmu`, `Drugi przykład` oraz `Porównanie i decyzje`. Każdy rozdział zawiera co najmniej dwa bloki przykładów, z których przynajmniej jeden powinien być samowystarczalnym C++23, jeśli charakter tematu na to pozwala.

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

Przed oddaniem zmian uruchom `python3 -m unittest scripts/test_verify.py -v`, a następnie `bash scripts/verify.sh`. Nowy plik musi zostać dodany do głównego indeksu, nie może być pustym szkieletem i podlega tym samym progom co istniejące rozdziały.

## Powiązane tematy

- [Źródła](zrodla.md)
- [Ściąga](sciaga.md)
