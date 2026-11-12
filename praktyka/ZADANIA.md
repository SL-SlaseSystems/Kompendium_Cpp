[← Laboratoria](README.md) · [Ścieżka nauki](../sciezka_nauki.md)

# Dwanaście prób pogłębienia projektu

Nie implementuj wszystkiego jednocześnie. Wybierz jedną zmianę, najpierw opisz jej kontrakt i test odróżniający poprawną implementację od błędnej. Rozwiązania poniżej podają kierunek i kryteria recenzji, a nie gotowy kod do przepisania.

## 1. Parametryzowany parser

Rozszerz parser na typy całkowite z wyłączeniem bool. Zaprojektuj wynik tak, aby dla unsigned minus był odrzucany, a granice zależały od typu. Sprawdź zero, minimum, maksimum, jedną cyfrę za dużo i niezużyty sufiks.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Oprzyj implementację na odpowiednim przeciążeniu `from_chars` i ograniczeniu typu. Nie parsuj wszystkiego przez int ani nie przerzucaj problemu na późniejsze rzutowanie. Dopuszczalność typu w concept i poprawność gramatyki wejścia są dwoma oddzielnymi kontraktami. Wyłączenie bool powinno dawać czytelną diagnostykę.

</details>

## 2. Limit zasobów parsera

Dodaj limit długości argumentu i osobny błąd przekroczenia limitu. Określ, czy sprawdzasz go przed gramatyką. Testy: limit minus jeden, limit, limit plus jeden i same zera w bardzo długim ciągu.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Limit badaj przed parsowaniem, jeśli celem jest ograniczenie pracy. Zera wiodące mogą nie powodować przepełnienia, lecz nadal wymagają przejrzenia danych. Błąd zasobów nie powinien udawać błędu zakresu wartości liczbowej. Dokumentacja musi określać priorytet błędów.

</details>

## 3. Wczytywanie strumienia

Dodaj tryb czytania liczb z wejścia standardowego. Rozróżnij koniec danych, pusty rekord, błąd formatu i błąd I/O. Ustal, czy raport częściowy jest dozwolony. Przetestuj ostatni wiersz bez newline i błąd w środku danych.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Oddziel parser pojedynczego rekordu od źródła danych. Nie opieraj pętli na wcześniejszym `eof()`: stan wynika z próby odczytu. Limit wiersza wymaga uwagi, bo zwykłe `getline` może najpierw zaalokować dowolnie duży bufor. Testuj politykę wyniku procesu, nie tylko funkcję pomocniczą.

</details>

## 4. Bezpieczne mnożenie pieniędzy

Dodaj mnożenie `Money` przez nieujemną liczbę sztuk. Rozpoznaj przepełnienie bez wykonywania przepełniającej operacji. Testy obejmują 0, 1, maksimum, wartości ujemne i minimalne int64.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Nie stosuj `abs(min)`, którego wynik nie mieści się w tym samym signed typie. Rozbij analizę według znaków i przypadków zero/jeden albo użyj starannie zaprojektowanej reprezentacji bez znaku. Sam iloczyn obliczony w int64 i zbadany później narusza warunek zadania. Sprawdź też konwersję typu liczby sztuk.

</details>

## 5. Rabat i polityka zaokrąglania

Zaprojektuj rabat jako wymierną część kwoty, bez double. Czy 1 grosz razy 1/2 daje 0 czy 1? Co z kwotą ujemną i połową dokładnie między reprezentowalnymi wynikami?

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Najpierw wybierz politykę: np. half-to-even lub ku zeru. Nie ma uniwersalnej odpowiedzi domenowej. Zabezpiecz także wynik pośredniego mnożenia. Testy powinny zawierać remisy dodatnie i ujemne oraz przypadek, gdzie wynik końcowy się mieści, ale naiwny iloczyn pośredni nie.

</details>

## 6. Silna gwarancja aktualizacji sald

Przelew pomiędzy dwoma saldami ma aktualizować oba albo żadne. Wstrzyknij błąd między przygotowaniem a zatwierdzeniem. Rozdziel projekt jednowątkowy od synchronizacji wielu przelewów.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Policz i zweryfikuj oba nowe salda przed zmianą stanu, a commit wykonaj operacjami o wymaganej gwarancji. RAII nie przywraca automatycznie wcześniejszych wartości. W wariancie współbieżnym oba salda muszą być chronione przez spójny protokół, z ustaloną kolejnością blokad albo równoważnym mechanizmem unikania deadlock.

