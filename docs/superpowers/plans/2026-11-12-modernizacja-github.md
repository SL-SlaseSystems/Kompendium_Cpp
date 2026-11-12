# Plan modernizacji repozytorium GitHub

Specyfikacja: ../specs/2026-11-12-modernizacja-github.md.

- [x] Inwentaryzacja, czysty git status, kopia i manifest źródłowych plików.
- [x] Włączenie ośmiu rozdziałów, 78 zadań, diagnozy i laboratoriów z poprzedniej lokalizacji.
- [x] Pełny indeks 30 działów, uzupełnienie map i brakującej mapy projektów.
- [x] Dwanaście rozdziałów produkcyjnych oraz dwa warsztatowe bez powielanej treści.
- [x] Testowalny walidator Markdown/kompilacji, testy regresyjne i metryki.
- [x] Presety i workflow z odpowiadającym im opisem; Debug/Release/UBSan.
- [x] Niezależny przegląd, pełna weryfikacja, raport rzeczywistych wyników.
- [x] Synchronizacja 43 nowych i 35 zmienionych plików do docelowego repo; tam 36/36 unittest, metadane bez błędów i CTest Debug/Release/UBSan po 4/4. Żadnego usuwania plików ani zmiany historii Git.

Bieżąca realizacja jest ograniczona do tej prośby. Nie jest deklaracją ponownego audytu całego historycznego korpusu ani uruchomienia zdalnego CI.

## Wynik kontroli przed synchronizacją

36 unittest, 282 Markdown, 417/417 bloków cpp, 34/34 uruchomienia z dotkniętych rozdziałów, niezależnie 32 nowe programy UBSan; laboratoria Debug/Release/UBSan/Ninja po 4/4. Rzeczywisty konsument pakietu CMake po relokacji oraz klienty C11/C++23 sprawdzone. Lokalne ograniczenia ASan i initdb PostgreSQL są jawne w raporcie. Workflow zdalnego CI pozostaje nieuruchomiony.
