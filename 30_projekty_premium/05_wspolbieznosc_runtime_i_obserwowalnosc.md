[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Współbieżność, runtime i obserwowalność

Kolekcja zawiera pięć projektów, które dają się pokazać jako działający artefakt, testy i zapis decyzji. Minimalny zakres jest celowo mniejszy od pełnego produktu: najpierw zamknij pionowy przepływ, potem rozszerzaj go na podstawie pomiaru oraz ryzyka. Wymagane działy są mapą powrotu do teorii, a nie listą technologii do użycia za wszelką cenę.

~~~cpp
#include <array>
#include <cassert>
#include <string_view>

struct Portfolio05Milestone { std::string_view name; bool verified; };

constexpr bool releasable(std::array<Portfolio05Milestone, 3> plan) {
    for (const auto& item : plan) if (!item.verified) return false;
    return true;
}

int main() {
    constexpr std::array plan{
        Portfolio05Milestone{"działający pion", true},
        Portfolio05Milestone{"test błędu", true},
        Portfolio05Milestone{"instrukcja odtworzenia", true},
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

### 1. Executor zadań

- **Poziom:** zaawansowany.
- **Efekt portfolio:** thread pool z anulowaniem i shutdownem.
- **Problem:** Wiele małych prac trzeba wykonać równolegle bez nieograniczonej kolejki.
- **Minimalny zakres:** Bounded queue, futures, stop token, drenaż i metryki opóźnienia.
- **Wymagane działy:** 10, 17–20, 23, 27.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 2. Mini runtime aktorów

- **Poziom:** ekspercki.
- **Efekt portfolio:** ownership wiadomości i izolacja stanu.
- **Problem:** Współdzielony stan powoduje trudne do reprodukcji wyścigi.
- **Minimalny zakres:** Mailbox, actor id, dispatch, supervision podstawowy i kontrolowane zakończenie.
- **Wymagane działy:** 10, 17–20, 23, 27.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 3. Współbieżny cache

- **Poziom:** ekspercki.
- **Efekt portfolio:** porównanie blokad, sharding i kosztów.
- **Problem:** Gorący cache musi ograniczyć contention i zachować poprawność wygaśnięcia.
- **Minimalny zakres:** TTL, shard locks, limit rozmiaru, statystyki i benchmark z różnymi proporcjami.
- **Wymagane działy:** 10, 17–20, 23, 27.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 4. Kolektor śladów

- **Poziom:** ekspercki.
- **Efekt portfolio:** batching, sampling i bounded memory.
- **Problem:** Duża liczba spanów nie może zagłodzić monitorowanej aplikacji.
- **Minimalny zakres:** API ingest, kolejka, batch exporter, sampling, drop counter i shutdown.
- **Wymagane działy:** 10, 17–20, 23, 27.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 5. Silnik potoków danych

- **Poziom:** ekspercki.
- **Efekt portfolio:** backpressure przez wieloetapowy pipeline.
- **Problem:** Etapy o różnej szybkości tworzą kolejki i trudne warunki anulowania.
- **Minimalny zakres:** Źródło, transformacje, bounded channels, sink, błędy i metryki per etap.
- **Wymagane działy:** 10, 17–20, 23, 27.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.


## Porównanie i decyzje

Projekt średni ma pokazać poprawny model C++, testy i ergonomię użytkownika. Projekt zaawansowany powinien dodatkowo mieć granice adapterów, kontrolowane błędy i pomiar. Projekt ekspercki łączy awarie częściowe, operacyjność oraz proces wydania. Rozszerzenie nie podnosi automatycznie poziomu; wartość rośnie dopiero wtedy, gdy nowy zakres ma kontrakt i dowód.

Nie zaczynaj równocześnie pięciu propozycji. Ukończ jedną, opublikuj release i wykonaj retrospektywę. Drugi projekt wybierz tak, aby pokazywał inne ryzyko: po narzędziu CLI może to być sieć i baza, po usłudze — runtime lub parser. W ten sposób portfolio pokazuje szerokość bez sześciu wariantów tej samej aplikacji CRUD.

## Powiązane tematy

- [Mapa projektów](README.md)
- [Proces realizacji projektu](ZESTAW-CWICZEN.md)
- [Główna mapa portfolio](../Projekty.md)
