[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Sieć, bazy i usługi

Kolekcja zawiera pięć projektów, które dają się pokazać jako działający artefakt, testy i zapis decyzji. Minimalny zakres jest celowo mniejszy od pełnego produktu: najpierw zamknij pionowy przepływ, potem rozszerzaj go na podstawie pomiaru oraz ryzyka. Wymagane działy są mapą powrotu do teorii, a nie listą technologii do użycia za wszelką cenę.

~~~cpp
#include <array>
#include <cassert>
#include <string_view>

struct Portfolio04Milestone { std::string_view name; bool verified; };

constexpr bool releasable(std::array<Portfolio04Milestone, 3> plan) {
    for (const auto& item : plan) if (!item.verified) return false;
    return true;
}

int main() {
    constexpr std::array plan{
        Portfolio04Milestone{"działający pion", true},
        Portfolio04Milestone{"test błędu", true},
        Portfolio04Milestone{"instrukcja odtworzenia", true},
    };
    static_assert(releasable(plan));
    assert(releasable(plan));
}
~~~

## Jak to działa krok po kroku

Wybierz projekt przez ryzyko, którego chcesz się nauczyć, a nie przez liczbę modnych bibliotek. Zapisz jednego odbiorcę, problem i mierzalny efekt. Następnie wytnij pionową iterację przechodzącą od wejścia do wyniku. Pierwsza wersja ma być mała, ale kompletna: buduje się od świeżego klonu, ma jeden test sukcesu, jeden test błędu i instrukcję uruchomienia.

Przed kodem przygotuj ADR dla najważniejszej decyzji oraz prototyp największej niewiadomej. Jeśli ryzykiem jest parser, fuzzuj mały harness; jeśli baza, sprawdź transakcję i awarię; jeśli współbieżność, zbuduj kontrolowany harmonogram. Dopiero wynik prototypu uzasadnia architekturę. Każdy kolejny milestone kończy się działającym artefaktem, nie zbiorem części czekających na wielkie połączenie.

## Pogłębienie mechanizmu

Portfolio ocenia się po jakości decyzji i dowodach, nie wyłącznie po liczbie funkcji. Zachowaj krótką historię commitów, testy kontraktu, profil albo raport bezpieczeństwa i jedno ograniczenie, którego świadomie nie rozwiązujesz. Publiczne demo nie może wymagać sekretów, prywatnej ścieżki ani ręcznie przygotowanej bazy. Dane przykładowe powinny być syntetyczne i licencjonowane do publikacji.

Dla każdego projektu ustal budżet: czas odpowiedzi, pamięć, rozmiar wejścia, równoległość albo czas odtworzenia. Budżet zmienia ogólną deklarację „działa” w kryterium. Jeśli projekt obejmuje sieć i trwałość, opisz stan po timeoutach oraz częściowym zapisie. Jeśli generuje artefakt, przypisz wersję, digest i pochodzenie. Jeśli działa długo, dodaj kontrolowany shutdown oraz podstawowe sygnały obserwowalności.

## Drugi przykład

Każdą iterację można opisać tą samą kartą, a jej zawartość jest częścią review:

~~~text
cel: jedna obserwowalna wartość dla użytkownika
ryzyko: największa niewiadoma techniczna lub produktowa
zakres: najmniejszy pion od wejścia do trwałego wyniku
dowód: test, pomiar, trace albo odtworzony scenariusz awarii
release: wersja, instrukcja, digest i znane ograniczenia
retrospektywa: czego dowiedzieliśmy się i co zmieniamy dalej
~~~

### 1. Usługa skracania adresów

- **Poziom:** zaawansowany.
- **Efekt portfolio:** pełny przepływ API–baza–telemetria–release.
- **Problem:** Krótki identyfikator musi być trwały, unikalny i bezpieczny dla wielokrotnych żądań.
- **Minimalny zakres:** HTTP API, SQLite/PostgreSQL adapter, cache, metryki i kontener release.
- **Wymagane działy:** 15, 20–23, 25–27, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 2. Ingestor telemetrii

- **Poziom:** ekspercki.
- **Efekt portfolio:** usługa streamingowa z backpressure i obserwowalnością.
- **Problem:** Klienci wysyłają paczki zdarzeń szybciej, niż storage potrafi je zapisać.
- **Minimalny zakres:** Endpoint batch, walidacja schematu, bounded queue, trwały zapis i dashboard.
- **Wymagane działy:** 15, 20–23, 25–27, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 3. Rejestr artefaktów

- **Poziom:** ekspercki.
- **Efekt portfolio:** integracja uploadu, digestów, SBOM i podpisów.
- **Problem:** Artefakt musi być adresowany treścią i powiązany z metadanymi pochodzenia.
- **Minimalny zakres:** Upload z limitem, SHA-256, metadata DB, download, SBOM i weryfikacja podpisu.
- **Wymagane działy:** 15, 20–23, 25–27, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 4. Usługa harmonogramu zadań

- **Poziom:** ekspercki.
- **Efekt portfolio:** kontrolowany czas, leasing i retry.
- **Problem:** Zadanie nie może zniknąć po awarii pracownika ani wykonywać się bez ograniczeń.
- **Minimalny zakres:** API zadań, trwały stan, leasing, worker, backoff, metryki i wydanie.
- **Wymagane działy:** 15, 20–23, 25–27, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 5. Serwis feature flags

- **Poziom:** ekspercki.
- **Efekt portfolio:** kontraktowe API, cache i bezpieczny rollout.
- **Problem:** Aplikacje potrzebują szybkiej decyzji flagi mimo chwilowej niedostępności serwera.
- **Minimalny zakres:** CRUD, reguły segmentacji, ETag, klient cache, audit log i proces release.
- **Wymagane działy:** 15, 20–23, 25–27, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.


## Porównanie i decyzje

Projekt średni ma pokazać poprawny model C++, testy i ergonomię użytkownika. Projekt zaawansowany powinien dodatkowo mieć granice adapterów, kontrolowane błędy i pomiar. Projekt ekspercki łączy awarie częściowe, operacyjność oraz proces wydania. Rozszerzenie nie podnosi automatycznie poziomu; wartość rośnie dopiero wtedy, gdy nowy zakres ma kontrakt i dowód.

Nie zaczynaj równocześnie pięciu propozycji. Ukończ jedną, opublikuj release i wykonaj retrospektywę. Drugi projekt wybierz tak, aby pokazywał inne ryzyko: po narzędziu CLI może to być sieć i baza, po usłudze — runtime lub parser. W ten sposób portfolio pokazuje szerokość bez sześciu wariantów tej samej aplikacji CRUD.

## Powiązane tematy

- [Mapa projektów](README.md)
- [Proces realizacji projektu](ZESTAW-CWICZEN.md)
- [Główna mapa portfolio](../Projekty.md)
