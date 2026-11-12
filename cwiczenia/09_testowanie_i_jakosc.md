[← Mapa działu](../09_testowanie_i_jakosc/README.md) · [Spis treści](../README.md)

# Ćwiczenia: wybór dowodu i kontrprzykładu

Dobre rozwiązanie określa badaną hipotezę, dane oraz granice wniosku. Nie traktuj liczby testów jako miary pokrycia semantyki. Jeden celny kontrprzykład może być cenniejszy od tysięcy powtórzeń tego samego scenariusza.

## 1. Test, którego Release nie wykonuje

**Wejście:** test zawiera wyłącznie `assert(parse("12") == 12)`; konfiguracja Release definiuje `NDEBUG`. Mutacja parsera zwracająca zawsze zero nie psuje CI. **Oddaj:** minimalną naprawę testu i kryterium jego wiarygodności. Dodaj jeden poprawny i jeden błędny przypadek, bez testowania prywatnej implementacji. **Wskazówka:** sprawdź, czy badana funkcja jest w ogóle wywołana.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Użyj mechanizmu testowego aktywnego w każdej konfiguracji albo jawnego warunku zwracającego niezerowy kod procesu. Testuj poprawne `12` i np. odrzucenie `12x`, jeśli kontrakt wymaga pełnego wejścia. Wprowadź chwilowo błędny wynik parsera i potwierdź porażkę testu w Release. Test, który nie wykrywa celowej usterki, nie uzasadnia poprawności. [Testy](../09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md).

</details>

## 2. Sanitizer a rodzaj błędu

**Wejście:** A: odczyt usuniętej tablicy; B: przepełnienie `int`; C: niesynchronizowany zapis dwóch wątków do licznika. **Oddaj:** dobór ASan, UBSan lub TSan oraz konfigurację eksperymentów. Wyjaśnij, czego nie dowodzi cisza narzędzia. **Wskazówka:** nie wszystkie sanitizery dają się sensownie łączyć w jednym wykonaniu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

ASan kieruj na A, UBSan na B, TSan na C. Przygotuj osobny wariant TSan, a ASan i UBSan łącz tylko w obsługiwanej konfiguracji. Podaj symbole i dane wymuszające podejrzaną ścieżkę. Brak raportu oznacza brak wykrycia w badanym wykonaniu, nie formalny brak błędów ani pełne pokrycie wszystkich przeplotów. [Sanitizery](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md).

</details>

## 3. Własność niezależna od implementacji

**Wejście:** funkcja usuwa duplikaty z posortowanego wektora liczb. Autor testu porównuje wynik z drugim wywołaniem tej samej funkcji. **Oddaj:** trzy niezależne własności i generator przypadków. Uwzględnij pusty wektor, same duplikaty oraz skrajne liczby. **Wskazówka:** równość dwóch identycznie błędnych wyników niczego nie rozstrzyga.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wynik powinien być ściśle rosnący, zawierać dokładnie ten sam zbiór wartości i być idempotentny. Równość zbiorów sprawdzaj niezależną reprezentacją referencyjną; sama idempotencja nie wystarczy, bo funkcja zwracająca pusty wynik ją spełnia. Generuj krótkie wektory z małej dziedziny oraz osobno wartości graniczne, po czym sortuj wejścia. [Własności](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md).

</details>

## 4. Benchmark mierzący sprzątanie po poprzednim przebiegu

**Wejście:** porównujesz wyszukiwanie liniowe i haszowane. W pierwszym pomiarze tworzysz strukturę oraz szukasz, w drugim tylko szukasz w gotowej mapie; dane to zawsze pierwszy element. **Oddaj:** poprawny eksperyment dla aplikacji wykonującej tysiąc wyszukiwań po jednorazowym wczytaniu. **Wskazówka:** koszt przygotowania zależy od rzeczywistego scenariusza.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Mierz osobno budowę i wyszukiwanie, a potem porównaj sumę budowy oraz tysiąca operacji. Przygotuj trafienia w różnych pozycjach i nietrafienia z reprezentatywnego rozkładu. Konsumuj wynik, powtarzaj pomiary i raportuj rozrzut, rozmiar danych oraz konfigurację. Nie ekstrapoluj z trafienia w pierwszy element na cały profil aplikacji. [Benchmarki](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md).

</details>

## 5. Ostrzeżenie to trop, nie specyfikacja

**Wejście:** pętla używa `int i` i porównuje go z `vector.size()`; kompilator zgłasza mieszanie znaków. Autor dodaje rzutowanie rozmiaru na `int`. **Oddaj:** analizę nowego ryzyka i poprawną wersję dla iteracji bez indeksu oraz z indeksem. Uwzględnij rozmiar większy od `INT_MAX`. **Wskazówka:** wyciszenie diagnostyki może usunąć informację o błędzie.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Konwersja dużego rozmiaru do `int` nie zachowuje wymaganej wartości i może zepsuć granicę pętli. Bez indeksu użyj pętli zakresowej. Z indeksem użyj odpowiedniego typu rozmiaru i bezpiecznej relacji, a gdy potrzebujesz różnic ze znakiem, świadomie dobierz typ i zakres. Zrozum przyczynę ostrzeżenia przed zmianą kodu. [Analiza statyczna](../09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md).

</details>

## 6. Fuzzer znalazł cztery megabajty

**Wejście:** parser formatu `length:payload` pada dla dużego pliku. Specyfikacja wymaga odrzucenia długości większej niż pozostała liczba bajtów. **Oddaj:** strategię minimalizacji i trzy małe ziarna korpusu. Kryterium: zachowany kontrprzykład uruchamia tę samą wadliwą ścieżkę. **Wskazówka:** minimalizuj dane z zachowaniem objawu, nie tylko rozmiaru.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Usuwaj bloki i upraszczaj pole długości, potwierdzając po każdym kroku ten sam raport. Ziarna mogą obejmować `0:`, `1:a` i `2:a`. Ostatnie sprawdza brakujące bajty; dodaj osobno przepełnienie długości i brak dwukropka. Regresja powinna oczekiwać kontrolowanego błędu, a nie jedynie braku awarii procesu. [Fuzzing](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md).

</details>
