[← Mapa działu](../03_pamiec_i_czas_zycia/README.md) · [Spis treści](../README.md)

# Ćwiczenia: dowód ważności obiektu

Rysuj oddzielnie właściciela, obiekt i nieposiadające odwołania. Dla każdego zadania wskaż ostatni dozwolony moment użycia odwołania. Sam adres oraz fakt, że „pamięć nadal wygląda dobrze”, nie wystarczają jako uzasadnienie.

## 1. Pamięć została, obiekt zniknął

**Wejście:** `std::optional<Record> slot` zawiera rekord; klient przechowuje `Record& r = *slot`, po czym wywołuje `slot.reset()`. **Oddaj:** oś czasu i bezpieczną wersję interfejsu odczytu. Uwzględnij pusty optional oraz ponowne `emplace`. Kryterium: klient nie używa referencji po resecie. **Wskazówka:** czas życia składowanej wartości nie jest czasem życia całego optional.

<details><summary>Rozwiązanie i uzasadnienie</summary>

`reset` kończy czas życia `Record`, chociaż sam `slot` i jego przestrzeń pozostają. Nie wolno odczytać rekordu przez `r` po resecie. Oferuj operację ograniczoną do czasu pożyczania albo kopię wyniku i dokumentuj zakaz mutacji właściciela podczas pożyczania. Po `emplace` uzyskaj nowe odwołanie zamiast opierać API na szczegółach zastępowania obiektów. [Lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md).

</details>

## 2. Parsowanie zwracające cudze bajty

**Wejście:** `first_field` zwraca `std::string_view` do pierwszego pola argumentu `std::string_view`; klient przekazuje tymczasowy `std::string`. **Oddaj:** diagnozę przypisania wyniku do zmiennej oraz dwa kontrakty naprawy. Rozważ pusty argument i brak separatora. **Wskazówka:** parametr widoku nie przedłuża życia właściciela bajtów.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Tymczasowy string znika na końcu pełnego wyrażenia wywołania, więc zachowany widok zwisa. Pierwszy kontrakt zwraca własny `std::string`. Drugi wymaga właściciela żyjącego dłużej niż wynik i przechowywania go przez klienta. Pusty argument daje pusty wynik, brak separatora całe wejście; nie rozwiązują one problemu właściciela. [Widoki](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md).

</details>

## 3. Nieudana konstrukcja dwóch zasobów

**Wejście:** konstruktor najpierw otwiera plik, potem rezerwuje drugi zasób, którego pozyskanie rzuca wyjątek. Plik zamyka wyłącznie destruktor kompletnej klasy. **Oddaj:** analizę wycieku i projekt składowych odporny na wyjątek. Kryterium: każdy pomyślnie pozyskany zasób zwalnia się dokładnie raz. **Wskazówka:** destruktor nieukończonego obiektu nie wykonuje ciała.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Destruktory już skonstruowanych baz i składowych zostają wywołane, lecz ciało destruktora całego obiektu nie. Surowy uchwyt pliku jako pole nie zamknie się sam. Umieść go w małym typie RAII z poprawnym deleterem, a drugi zasób w osobnym właścicielu. Kolejność inicjalizacji ustala deklaracja pól. [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md).

</details>

## 4. Cykl bez zewnętrznych właścicieli

**Wejście:** `Parent` ma `shared_ptr<Child>`, a `Child` ma `shared_ptr<Parent>`; połączono parę i usunięto wszystkie uchwyty klienta. **Oddaj:** graf liczników i zmianę reprezentacji dla relacji dziecko–rodzic. Obsłuż próbę dostępu do rodzica po jego zniszczeniu. **Wskazówka:** współdzielona własność nie jest odśmiecaniem grafu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Każdy obiekt nadal ma jednego silnego właściciela wewnątrz cyklu, więc oba pozostają żywe. Jeśli rodzic posiada dziecko, kierunek powrotny reprezentuj przez `weak_ptr`. Dziecko wywołuje `lock` i sprawdza wynik; chwilowy silny uchwyt utrzymuje rodzica przy życiu podczas dostępu. Samo sprawdzenie `expired` nie zastępuje `lock`. [Smart pointery](../03_pamiec_i_czas_zycia/05_smart_pointery.md).

</details>

## 5. Fabryka typu nieprzenoszalnego

**Wejście:** `Token` ma dostępny domyślny konstruktor i destruktor, ale usunięte kopiowanie oraz przenoszenie. Porównaj `return Token{};` i `Token t; return t;`. **Oddaj:** ocenę obu fabryk C++23 bez polegania na ustawieniach optymalizatora. **Wskazówka:** obowiązkowe tworzenie wartości wyniku i opcjonalne NRVO mają odmienne wymagania.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pierwsza fabryka jest poprawna: prvalue bezpośrednio inicjalizuje obiekt wyniku, więc kopiowanie ani przenoszenie nie jest potrzebne. Druga jest niepoprawna, ponieważ NRVO dla nazwanego lokalnego obiektu pozostaje opcjonalne, a wymagana ścieżka bez niego nie ma dostępnego konstruktora. Dodanie `std::move(t)` nie pomaga i dodatkowo wyklucza NRVO. [Zwracanie wartości](../03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md).

</details>

## 6. Span po zmianie właściciela

**Wejście:** wektor ma `size()==capacity()==4`; utworzono span wszystkich elementów, a potem wykonano `push_back(5)`. **Oddaj:** analizę ważności spanu i dwie wersje kolejności operacji. Uwzględnij fakt, że po wcześniejszym `reserve` stary span może nadal obejmować tylko cztery elementy. **Wskazówka:** ważność adresu i długość widoku to osobne kwestie.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dodanie piątego elementu przekracza pojemność, powoduje realokację i unieważnia dotychczasowe odwołania. Utwórz span dopiero po modyfikacji albo zagwarantuj brak realokacji przez wcześniejsze `reserve`, zanim pożyczysz pamięć. Nawet ważny stary span zachowuje swój dawny rozmiar: nie obserwuje automatycznie nowej długości wektora. [Pożyczanie pamięci](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md).

</details>
