[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — budowanie i organizacja

Wszystkie ścieżki w rozwiązaniach mają być względne lub wyliczane przez narzędzie. Testuj projekt w świeżym katalogu build.

## Poziom 1 — translation units

1. Rozdziel program na nagłówek i dwa pliki źródłowe.
2. Usuń zależność od transitive include przez jawny include.
3. Dodaj include guard lub `#pragma once` i opisz przenośność.
4. Użyj forward declaration tylko dla typu niekompletnego, dla którego jest legalna.
5. Porównaj czas przebudowy po zmianie nagłówka i pliku `.cpp`.

## Poziom 2 — linkowanie i ODR

6. Wywołaj kontrolowany undefined reference.
7. Wywołaj multiple definition i wskaż naruszoną regułę.
8. Popraw stałą lub funkcję nagłówkową przez właściwe użycie `inline`.
9. Obejrzyj symbole pliku obiektowego narzędziem platformy.
10. Wyjaśnij różnicę między linkowaniem statycznym i dynamicznym.

## Poziom 3 — namespaces i moduły

11. Usuń `using namespace` z publicznego nagłówka.
12. Znajdź nieoczekiwane wywołanie odkryte przez ADL.
13. Zbuduj API z funkcją hidden friend i uzasadnij decyzję.
14. Naszkicuj odpowiednik prostego nagłówka jako moduł C++.
15. Zapisz zależności i kolejność budowania interfejsu modułu oraz importera.

## Poziom 4 — CMake

16. Utwórz target biblioteki i programu przez `add_library` oraz `add_executable`.
17. Ustaw C++23 przez compile features targetu.
18. Rozróżnij `PRIVATE`, `PUBLIC` i `INTERFACE` na działającym przykładzie.
19. Dodaj test przez CTest bez zakodowanej ścieżki binarnej.
20. Zbuduj konfiguracje debug i release w osobnych katalogach.

## Poziom 5 — zależności i reprodukowalność

21. Opisz, które artefakty zależności należy wersjonować, a które odtwarzać.
22. Dodaj małą zależność przez jeden wybrany menedżer pakietów.
23. Zablokuj wersję i sprawdź budowę w pustym cache.
24. Wygeneruj compile commands i użyj ich w narzędziu analitycznym.
25. Napisz instrukcję od czystego checkoutu do uruchomienia testów.

## Zadanie końcowe

Zbuduj projekt składający się z biblioteki, aplikacji i testów. Interfejs publiczny ma być oddzielony od implementacji, wymagania użycia mają propagować się przez targety, a build ma działać poza drzewem źródeł w debug i release. Dostarcz minimalną instrukcję, listę zależności oraz kontrolowany przykład błędu ODR z objaśnieniem.
