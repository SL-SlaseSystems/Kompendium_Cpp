[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — błędy i kontrakty

Przy każdym zadaniu zapisz oczekiwany stan programu po błędzie i sprawdź, czy test obserwuje zachowanie publiczne, a nie szczegóły implementacji.

## Poziom 1 — klasyfikacja

1. Podziel przykładowe awarie na naruszenie precondition, błąd środowiska i błąd programisty.
2. Zapisz kontrakt dzielenia, parsowania i odczytu pliku.
3. Wskaż błędy, po których operację można ponowić.
4. Rozróżnij brak wyniku od błędu z informacją diagnostyczną.
5. Usuń wartość sentinel z prostego API.

## Poziom 2 — wyjątki i RAII

6. Dodaj wyjątek w połowie operacji i sprawdź zwolnienie zasobów.
7. Zastąp ręczny cleanup obiektem RAII.
8. Złap wyjątek przez referencję i zachowaj typ dynamiczny.
9. Dodaj kontekst na granicy warstwy bez podwójnego logowania.
10. Zademonstruj stack unwinding kolejnością destruktorów.

## Poziom 3 — gwarancje

11. Określ, czy operacja zapewnia no-throw, strong, basic czy brak gwarancji.
12. Zaimplementuj aktualizację stanu przez copy-and-swap.
13. Przetestuj obiekt po wyjątku podczas drugiego kroku aktualizacji.
14. Sprawdź konsekwencję wyjątku wychodzącego z funkcji `noexcept`.
15. Oceń `noexcept` operacji przenoszenia typu przechowywanego w `vector`.

## Poziom 4 — typy wynikowe

16. Użyj `optional` dla wyszukania nieobowiązkowej wartości.
17. Użyj `expected` dla parsera z typowanym błędem.
18. Porównaj ten sam kontrakt zapisany wyjątkiem i wartością wynikową.
19. Połącz dwie operacje `expected` bez utraty kontekstu błędu.
20. Zaprojektuj enum błędów stabilny dla wywołującego.

## Poziom 5 — assertions i granice

21. Dodaj assertion dla niezmiennika wewnętrznego, nie danych zewnętrznych.
22. Zmień błędną assertion walidującą plik na normalną obsługę błędu.
23. Zdefiniuj precondition funkcji pracującej na `span`.
24. Przygotuj test procesu dla kontrolowanego zakończenia po naruszeniu kontraktu.
25. Sporządź tabelę polityki błędów dla biblioteki, CLI i serwera.

## Zadanie końcowe

Zaprojektuj import konfiguracji składający się z odczytu, parsowania, walidacji i atomowego zastosowania. Wybierz mechanizm błędu na każdej granicy, zachowaj poprzednią konfigurację przy niepowodzeniu i dodaj testy braku pliku, złej składni, naruszenia reguł domenowych oraz wyjątku podczas budowy nowego stanu.
