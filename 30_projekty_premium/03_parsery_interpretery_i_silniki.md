[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Parsery, interpretery i silniki

Kolekcja zawiera pięć projektów, które dają się pokazać jako działający artefakt, testy i zapis decyzji. Minimalny zakres jest celowo mniejszy od pełnego produktu: najpierw zamknij pionowy przepływ, potem rozszerzaj go na podstawie pomiaru oraz ryzyka. Wymagane działy są mapą powrotu do teorii, a nie listą technologii do użycia za wszelką cenę.

~~~cpp
#include <array>
#include <cassert>
#include <string_view>

struct Portfolio03Milestone { std::string_view name; bool verified; };

constexpr bool releasable(std::array<Portfolio03Milestone, 3> plan) {
    for (const auto& item : plan) if (!item.verified) return false;
    return true;
}

int main() {
    constexpr std::array plan{
        Portfolio03Milestone{"działający pion", true},
        Portfolio03Milestone{"test błędu", true},
        Portfolio03Milestone{"instrukcja odtworzenia", true},
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

### 1. Parser konfiguracji

- **Poziom:** średni.
- **Efekt portfolio:** diagnostyka z pozycją i bezpieczne limity.
- **Problem:** Nieufny tekst trzeba zamienić na typowany model z czytelnymi błędami.
- **Minimalny zakres:** Lexer, parser recursive descent, AST, lokalizacja błędu i limit głębokości.
- **Wymagane działy:** 05–07, 12, 15, 18, 20, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 2. Interpreter wyrażeń

- **Poziom:** zaawansowany.
- **Efekt portfolio:** mały język z testami semantyki.
- **Problem:** Użytkownik potrzebuje obliczeń bez kompilowania ani uruchamiania obcego kodu.
- **Minimalny zakres:** Liczby, zmienne, operatory, funkcje z allowlisty i budżet kroków.
- **Wymagane działy:** 05–07, 12, 15, 18, 20, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 3. Silnik szablonów

- **Poziom:** zaawansowany.
- **Efekt portfolio:** escaping, streaming i rozdzielenie faz.
- **Problem:** Tekst z placeholderami ma być generowany bez przypadkowego wstrzyknięcia składni wyjścia.
- **Minimalny zakres:** Parser szablonu, typowany kontekst, escaping HTML i render do strumienia.
- **Wymagane działy:** 05–07, 12, 15, 18, 20, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 4. Język zapytań do logów

- **Poziom:** ekspercki.
- **Efekt portfolio:** DSL łączący parser, plan i wykonanie.
- **Problem:** Filtry tekstowe stają się nieczytelne i trudne do optymalizacji.
- **Minimalny zakres:** Gramatyka filtrów, AST, walidacja pól, plan predykatów i limity.
- **Wymagane działy:** 05–07, 12, 15, 18, 20, 29.
- **Kryteria jakości:** Formatowanie, analiza statyczna, brak sekretów, udokumentowany build od świeżego klonu i ostrzeżenia traktowane jako błędy we własnym kodzie.
- **Testy:** Testy jednostkowe domeny, przypadki graniczne, test kontraktu adaptera oraz scenariusz awarii z deterministycznym czasem i danymi.
- **Ryzyka:** Nieograniczone wejście, niejasny ownership, częściowe wykonanie i zbyt szeroki zakres pierwszej iteracji; każde ryzyko ma limit albo prototyp redukujący niewiedzę.
- **Rozszerzenia:** Dodaj pomiar wydajności, drugi adapter, pakiet instalacyjny i pipeline publikujący wersjonowany artefakt.

### 5. Maszyna wirtualna bytecode

- **Poziom:** ekspercki.
- **Efekt portfolio:** runtime z jawnym modelem błędów i benchmarkiem.
- **Problem:** AST interpreter jest zbyt wolny, ale semantyka musi pozostać identyczna.
- **Minimalny zakres:** Kompilacja AST do bytecode, stos, instrukcje, budżet i porównanie wyników.
- **Wymagane działy:** 05–07, 12, 15, 18, 20, 29.
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
