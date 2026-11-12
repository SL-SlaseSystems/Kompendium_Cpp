[← Spis treści](../README.md)

# Transakcje i poziomy izolacji

Transakcja wyznacza jednostkę zatwierdzenia, lecz sama obecność `BEGIN` nie wystarcza do ochrony reguły biznesowej. Jeżeli dwie decyzje zależą od odczytanej liczby wolnych miejsc, trzeba ustalić, czy mogą jednocześnie użyć tej samej informacji. Izolacja określa dopuszczalne historie współbieżnych transakcji. Trwałość odpowiada na inne pytanie: co pozostanie po awarii po potwierdzonym zatwierdzeniu. Nie wyprowadzaj jednej gwarancji z drugiej.

W C++ typ `Transaction` może pilnować, aby zakres zakończył się jawnym `commit()` albo awaryjnym rollbackiem. Nie potrafi jednak nadać silnikowi dodatkowego poziomu izolacji. Nie usunie również niepewności, gdy po wysłaniu COMMIT połączenie zostało zerwane przed odebraniem wyniku. W takim przypadku aplikacja potrzebuje sposobu odszukania wyniku operacji po stabilnym identyfikatorze.

## Jak to działa krok po kroku

Rozpocznij od niezmiennika, a nie od nazwy poziomu. W grafiku dyżurów co najmniej jedna osoba musi pozostawać dostępna. Operacja wypisania lekarza odczytuje liczbę dyżurujących i zmienia jego własny wiersz, jeżeli liczba przekracza jeden. Dwie takie operacje na różnych wierszach mogą nie kolidować zapisem, mimo że razem łamią regułę.

Pierwszy przykład jest harmonogramem dla **dwóch sesji PostgreSQL**, nie jednym skryptem wykonywanym od góry. Polecenia uruchamiaj w podanej kolejności, zachowując otwarte transakcje. Schemat tworzysz raz, poza nimi. Warunek biznesowy celowo jest decyzją aplikacji po odczycie wyniku; nie stanowi ograniczenia zadeklarowanego w tabeli.

~~~sql
-- Przygotowanie, osobna sesja administracyjna:
CREATE TABLE dyzur (
    lekarz integer PRIMARY KEY,
    aktywny boolean NOT NULL
);
INSERT INTO dyzur VALUES (1, true), (2, true);

-- Krok 1, sesja A:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM dyzur WHERE aktywny; -- 2

-- Krok 2, sesja B:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM dyzur WHERE aktywny; -- 2

-- Krok 3, sesja A: aplikacja uznała, że może wypisać lekarza 1.
UPDATE dyzur SET aktywny = false WHERE lekarz = 1;
COMMIT;

-- Krok 4, sesja B: nadal działa decyzja oparta na wyniku 2.
UPDATE dyzur SET aktywny = false WHERE lekarz = 2;
COMMIT;

-- Po obu commitach, dowolna sesja:
SELECT count(*) FROM dyzur WHERE aktywny; -- 0
~~~

To write skew: spójne odczyty indywidualnych transakcji prowadzą do niespójnej decyzji zbiorowej. Gdyby A wykonała się w całości przed B, B odczytałaby jeden dyżur i odmówiła zmiany. Odwrotna kolejność także pozostawiłaby jedną osobę. Uzyskanego wyniku nie da się więc wyjaśnić żadną szeregową kolejnością tych dwóch operacji.

Po odtworzeniu schematu można zmienić oba `BEGIN` na `SERIALIZABLE`. W PostgreSQL takie zależności mogą spowodować odrzucenie jednej transakcji jako błędu serializacji. Aplikacja powtarza wtedy całą decyzję z nowym odczytem, a nie samo nieudane `UPDATE`. Nie zakładaj, że zawsze przegra wskazana sesja ani że konflikt ujawni się dopiero przy COMMIT.

## Pogłębienie mechanizmu

