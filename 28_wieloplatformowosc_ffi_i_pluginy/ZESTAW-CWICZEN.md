[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — wieloplatformowość, ffi i pluginy

Zadania rozwijają umiejętność, aby zaprojektować cienką warstwę platformową i stabilną granicę C dla rozszerzeń. Pracuj na repozytorium ćwiczeniowym i nie używaj danych produkcyjnych. Każdy wynik powinien zawierać założenie, polecenie reprodukcji, obserwację oraz krótką decyzję. Nie przenosimy STL przez stabilne ABI pluginu. Interfejs opisuje wersję struktury, capabilities, ownership, alokator, regułę zwalniania i zakaz propagacji wyjątków.

## Zadania prowadzone

1. Zapisz model dla zagadnienia „warstwy platformowe i porty”; podaj kontrakt, limit, wynik i sposób odtworzenia.
2. Zbuduj minimalny test dla zagadnienia „ffi c i stabilne abi”; podaj kontrakt, limit, wynik i sposób odtworzenia.
3. Wprowadź kontrolowaną awarię dla zagadnienia „biblioteki dynamiczne i pluginy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
4. Porównaj dwa warianty dla zagadnienia „wersjonowanie pluginów i capabilities”; podaj kontrakt, limit, wynik i sposób odtworzenia.
5. Udokumentuj decyzję dla zagadnienia „cross compilation i toolchain files”; podaj kontrakt, limit, wynik i sposób odtworzenia.
6. Zapisz model dla zagadnienia „dystrybucja windows linux macos”; podaj kontrakt, limit, wynik i sposób odtworzenia.
7. Zbuduj minimalny test dla zagadnienia „warstwy platformowe i porty”; podaj kontrakt, limit, wynik i sposób odtworzenia.
8. Wprowadź kontrolowaną awarię dla zagadnienia „ffi c i stabilne abi”; podaj kontrakt, limit, wynik i sposób odtworzenia.
9. Porównaj dwa warianty dla zagadnienia „biblioteki dynamiczne i pluginy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
10. Udokumentuj decyzję dla zagadnienia „wersjonowanie pluginów i capabilities”; podaj kontrakt, limit, wynik i sposób odtworzenia.
11. Zapisz model dla zagadnienia „cross compilation i toolchain files”; podaj kontrakt, limit, wynik i sposób odtworzenia.
12. Zbuduj minimalny test dla zagadnienia „dystrybucja windows linux macos”; podaj kontrakt, limit, wynik i sposób odtworzenia.
13. Wprowadź kontrolowaną awarię dla zagadnienia „warstwy platformowe i porty”; podaj kontrakt, limit, wynik i sposób odtworzenia.
14. Porównaj dwa warianty dla zagadnienia „ffi c i stabilne abi”; podaj kontrakt, limit, wynik i sposób odtworzenia.
15. Udokumentuj decyzję dla zagadnienia „biblioteki dynamiczne i pluginy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
16. Zapisz model dla zagadnienia „wersjonowanie pluginów i capabilities”; podaj kontrakt, limit, wynik i sposób odtworzenia.
17. Zbuduj minimalny test dla zagadnienia „cross compilation i toolchain files”; podaj kontrakt, limit, wynik i sposób odtworzenia.
18. Wprowadź kontrolowaną awarię dla zagadnienia „dystrybucja windows linux macos”; podaj kontrakt, limit, wynik i sposób odtworzenia.
19. Porównaj dwa warianty dla zagadnienia „warstwy platformowe i porty”; podaj kontrakt, limit, wynik i sposób odtworzenia.
20. Udokumentuj decyzję dla zagadnienia „ffi c i stabilne abi”; podaj kontrakt, limit, wynik i sposób odtworzenia.
21. Zapisz model dla zagadnienia „biblioteki dynamiczne i pluginy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
22. Zbuduj minimalny test dla zagadnienia „wersjonowanie pluginów i capabilities”; podaj kontrakt, limit, wynik i sposób odtworzenia.
23. Wprowadź kontrolowaną awarię dla zagadnienia „cross compilation i toolchain files”; podaj kontrakt, limit, wynik i sposób odtworzenia.
24. Porównaj dwa warianty dla zagadnienia „dystrybucja windows linux macos”; podaj kontrakt, limit, wynik i sposób odtworzenia.
25. Udokumentuj decyzję dla zagadnienia „warstwy platformowe i porty”; podaj kontrakt, limit, wynik i sposób odtworzenia.

## Zadanie końcowe

Zaprojektuj małe studium obejmujące co najmniej trzy tematy z działu. Zacznij od granic i modelu awarii, przygotuj bezpieczny prototyp, testy sukcesu i błędu oraz plan obserwowalności. Następnie wykonaj przegląd ryzyka, zmierz koszt rozwiązania i zapisz warunki, które wymusiłyby zmianę projektu. Wynik ma dać się odtworzyć od świeżego klonu bez prywatnych ścieżek, sekretów i ręcznie przygotowanego stanu.
