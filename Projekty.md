[← Spis treści](README.md)

# Mapa projektów portfolio

Wybierz jeden projekt odpowiadający luce wykrytej w diagnozie. Najpierw doprowadź go od wejścia do wyniku i testu błędu, potem rozbudowuj. Poniższe trzydzieści propozycji jest rozwiniętych w dziale 30; kompletne, uruchamiane przykłady znajdują się osobno w [laboratoriach](praktyka/README.md).

## Narzędzia CLI i automatyzacja

- [Inspektor danych CSV](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)
- [Graf zależności CMake](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)
- [Build Doctor](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)
- [Migrator konfiguracji](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)
- [Generator informacji o wydaniu](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)

## Systemy plikowe i wyszukiwanie

- [Wyszukiwarka duplikatów](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)
- [Indeksator dokumentów](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)
- [Snapshot backup](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)
- [Silnik wyszukiwania logów](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)
- [Planer synchronizacji katalogów](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)

## Parsery, interpretery i silniki

- [Parser konfiguracji](30_projekty_premium/03_parsery_interpretery_i_silniki.md)
- [Interpreter wyrażeń](30_projekty_premium/03_parsery_interpretery_i_silniki.md)
- [Silnik szablonów](30_projekty_premium/03_parsery_interpretery_i_silniki.md)
- [Język zapytań do logów](30_projekty_premium/03_parsery_interpretery_i_silniki.md)
- [Maszyna wirtualna bytecode](30_projekty_premium/03_parsery_interpretery_i_silniki.md)

## Sieć, bazy i usługi

- [Usługa skracania adresów](30_projekty_premium/04_siec_bazy_i_uslugi.md)
- [Ingestor telemetrii](30_projekty_premium/04_siec_bazy_i_uslugi.md)
- [Rejestr artefaktów](30_projekty_premium/04_siec_bazy_i_uslugi.md)
- [Usługa harmonogramu zadań](30_projekty_premium/04_siec_bazy_i_uslugi.md)
- [Serwis feature flags](30_projekty_premium/04_siec_bazy_i_uslugi.md)

## Współbieżność, runtime i obserwowalność

- [Executor zadań](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)
- [Mini runtime aktorów](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)
- [Współbieżny cache](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)
- [Kolektor śladów](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)
- [Silnik potoków danych](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)

## Systemy rozproszone i capstone

- [Platforma zamówień](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)
- [Event-sourced inventory](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)
- [Rozproszona kolejka pracy](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)
- [Laboratorium replikowanego KV](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)
- [Bezpieczna usługa aktualizacji](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)

## Co oddać do recenzji

Działający kod i polecenia budowania od czystego katalogu, kontrakt wejścia/wyjścia, limity, testy sukcesu i awarii, opis ownership i zakończenia pracy oraz pomiar najważniejszego kosztu. Dla zewnętrznego adaptera potrzebny jest test rzeczywistego protokołu; fake domenowy nie zastępuje integracji.

[Proces realizacji](30_projekty_premium/ZESTAW-CWICZEN.md) prowadzi przez zakres, ADR, prototyp ryzyka, testy i wydanie. [Pogłębiona ścieżka](sciezka_nauki.md) łączy projekty z mechaniką języka.
