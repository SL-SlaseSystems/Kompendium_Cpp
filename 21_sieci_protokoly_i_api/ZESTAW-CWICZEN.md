[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — sieci, protokoły i api

Zadania rozwijają umiejętność, aby budować niezawodną komunikację przez jawny protokół, limity, timeouty i model błędów częściowych. Pracuj na repozytorium ćwiczeniowym i nie używaj danych produkcyjnych. Każdy wynik powinien zawierać założenie, polecenie reprodukcji, obserwację oraz krótką decyzję. Fragment zależny od biblioteki oznaczamy jako zewnętrzny. Retry nie może ukrywać braku timeoutu, idempotencji ani limitu, a TLS wymaga poprawnej weryfikacji tożsamości.

## Zadania prowadzone

1. Zapisz model dla zagadnienia „modele sieci tcp udp i dns”; podaj kontrakt, limit, wynik i sposób odtworzenia.
2. Zbuduj minimalny test dla zagadnienia „http i rest”; podaj kontrakt, limit, wynik i sposób odtworzenia.
3. Wprowadź kontrolowaną awarię dla zagadnienia „tls certyfikaty i zaufanie”; podaj kontrakt, limit, wynik i sposób odtworzenia.
4. Porównaj dwa warianty dla zagadnienia „serializacja json protobuf i schema”; podaj kontrakt, limit, wynik i sposób odtworzenia.
5. Udokumentuj decyzję dla zagadnienia „klient http timeouty retry i pooling”; podaj kontrakt, limit, wynik i sposób odtworzenia.
6. Zapisz model dla zagadnienia „serwer api limity i testy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
7. Zbuduj minimalny test dla zagadnienia „modele sieci tcp udp i dns”; podaj kontrakt, limit, wynik i sposób odtworzenia.
8. Wprowadź kontrolowaną awarię dla zagadnienia „http i rest”; podaj kontrakt, limit, wynik i sposób odtworzenia.
9. Porównaj dwa warianty dla zagadnienia „tls certyfikaty i zaufanie”; podaj kontrakt, limit, wynik i sposób odtworzenia.
10. Udokumentuj decyzję dla zagadnienia „serializacja json protobuf i schema”; podaj kontrakt, limit, wynik i sposób odtworzenia.
11. Zapisz model dla zagadnienia „klient http timeouty retry i pooling”; podaj kontrakt, limit, wynik i sposób odtworzenia.
12. Zbuduj minimalny test dla zagadnienia „serwer api limity i testy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
13. Wprowadź kontrolowaną awarię dla zagadnienia „modele sieci tcp udp i dns”; podaj kontrakt, limit, wynik i sposób odtworzenia.
14. Porównaj dwa warianty dla zagadnienia „http i rest”; podaj kontrakt, limit, wynik i sposób odtworzenia.
15. Udokumentuj decyzję dla zagadnienia „tls certyfikaty i zaufanie”; podaj kontrakt, limit, wynik i sposób odtworzenia.
16. Zapisz model dla zagadnienia „serializacja json protobuf i schema”; podaj kontrakt, limit, wynik i sposób odtworzenia.
17. Zbuduj minimalny test dla zagadnienia „klient http timeouty retry i pooling”; podaj kontrakt, limit, wynik i sposób odtworzenia.
18. Wprowadź kontrolowaną awarię dla zagadnienia „serwer api limity i testy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
19. Porównaj dwa warianty dla zagadnienia „modele sieci tcp udp i dns”; podaj kontrakt, limit, wynik i sposób odtworzenia.
20. Udokumentuj decyzję dla zagadnienia „http i rest”; podaj kontrakt, limit, wynik i sposób odtworzenia.
21. Zapisz model dla zagadnienia „tls certyfikaty i zaufanie”; podaj kontrakt, limit, wynik i sposób odtworzenia.
22. Zbuduj minimalny test dla zagadnienia „serializacja json protobuf i schema”; podaj kontrakt, limit, wynik i sposób odtworzenia.
23. Wprowadź kontrolowaną awarię dla zagadnienia „klient http timeouty retry i pooling”; podaj kontrakt, limit, wynik i sposób odtworzenia.
24. Porównaj dwa warianty dla zagadnienia „serwer api limity i testy”; podaj kontrakt, limit, wynik i sposób odtworzenia.
25. Udokumentuj decyzję dla zagadnienia „modele sieci tcp udp i dns”; podaj kontrakt, limit, wynik i sposób odtworzenia.

## Zadanie końcowe

Zaprojektuj małe studium obejmujące co najmniej trzy tematy z działu. Zacznij od granic i modelu awarii, przygotuj bezpieczny prototyp, testy sukcesu i błędu oraz plan obserwowalności. Następnie wykonaj przegląd ryzyka, zmierz koszt rozwiązania i zapisz warunki, które wymusiłyby zmianę projektu. Wynik ma dać się odtworzyć od świeżego klonu bez prywatnych ścieżek, sekretów i ręcznie przygotowanego stanu.
