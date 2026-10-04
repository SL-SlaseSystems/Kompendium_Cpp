[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — wprowadzenie do C++

Wykonuj zadania w osobnym katalogu roboczym. Zachowuj polecenia i komunikaty diagnostyczne, ponieważ w tym dziale obserwacja procesu jest równie ważna jak kod.

## Poziom 1 — orientacja

1. Sprawdź wersję dostępnego kompilatora i zapisz nazwę frontendu oraz platformę docelową.
2. Znajdź informację, jaki standard C++ kompilator wybiera bez flagi `-std`.
3. Skompiluj minimalny program wypisujący tekst w trybie C++23.
4. Dodaj `-Wall -Wextra -Wpedantic` i usuń wszystkie ostrzeżenia.
5. Zmień nazwę pliku wynikowego i uruchom go z terminala.

## Poziom 2 — standard i implementacja

6. Wyjaśnij własnymi słowami różnicę między ISO C++, kompilatorem i biblioteką standardową.
7. Sprawdź wartość makra `__cplusplus` w używanym trybie kompilacji.
8. Porównaj wynik `__cplusplus` dla dwóch dostępnych trybów standardu.
9. Znajdź jedną funkcję C++23 nieobsługiwaną przez lokalny toolchain i opisz, która warstwa jej nie dostarcza.
10. Zbuduj ten sam program dwoma kompilatorami, jeśli są dostępne, i porównaj diagnostykę.

## Poziom 3 — diagnozowanie etapów

11. Wprowadź błąd składni i wskaż najważniejszy komunikat, ignorując błędy wtórne.
12. Zadeklaruj funkcję bez definicji, wywołaj ją i rozpoznaj błąd linkera.
13. Utwórz funkcję zwracającą niezerowy kod i sprawdź kod zakończenia procesu.
14. Wygeneruj plik po preprocessingu i znajdź rozwiniętą dyrektywę `#include`.
15. Wygeneruj plik obiektowy bez linkowania i sprawdź, że nie jest programem wykonywalnym.

## Poziom 4 — program wieloplikowy

16. Rozdziel deklarację funkcji, definicję i `main` między nagłówek oraz dwa pliki źródłowe.
17. Zbuduj oba pliki do osobnych plików obiektowych, a następnie połącz je.
18. Zmień tylko jeden plik źródłowy i przebuduj minimalny potrzebny zakres ręcznie.
19. Dodaj guard do nagłówka i wyjaśnij problem, któremu zapobiega.
20. Celowo zdefiniuj tę samą funkcję w dwóch plikach i przeanalizuj diagnostykę.

## Poziom 5 — decyzje i dokumentacja

21. Napisz krótką instrukcję budowania projektu dla drugiej osoby.
22. Dodaj do instrukcji wymagany standard, kompilator i znane ograniczenia.
23. Wyjaśnij, dlaczego „działa na moim komputerze” nie jest kryterium przenośności.
24. Porównaj build debug i release pod względem diagnostyki, symboli i optymalizacji.
25. Sporządź tabelę: błąd preprocessora, kompilatora, linkera i runtime — objaw oraz pierwsza czynność diagnostyczna.

## Zadanie końcowe

Zbuduj ręcznie trzyplikowy program, który przyjmuje argument wiersza poleceń i wypisuje przetworzony wynik. Dostarcz kod, pełne polecenia budowania w C++23, przykład poprawnego uruchomienia oraz po jednym kontrolowanym błędzie kompilacji i linkowania z objaśnieniem. Odbiór wymaga czystej kompilacji z ostrzeżeniami i instrukcji możliwej do wykonania w świeżym katalogu.
