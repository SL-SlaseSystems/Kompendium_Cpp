[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Systemy rozproszone i capstone

Kolekcja zawiera pięć projektów, które dają się pokazać jako działający artefakt, testy i zapis decyzji. Minimalny zakres jest celowo mniejszy od pełnego produktu: najpierw zamknij pionowy przepływ, potem rozszerzaj go na podstawie pomiaru oraz ryzyka. Wymagane działy są mapą powrotu do teorii, a nie listą technologii do użycia za wszelką cenę.

~~~cpp
#include <array>
#include <cassert>
#include <string_view>

struct Portfolio06Milestone { std::string_view name; bool verified; };

constexpr bool releasable(std::array<Portfolio06Milestone, 3> plan) {
    for (const auto& item : plan) if (!item.verified) return false;
    return true;
}

int main() {
    constexpr std::array plan{
        Portfolio06Milestone{"działający pion", true},
        Portfolio06Milestone{"test błędu", true},
        Portfolio06Milestone{"instrukcja odtworzenia", true},
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

### 1. Platforma zamówień

- **Poziom:** ekspercki.
- **Efekt portfolio:** capstone sieci, trwałości, zdarzeń, telemetrii i release.
- **Problem:** Przyjęcie, płatność oraz realizacja kończą się w różnym czasie i mogą być ponawiane.
- **Minimalny zakres:** API, baza, outbox, konsumenci, saga, tracing, kontenery i podpisany release.
- **Wymagane działy:** 20–29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 2. Event-sourced inventory

- **Poziom:** ekspercki.
- **Efekt portfolio:** replay, snapshoty i ewolucja schematu.
- **Problem:** Stan magazynu musi być odtwarzalny, a zdarzenia kompatybilne w czasie.
- **Minimalny zakres:** Append-only log, aggregate, optimistic concurrency, snapshot i migracja eventów.
- **Wymagane działy:** 20–29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 3. Rozproszona kolejka pracy

- **Poziom:** ekspercki.
- **Efekt portfolio:** delivery semantics i operacyjne SLO.
- **Problem:** Wielu workerów rywalizuje o pracę, a awaria może nastąpić przed potwierdzeniem.
- **Minimalny zakres:** Broker, lease, retry DLQ, idempotentny handler, metryki i rollout.
- **Wymagane działy:** 20–29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 4. Laboratorium replikowanego KV

- **Poziom:** ekspercki.
- **Efekt portfolio:** edukacyjny model quorum i partycji.
- **Problem:** Repliki mogą widzieć różną kolejność zapisów i chwilowo się nie komunikować.
- **Minimalny zakres:** Trzy węzły w jednym procesie, wersje, quorum, symulator partycji i historia.
- **Wymagane działy:** 20–29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie. Usługa ma limity, telemetryczną redakcję, SBOM i powtarzalny release z możliwością rollbacku.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi. Obejmij sieć, prawdziwy silnik bazy w integracji, korelację trace oraz smoke test wydanego artefaktu.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 5. Bezpieczna usługa aktualizacji

- **Poziom:** ekspercki.
- **Efekt portfolio:** supply chain od artefaktu do kontrolowanego rollout.
- **Problem:** Klient musi przyjąć wyłącznie zgodny, autentyczny i niecofnięty artefakt.
- **Minimalny zakres:** Manifest, digest, podpis, kanały rollout, audit, rollback policy i obserwowalność.
- **Wymagane działy:** 20–29.
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
