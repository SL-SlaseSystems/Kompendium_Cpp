[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — podstawy języka C++

Kompiluj każde rozwiązanie z pełnymi ostrzeżeniami. Przy zadaniach diagnostycznych najpierw zapisz przewidywanie, potem dopiero uruchom kompilator.

## Poziom 1 — deklaracje i typy

1. Zadeklaruj wartości reprezentujące liczbę elementów, cenę, znak i stan logiczny; uzasadnij typy.
2. Pokaż zakres nazwy w bloku zagnieżdżonym bez przesłaniania istniejącej zmiennej.
3. Zapisz literały dziesiętne, szesnastkowe, binarne i zmiennoprzecinkowe z czytelnymi separatorami.
4. Sprawdź rozmiary podstawowych typów bez zakładania konkretnych wartości.
5. Utwórz silniej opisową strukturę zamiast przekazywania trzech niepowiązanych liczb.

## Poziom 2 — const, constexpr i operatory

6. Przenieś obliczenie stałej tablicy do czasu kompilacji.
7. Napisz funkcję `constexpr`, którą można wywołać w compile time i runtime.
8. Zademonstruj różnicę między `const int*`, `int* const` i `const int* const`.
9. Znajdź przykład, w którym kolejność ewaluacji ma znaczenie, i przepisz go jednoznacznie.
10. Wykryj niebezpieczną konwersję signed/unsigned przy porównaniu rozmiaru kontenera.

## Poziom 3 — funkcje

11. Napisz funkcję przyjmującą mały typ przez wartość i tekst przez `std::string_view`.
12. Zaprojektuj przeciążenia tak, aby wywołania dla `int` i `double` były jednoznaczne.
13. Zastąp parametr wyjściowy zwracanym typem agregującym dwa wyniki.
14. Napisz funkcję czystą i osobno funkcję wykonującą I/O; wyjaśnij korzyść podziału.
15. Sprawdź, kiedy argument domyślny jest wiązany i dlaczego nie zastępuje polimorfizmu.

## Poziom 4 — sterowanie przepływem

16. Zaimplementuj klasyfikację liczby z kompletnym `if/else`.
17. Przepisz pętlę indeksową na range-for bez zmiany semantyki.
18. Użyj inicjalizatora w `if`, aby ograniczyć zakres zmiennej pomocniczej.
19. Napisz `switch` dla `enum class` i obsłuż wszystkie enumeratory.
20. Usuń przypadkowy infinite loop, dodając jawny wariant postępu i warunek zakończenia.

## Poziom 5 — referencje, wskaźniki i granice

21. Zaimplementuj funkcję, która wymaga obiektu, oraz osobną, która dopuszcza brak wartości; dobierz referencję i wskaźnik.
22. Znajdź dangling reference w krótkim przykładzie i napraw ownership, nie tylko składnię.
23. Przekaż tablicę przez `std::span` i zachowaj jej rozmiar.
24. Sprawdź każdy dostęp do tablicy dla rozmiaru zero, jeden i wartości granicznej.
25. Narysuj lifetime obiektów w programie używającym zmiennej lokalnej, referencji i wskaźnika.

## Zadanie końcowe

Napisz analizator listy liczb przyjmujący `std::span<const int>` i zwracający strukturę z minimum, maksimum, sumą oraz liczbą elementów. Zdefiniuj zachowanie dla pustego wejścia bez wartości sentinel, dodaj przypadki graniczne i wyjaśnij wszystkie konwersje oraz reguły lifetime. Rozwiązanie ma kompilować się bez ostrzeżeń w C++23.
