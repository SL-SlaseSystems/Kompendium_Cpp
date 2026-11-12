[← Mapa działu](../11_io_i_system/README.md) · [Spis treści](../README.md)

# Ćwiczenia: dane przekraczające granicę programu

Oddziel składnię formatu, stan operacji i politykę aplikacji. Każdy niekompletny odczyt oraz błąd końcowego zapisu musi mieć określony wynik. Nie zakładaj, że właściwości lokalnego dysku, zegara i biblioteki są uniwersalne.

## 1. Ostatni wiersz bez końcowego separatora

**Wejście:** trzy pliki zawierają odpowiednio pusty tekst, `alpha\nbeta\n` oraz `alpha\nbeta` bez ostatniego znaku nowej linii. **Oddaj:** pętlę zliczającą wiersze i oczekiwane wyniki. Rozróżnij poprawny koniec pliku od błędu urządzenia. **Wskazówka:** stan EOF jest skutkiem próby odczytu, a nie prognozą jego powodzenia.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Iteruj według powodzenia `getline`, przetwarzając każdy uzyskany wiersz; wyniki to 0, 2 i 2. Nie używaj `while(!eof())`, bo może przetworzyć nieudany odczyt. Po pętli warunek `input.bad() || !input.eof()` sygnalizuje błąd w tym schemacie; uwzględnij również skonfigurowaną maskę wyjątków strumienia. [Strumienie](../11_io_i_system/01_strumienie_i_formatowanie.md).

</details>

## 2. Ostatni fragment binarnego odczytu

**Wejście:** plik ma 11 bajtów, bufor 4. Pętla przetwarza blok tylko wtedy, gdy `read` zwróci strumień w stanie sukcesu. **Oddaj:** poprawny algorytm oraz liczby przetworzonych bajtów w kolejnych iteracjach. Sprawdź pusty plik i długość dokładnie podzielną przez cztery. **Wskazówka:** końcowy częściowy odczyt może dostarczyć dane razem z ustawionym EOF.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Po każdym `read` pobierz `gcount` i przetwórz dokładnie tyle bajtów, także gdy pełna operacja nie odczytała czterech. Dla 11 bajtów użyteczne fragmenty mają długości 4, 4, 3. Dopiero potem oceń koniec i błąd. Pusty plik nie daje fragmentu; dodatkowa próba po pełnych blokach może dać zero. [Pliki](../11_io_i_system/02_pliki_i_filesystem.md).

</details>

## 3. Ścieżka poprawna tekstowo, zły obiekt

**Wejście:** importer dopuszcza wyłącznie pliki pod katalogiem roboczym; sprawdza tekstowy prefiks po `lexically_normal`. Wewnątrz katalogu istnieje symlink wskazujący poza niego. **Oddaj:** kontrprzykład oraz granice rozwiązania przenośnym `filesystem`. Uwzględnij zmianę dowiązania po sprawdzeniu. **Wskazówka:** operacja leksykalna nie odczytuje systemu plików.

<details><summary>Rozwiązanie i uzasadnienie</summary>

`root/link/secret` zachowuje dozwolony prefiks, choć rozwiązuje się poza `root`. `canonical` pomaga poznać cel w danym momencie, ale nie usuwa wyścigu między kontrolą a otwarciem. Dla granicy bezpieczeństwa potrzebne są właściwe platformie operacje względem uchwytu katalogu i zasady obsługi symlinków. Samo porównanie napisów nie daje żądanej gwarancji. [Filesystem i TOCTOU](../11_io_i_system/02_pliki_i_filesystem.md).

</details>

## 4. Timeout po korekcie zegara

**Wejście:** operacja ma limit pięciu sekund, a aplikacja liczy deadline przez `system_clock`. Administrator cofa zegar o minutę podczas oczekiwania. **Oddaj:** dobór zegara dla timeoutu i dla znacznika w logu. Rozważ test bez faktycznego czekania pięciu sekund. **Wskazówka:** czas kalendarzowy i upływ czasu pełnią inne role.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Timeout opieraj na monotonicznym `steady_clock`; do znacznika kalendarzowego użyj `system_clock`. Nie odejmuj punktów różnych zegarów bez jawnego modelu konwersji. Wstrzyknij źródło czasu albo przekaż `now` do czystej logiki decyzji i testuj granice przed, równo i po deadline. Korekta czasu ściennego nie powinna przedłużać limitu. [Chrono](../11_io_i_system/03_chrono_i_czas.md).

</details>

## 5. Cztery kolejki z dziesięciu wyników

**Wejście:** idealnie równomierne źródło daje liczby 0–9; autor wybiera jedną z czterech kolejek roboczych przez modulo 4. **Oddaj:** rozkład prawdopodobieństwa i bezstronną metodę mapowania. Zdecyduj, co trzeba zapisać, aby odtworzyć symulację na innej bibliotece. **Wskazówka:** nie każda reszta ma tyle samo reprezentantów.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Prawdopodobieństwa to 3/10, 3/10, 2/10 i 2/10. Odrzucaj 8 oraz 9, a wartości 0–7 mapuj modulo 4; każda reszta ma dwóch reprezentantów. W praktyce użyj odpowiedniego rozkładu. Do bitowej odtwarzalności zapisz silnik, seed lub stan, kolejność wywołań i algorytm mapowania; implementacje rozkładów mogą się różnić. [Random](../11_io_i_system/04_random_i_numeryka.md).

</details>

## 6. Struktura nie jest protokołem

**Wejście:** komunikat zawiera 16-bitowy kod i 32-bitową długość, a autor wysyła `sizeof(Message)` bajtów surowej struktury. Odbiorca może mieć inną architekturę. **Oddaj:** definicję formatu bajtowego i stan parsera dla niepełnego nagłówka. Ustal limit długości i kolejność bajtów. **Wskazówka:** tryb binarny nie standaryzuje paddingu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Określ sześć oktetów (jednostek 8-bitowych) nagłówka w wybranym porządku, np. big-endian, po czym dokładnie wskazaną liczbę bajtów payload. Serializuj pola, nie reprezentację obiektu. Parser buforuje niepełny nagłówek, sprawdza limit przed alokacją i zbiera brakujący payload; pojedynczy odczyt nie musi odpowiadać komunikatowi. [Serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md).

</details>
