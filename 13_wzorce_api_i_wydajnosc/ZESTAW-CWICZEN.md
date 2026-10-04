[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — wzorce, API i wydajność

Każdą decyzję uzasadnij kontraktem użytkownika. Pomiary wykonuj w release, zapisuj konfigurację i nie uruchamiaj ryzykownych eksperymentów na ważnych danych.

## Poziom 1 — rule of zero i granice

1. Usuń zbędne funkcje specjalne z klasy złożonej z typów wartościowych.
2. Zastosuj PImpl i sprawdź, które include znikają z publicznego nagłówka.
3. Oceń koszt alokacji i niekompletnego typu w PImpl.
4. Zbuduj NVI z jednym publicznym kontraktem i prywatnym punktem rozszerzenia.
5. Przetestuj inwariant przez publiczne API.

## Poziom 2 — modele polimorfizmu

6. Zaimplementuj operację przez value semantics.
7. Zbuduj odpowiednik przez interfejs wirtualny.
8. Zbuduj mały wrapper type-erased dla callable.
9. Porównaj ownership, alokacje i kopiowalność trzech wersji.
10. Wybierz `variant` dla zamkniętego zbioru alternatyw.

## Poziom 3 — API i ABI

11. Przepisz funkcję z niejasnymi parametrami bool na nazwane opcje.
12. Wyraź jednostkę fizyczną osobnym typem.
13. Oddziel typ błędu publicznego od szczegółu biblioteki zależnej.
14. Wskaż zmianę kompatybilną źródłowo, ale ryzykowną binarnie.
15. Zaprojektuj wersjonowanie interfejsu biblioteki współdzielonej.

## Poziom 4 — architektura i testowalność

16. Wstrzyknij zegar do logiki zależnej od czasu.
17. Wstrzyknij port zapisu bez service locatora.
18. Zbuduj composition root tworzący cały graf obiektów.
19. Usuń cykliczną zależność między dwoma modułami.
20. Napisz test domeny bez systemu plików i sieci.

## Poziom 5 — wydajność

21. Porównaj array-of-structs i struct-of-arrays na kontrolowanym obciążeniu.
22. Zmierz koszt alokacji na gorącej ścieżce.
23. Sprawdź profil, zanim zmienisz strukturę danych.
24. Porównaj lokalność cache, nie tylko notację Big-O.
25. Zapisz wynik negatywny, gdy optymalizacja nie daje mierzalnej korzyści.

## Zadanie końcowe

Zaprojektuj bibliotekę przetwarzania zdarzeń z małym publicznym API i wymiennym backendem. Przygotuj wariant wirtualny albo type-erased, composition root, typowane błędy oraz test bez realnego I/O. Następnie zmierz reprezentatywny hotspot w release i udokumentuj decyzję wraz z wynikiem, który uzasadnia lub odrzuca optymalizację.