W PostgreSQL Read Committed nadaje zwykłemu SELECT migawkę na początku polecenia. Repeatable Read zachowuje migawkę od pierwszego polecenia niebędącego sterowaniem transakcją; zapobiega także fantomom, lecz dopuszcza anomalie serializacji. Read Uncommitted zachowuje się tam jak Read Committed. Serializable chroni efekt równoważny szeregowemu wykonaniu zatwierdzonych transakcji, kosztem możliwości ich odrzucania. To gwarancje konkretnego silnika, nie uniwersalna interpretacja nazw SQL. [Dokumentacja PostgreSQL: izolacja](https://www.postgresql.org/docs/current/transaction-iso.html).

Niepowtarzalny odczyt oznacza zmianę wartości już odczytanego wiersza; fantom oznacza zmianę zbioru spełniającego predykat. Zwalczanie ich nie wyczerpuje wszystkich reguł biznesowych, co pokazuje dyżur. Inny błąd, utracona aktualizacja, powstaje przy schemacie „odczytaj saldo, oblicz w C++, zapisz stałą wartość”. Dla pojedynczego licznika lepsze bywa atomowe `UPDATE ... SET saldo = saldo + :delta`, z warunkiem i sprawdzeniem liczby zmienionych wierszy.

Blokowanie musi obejmować wspólny punkt konfliktu. Zablokowanie wyłącznie wiersza wypisywanego lekarza pozostawia write skew, bo każdy blokuje inny wiersz. Alternatywą jest wiersz koordynujący konkretny grafik, blokowany przez wszystkich modyfikujących przed ponownym sprawdzeniem reguły. W PostgreSQL Read Committed osobne polecenie odczytu po uzyskaniu blokady zobaczy nowo zatwierdzone zmiany. Konsekwencją jest świadome szeregowanie operacji danego grafiku, a także obowiązek przestrzegania protokołu przez każdy zapis.

Nie trzymaj transakcji otwartej podczas rozmowy z użytkownikiem ani nieograniczonego wywołania HTTP. Długa transakcja przedłuża czas blokad i życia migawek. Krótka granica obejmująca walidację opartą na bieżących danych i zapis ułatwia bezpieczne ponowienie. Efekt zewnętrzny wyprowadź przez outbox lub inny jawny protokół; rollback bazy nie cofnie wysłanego e-maila.

## Drugi przykład

SQLite nie udostępnia takiej samej palety poziomów jak PostgreSQL. Typowo izoluje połączenia, dopuszczając jednego pisarza naraz. W rollback journal czytelnicy mogą współistnieć z początkiem zapisu, lecz przed zmianą pliku bazy pisarz potrzebuje dostępu wyłącznego. WAL pozwala czytelnikowi zachować starą migawkę podczas zapisu innego połączenia. Próba awansu nieaktualnej migawki do pisarza może zakończyć się `SQLITE_BUSY_SNAPSHOT`. [SQLite: izolacja](https://www.sqlite.org/isolation.html).

Poniższy harmonogram wymaga plikowej bazy `demo.db` i dwóch niezależnych połączeń bez shared cache. Polecenie ustawienia WAL wykonaj przed rozpoczęciem sesji. Zwykłe `:memory:` na każdym połączeniu utworzyłoby dwie różne bazy i nie odtworzyłoby mechanizmu.

~~~sql
-- Przygotowanie, raz:
PRAGMA journal_mode = WAL;
CREATE TABLE stan (id INTEGER PRIMARY KEY, wartosc INTEGER NOT NULL);
INSERT INTO stan VALUES (1, 10);

-- Krok 1, połączenie A:
BEGIN;
SELECT wartosc FROM stan WHERE id = 1; -- 10, migawka ustalona

-- Krok 2, połączenie B:
BEGIN IMMEDIATE;
UPDATE stan SET wartosc = 20 WHERE id = 1;
COMMIT;

-- Krok 3, połączenie A:
SELECT wartosc FROM stan WHERE id = 1; -- nadal 10
UPDATE stan SET wartosc = wartosc + 1 WHERE id = 1;
-- SQLITE_BUSY_SNAPSHOT (517 przy udostępnieniu rozszerzonego kodu)
ROLLBACK;

-- Krok 4, połączenie A: cała decyzja od nowa
BEGIN IMMEDIATE;
SELECT wartosc FROM stan WHERE id = 1; -- 20
UPDATE stan SET wartosc = wartosc + 1 WHERE id = 1;
COMMIT;
~~~

`BEGIN DEFERRED` odkłada wybór transakcji odczytu lub zapisu do dostępu do danych. `BEGIN IMMEDIATE` od razu próbuje rozpocząć zapis i może zwrócić BUSY. W WAL `EXCLUSIVE` zachowuje się pod tym względem jak `IMMEDIATE`; w innych trybach dodatkowo blokuje czytelników. COMMIT zwracający BUSY może pozostawić transakcję aktywną i pozwolić powtórzyć sam COMMIT. [SQLite: sterowanie transakcjami](https://www.sqlite.org/lang_transaction.html).

To ostatnie rozróżnienie jest ważne dla adaptera C++: polityka „każdy BUSY oznacza nową transakcję” jest za mało precyzyjna. Dla starej migawki samo czekanie nie naprawi historii; trzeba zakończyć transakcję i odczytać dane ponownie. Dla oczekiwania na blokadę ograniczony busy timeout może pomóc. Nadal musi mieścić się w deadline operacji.

## Porównanie i decyzje

Wybieraj najpierw sposób ochrony reguły: ograniczenie unikalności, pojedyncze warunkowe UPDATE, jawne blokady albo serializowalną transakcję. Każde rozwiązanie wymaga innego testu współbieżności. Test polegający na dwukrotnym uruchomieniu funkcji kolejno nie sprawdza żadnego z pokazanych przeplotów; potrzebne są kontrolowane punkty zatrzymania między odczytem i zapisem.

W wrapperze rozróżnij stany aktywna, zatwierdzona i zakończona błędem. `commit()` ma zwrócić wynik, zanim obiekt uzna transakcję za zakończoną. Destruktor wykonuje niezgłaszający cleanup i nie maskuje pierwotnego wyjątku. Po błędzie sprawdź kontrakt sterownika oraz stan połączenia; nie oddawaj do puli sesji pozostawionej w otwartej transakcji.

Budżet ponowień dotyczy całej operacji wraz z pobraniem połączenia i oczekiwaniem na blokady. Przy ponowieniu przelicz decyzję biznesową z nowych danych, zachowując identyfikator logicznej operacji. Dzięki temu poprawa izolacji nie zmieni się w niekontrolowane mnożenie pracy podczas przeciążenia.

## Ćwiczenia

1. Każdy lekarz blokuje `FOR UPDATE` wyłącznie swój wiersz. Czy naprawia to pierwszy przykład?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Zbiory zapisywanych i blokowanych wierszy nadal są rozłączne, a odczyt dotyczy obu. Potrzebny jest wspólny punkt konfliktu, właściwe ograniczenie modelu albo Serializable z obsługą ponowienia całej transakcji.

</details>

2. Po `SQLITE_BUSY_SNAPSHOT` program czeka sekundę i powtarza UPDATE bez ROLLBACK. Czy odzyskał aktualną migawkę?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Migawka należy do trwającej transakcji. Zakończ ją, rozpocznij nową i ponownie wykonaj odczyty, które uzasadniały zapis. Sam upływ czasu nie zmienia podstawy wcześniejszej decyzji.

</details>

## Powiązane tematy

- [SQLite i RAII połączenia](02_sqlite_i_raii_polaczenia.md)
- [Migracje, pooling i odporność](05_migracje_pooling_i_odpornosc.md)
- [Outbox, inbox i deduplikacja](../24_messaging_i_systemy_rozproszone/05_outbox_inbox_i_deduplication.md)
