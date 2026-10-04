[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — warsztat profesjonalisty

Wykonuj zadania w osobnym repozytorium. Do każdego wyniku dołącz polecenie odtwarzające oraz krótką notatkę: co jest polityką projektu, co zależy od komputera i jaki błąd ma zatrzymać kontrolę.

## Poziom 1 — formatowanie

1. Wygeneruj styl bazowy clang-format i ogranicz go do pięciu jawnych decyzji.
2. Dodaj `.editorconfig` regulujący kodowanie, końce linii i końcową nową linię.
3. Sformatuj jeden plik i obejrzyj diff przed zatwierdzeniem.
4. Uruchom kontrolę formatowania bez modyfikowania pliku.
5. Wyłącz katalog z kodem wygenerowanym i uzasadnij granicę.

## Poziom 2 — analiza

6. Włącz mały zestaw reguł clang-tidy i zapisz wersję kompilatora.
7. Wygeneruj `compile_commands.json` przez CMake.
8. Napraw ostrzeżenie bez wyciszania reguły.
9. Dodaj lokalne wyciszenie z komentarzem opisującym fałszywy alarm.
10. Porównaj raport clang-tidy z wynikiem Cppcheck dla tego samego pliku.

## Poziom 3 — budowanie i dokumentacja

11. Dodaj wersjonowany `CMakePresets.json` z presetem debug.
12. Dodaj lokalny `CMakeUserPresets.json` i upewnij się, że Git go ignoruje.
13. Zbuduj projekt generatorem Ninja bez ręcznego podawania katalogu build.
14. Dodaj komentarz Doxygen do publicznego typu i wygeneruj HTML.
15. Usuń komentarz, który tylko powtarza nazwę funkcji, i opisz rzeczywisty kontrakt.

## Poziom 4 — Git

16. Podziel mieszaną zmianę na dwa logiczne commity.
17. Zapisz commit w trybie imperatywnym i wyjaśnij powód w treści.
18. Użyj interaktywnego stage, aby pominąć przypadkowy fragment.
19. Rozwiąż kontrolowany konflikt i uruchom testy po rozwiązaniu.
20. Przygotuj opis pull requestu z ryzykiem i planem weryfikacji.

## Poziom 5 — automatyzacja

21. Skonfiguruj hook sprawdzający końcową nową linię.
22. Dodaj lokalną kontrolę clang-format tylko dla zmienionych plików.
23. Oddziel szybką kontrolę przed commitem od pełnego zestawu testów.
24. Uruchom wszystkie hooki na całym repozytorium.
25. Zasymuluj błąd narzędzia i sprawdź, czy kod wyjścia zatrzymuje proces.

## Zadanie końcowe

Przygotuj minimalny projekt biblioteki z `CMakePresets.json`, Ninja, testem, `.clang-format`, `.editorconfig`, małą konfiguracją clang-tidy, dokumentacją Doxygen i lokalnymi hookami. Od świeżego klonu odtwórz cały przepływ według README. Raport ma wskazać wersjonowane pliki polityki, lokalne ustawienia użytkownika, czas szybkiej pętli oraz elementy przeznaczone później do CI.
