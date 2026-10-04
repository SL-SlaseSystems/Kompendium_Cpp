[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — bazy danych i trwałość

Zadania rozwijają umiejętność, aby łączyć model danych, transakcje i RAII bez mylenia gwarancji bazy z gwarancjami wrappera C++. Pracuj na repozytorium ćwiczeniowym i nie używaj danych produkcyjnych. Każdy wynik powinien zawierać założenie, polecenie reprodukcji, obserwację oraz krótką decyzję. Zapytania parametryzujemy, ownership uchwytów zamykamy w RAII, a rollback testujemy. Poziom izolacji i trwałość opisujemy dla konkretnego silnika oraz konfiguracji.

## Zadania prowadzone

1. Zapisz model dla zagadnienia „sql i model relacyjny”; podaj kontrakt, limit, wynik i sposób odtworzenia.
2. Zbuduj minimalny test dla zagadnienia „sqlite i raii połączenia”; podaj kontrakt, limit, wynik i sposób odtworzenia.
3. Wprowadź kontrolowaną awarię dla zagadnienia „transakcje i poziomy izolacji”; podaj kontrakt, limit, wynik i sposób odtworzenia.
4. Porównaj dwa warianty dla zagadnienia „prepared statements i bezpieczeństwo”; podaj kontrakt, limit, wynik i sposób odtworzenia.
5. Udokumentuj decyzję dla zagadnienia „migracje pooling i odporność”; podaj kontrakt, limit, wynik i sposób odtworzenia.
6. Zapisz model dla zagadnienia „repozytoria i case study”; podaj kontrakt, limit, wynik i sposób odtworzenia.
7. Zbuduj minimalny test dla zagadnienia „sql i model relacyjny”; podaj kontrakt, limit, wynik i sposób odtworzenia.
8. Wprowadź kontrolowaną awarię dla zagadnienia „sqlite i raii połączenia”; podaj kontrakt, limit, wynik i sposób odtworzenia.
9. Porównaj dwa warianty dla zagadnienia „transakcje i poziomy izolacji”; podaj kontrakt, limit, wynik i sposób odtworzenia.
10. Udokumentuj decyzję dla zagadnienia „prepared statements i bezpieczeństwo”; podaj kontrakt, limit, wynik i sposób odtworzenia.
11. Zapisz model dla zagadnienia „migracje pooling i odporność”; podaj kontrakt, limit, wynik i sposób odtworzenia.
12. Zbuduj minimalny test dla zagadnienia „repozytoria i case study”; podaj kontrakt, limit, wynik i sposób odtworzenia.
13. Wprowadź kontrolowaną awarię dla zagadnienia „sql i model relacyjny”; podaj kontrakt, limit, wynik i sposób odtworzenia.
14. Porównaj dwa warianty dla zagadnienia „sqlite i raii połączenia”; podaj kontrakt, limit, wynik i sposób odtworzenia.
15. Udokumentuj decyzję dla zagadnienia „transakcje i poziomy izolacji”; podaj kontrakt, limit, wynik i sposób odtworzenia.
16. Zapisz model dla zagadnienia „prepared statements i bezpieczeństwo”; podaj kontrakt, limit, wynik i sposób odtworzenia.
17. Zbuduj minimalny test dla zagadnienia „migracje pooling i odporność”; podaj kontrakt, limit, wynik i sposób odtworzenia.
18. Wprowadź kontrolowaną awarię dla zagadnienia „repozytoria i case study”; podaj kontrakt, limit, wynik i sposób odtworzenia.
19. Porównaj dwa warianty dla zagadnienia „sql i model relacyjny”; podaj kontrakt, limit, wynik i sposób odtworzenia.
20. Udokumentuj decyzję dla zagadnienia „sqlite i raii połączenia”; podaj kontrakt, limit, wynik i sposób odtworzenia.
21. Zapisz model dla zagadnienia „transakcje i poziomy izolacji”; podaj kontrakt, limit, wynik i sposób odtworzenia.
22. Zbuduj minimalny test dla zagadnienia „prepared statements i bezpieczeństwo”; podaj kontrakt, limit, wynik i sposób odtworzenia.
23. Wprowadź kontrolowaną awarię dla zagadnienia „migracje pooling i odporność”; podaj kontrakt, limit, wynik i sposób odtworzenia.
24. Porównaj dwa warianty dla zagadnienia „repozytoria i case study”; podaj kontrakt, limit, wynik i sposób odtworzenia.
25. Udokumentuj decyzję dla zagadnienia „sql i model relacyjny”; podaj kontrakt, limit, wynik i sposób odtworzenia.

## Zadanie końcowe

Zaprojektuj małe studium obejmujące co najmniej trzy tematy z działu. Zacznij od granic i modelu awarii, przygotuj bezpieczny prototyp, testy sukcesu i błędu oraz plan obserwowalności. Następnie wykonaj przegląd ryzyka, zmierz koszt rozwiązania i zapisz warunki, które wymusiłyby zmianę projektu. Wynik ma dać się odtworzyć od świeżego klonu bez prywatnych ścieżek, sekretów i ręcznie przygotowanego stanu.
