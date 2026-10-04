[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — testowanie i jakość

Nie uruchamiaj celowego UB bez odpowiedniego sanitizera i odizolowanego procesu testowego. Zachowuj dokładne polecenie, wersję kompilatora i wynik.

## Poziom 1 — testy zachowania

1. Napisz test dla poprawnego i pustego wejścia prostej funkcji.
2. Wprowadź mutację implementacji i sprawdź, czy test ją wykrywa.
3. Oddziel test jednostkowy od integracji z systemem plików.
4. Zbuduj literalne oczekiwanie niezależne od kodu produkcyjnego.
5. Usuń test sprawdzający wyłącznie getter bez zachowania.

## Poziom 2 — analiza kompilatora

6. Włącz pełne ostrzeżenia i popraw konwersję zawężającą.
7. Uruchom clang-tidy lub inne dostępne narzędzie na compile database.
8. Oceń finding: błąd, świadomy wyjątek czy fałszywy alarm.
9. Dodaj lokalne wyciszenie z uzasadnieniem zamiast globalnego wyłączenia reguły.
10. Porównaj diagnostykę GCC i Clang dla tego samego fragmentu.

## Poziom 3 — sanitizery i debugger

11. Uruchom AddressSanitizer na kontrolowanym use-after-free w osobnym teście.
12. Uruchom UndefinedBehaviorSanitizer na signed overflow, jeśli platforma go wspiera.
13. Zatrzymaj program na wyjątku lub sygnale w GDB/LLDB.
14. Odczytaj stack trace i wskaż pierwszą ramkę własnego kodu.
15. Napraw przyczynę, a następnie ponów dokładnie to samo polecenie.

## Poziom 4 — pomiar

16. Napisz benchmark z rozgrzewką i wieloma próbkami.
17. Zapobiegnij usunięciu wyniku przez optymalizator.
18. Porównaj debug i release bez wyciągania wniosków z debug.
19. Zapisz medianę, rozrzut i parametry środowiska.
20. Użyj profilera, aby sprawdzić, czy optymalizujesz hotspot.

## Poziom 5 — przestrzeń wejść

21. Zapisz właściwość sortowania niezależną od konkretnego przykładu.
22. Wygeneruj wejścia puste, graniczne i z duplikatami.
23. Zbuduj mały harness fuzzingowy dla parsera bez efektów ubocznych.
24. Zachowaj minimalny crash input jako test regresyjny.
25. Ustal limit czasu i pamięci dla bezpiecznego uruchomienia fuzzera.

## Zadanie końcowe

Wybierz mały parser lub strukturę danych. Dodaj testy jednostkowe i integracyjne, uruchom ostrzeżenia, analizę statyczną, ASan/UBSan oraz fuzzing albo testy właściwości. Na końcu wykonaj benchmark tylko dla rzeczywistego hotspota. Raport ma zawierać polecenia, środowisko, jeden wykryty problem i dowód GREEN po poprawce.