</details>

## 7. Punkty liniaryzacji kolejki

Dla wyścigu `push(7)` z `close()` opisz wszystkie legalne wyniki. Wskaż punkt, w którym przyjęcie elementu staje się faktem, oraz moment rozstrzygnięcia odrzucenia. Czy notify jest takim punktem?

<details><summary>Wskazówka i kryterium rozwiązania</summary>

O rozstrzygnięciu decydują chronione mutexem odczyt flagi i zmiana kontenera. `close` ustawia flagę pod tym samym mutexem. Element przyjęty wcześniej pozostaje do odebrania; producent, który zobaczy zamknięcie, zwróci false. Notify umożliwia postęp oczekujących, ale nie określa przyjęcia danych.

</details>

## 8. Dlaczego test sumy nie wystarcza

Zaprojektuj test wielu producentów i konsumentów, który wykryje zgubienie elementu oraz duplikat, nawet jeśli suma pozostaje zgodna. Nie zakładaj kolejności zakończenia konsumentów.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Nadaj elementom rozłączne identyfikatory i policz wystąpienia każdego. Wymagaj dokładnie jednego. Odczyt liczników wykonaj po dołączeniu wątków. Oddziel test dokładności dostarczenia od testu FIFO; wielowątkowe zapisy wyników mogą mieć inną kolejność niż pobrania z kolejki.

</details>

## 9. Oczekiwanie z deadline

Dodaj `pop_until` z rozróżnieniem wartości, zamknięcia i timeout. Co się dzieje, gdy dane pojawiają się w pobliżu deadline? Nie obiecuj dokładności zegara ani uruchomienia wątku w konkretnej chwili.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Użyj jednego deadline i predykatu stanu; po przebudzeniu ponownie oceń warunek pod mutexem. Przy każdym spurious wakeup nie zaczynaj pełnego timeout od początku. Dla względnego upływu czasu wybierz monotoniczny zegar. Testy muszą rozróżniać wyniki kontraktu bez ścisłych progów czasowych zależnych od szybkości CI.

</details>

## 10. Zamknięcie a anulowanie

Dodaj osobną operację przerwania, która odrzuca oczekujące elementy. Zachowaj dotychczasowe `close`, które je opróżnia. Zdefiniuj wyniki `push` i `pop`, gdy stop, dane i close występują jednocześnie.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Potrzebujesz jawnej maszyny stanów i priorytetów, np. abort ma pierwszeństwo nad pobraniem. `optional<T>` może już nie wystarczyć do opisania przyczyn końca. Przeanalizuj lifetime odrzuconych obiektów oraz wykonywanie destruktorów pod blokadą. Sam stop token bez notify nie kończy zwykłego wait.

</details>

## 11. Wyjątek przy alokacji

Załóż, że alokacja kontenera w `push` może rzucić. Jakie gwarancje stanu i postępu chcesz dać pozostałym producentom? Oddziel brak uszkodzenia danych od braku uśpienia mimo wolnego miejsca.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Sprawdź gwarancję kontenera dla użytego typu. Jeśli obudzony producent rezygnuje po wyjątku, potrzebne może być przekazanie powiadomienia kolejnemu oczekującemu; wersja referencyjna już zawiera tę ścieżkę. Uzasadnij jej obecność. W swojej rozszerzonej wersji zastosuj kontrolowany alokator, test bez utraty istniejących danych i opis zachowania pozostałych wątków. Nie wstrzykuj globalnie losowych awarii do całego procesu testowego.

</details>

## 12. Eksperyment wydajnościowy

Porównaj pojemności kolejki 1, 8 i 128 dla pracy CPU oraz I/O. Oddziel throughput, opóźnienie i maksymalną ilość oczekujących danych. Przedstaw wynik, który może uzasadnić pozostanie przy wersji sekwencyjnej.

<details><summary>Wskazówka i kryterium rozwiązania</summary>

Najpierw ustal workload i wykorzystaj wyniki pracy, żeby optymalizator jej nie usunął. Raportuj konfigurację, powtórzenia i rozrzut. Więcej wątków zwiększa również koszty blokad, przełączeń i pamięci. Pojemność kolejki nie jest liczbą wszystkich obiektów istniejących w producentach i konsumentach. Brak przyspieszenia jest wartościowym wynikiem, jeśli pomiar jest uczciwy.

</details>
