[← Spis treści](../README.md)

# Pliki i filesystem

`std::ifstream`, `std::ofstream` i `std::fstream` zarządzają uchwytem pliku przez RAII. Tryb otwarcia określa odczyt, zapis, dopisywanie, truncation i binarność. Destruktor zamyka plik, ale błąd końcowego zapisu może wymagać jawnego `flush` lub `close` i sprawdzenia stanu przed destrukcją.

~~~cpp
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Użycie: program PLIK\n";
        return EXIT_FAILURE;
    }
    const std::filesystem::path path{argv[1]};
    std::ifstream input{path};
    if (!input) {
        std::cerr << "Nie można otworzyć pliku.\n";
        return EXIT_FAILURE;
    }
    std::string first_line;
    if (std::getline(input, first_line)) {
        std::cout << first_line << '\n';
    } else if (!input.eof() || input.bad()) {
        std::cerr << "Błąd odczytu.\n";
        return EXIT_FAILURE;
    }
}
~~~

Program czyta pierwszy wiersz wskazanego pliku i odróżnia nieudane otwarcie od błędu odczytu. Pusty plik traktuje jako poprawne wejście bez wiersza. Przykład nie nadpisuje istniejących plików; do ćwiczeń zapisu używaj osobnego katalogu testowego i jawnie wybranej polityki nadpisania.

`std::filesystem::path` reprezentuje ścieżkę zgodnie z platformą. Operator `/` łączy komponenty bez ręcznego separatora. Funkcje mają wariant rzucający `filesystem_error` oraz overload z `std::error_code`, co pozwala wybrać model błędów. Symlinki, uprawnienia, race między sprawdzeniem a użyciem i różnice kodowania wymagają uwagi.

Odczyt całego pliku do pamięci jest prosty, ale nieodpowiedni dla niezaufanego rozmiaru. Przetwarzaj strumieniowo lub ustaw limit. Atomiczna zamiana pliku często polega na zapisie do pliku tymczasowego, flush/sync zgodnym z wymaganiami i rename, lecz gwarancje trwałości są zależne od systemu plików.

## Jak to działa krok po kroku

Oddziel utworzenie ścieżki od operacji na systemie plików. Złożenie `directory / "report.txt"` jedynie oblicza nazwę; nie tworzy katalogu ani nie sprawdza uprawnień. Konstrukcja strumienia próbuje otworzyć plik. Dopiero odczyt lub zapis wykonuje właściwą pracę, a jego powodzenie trzeba sprawdzać także po udanym otwarciu.

Przy zapisie istotnego wyniku sprawdź stan po operacjach i po jawnym zamknięciu. Nie czekaj na destruktor, aby dopiero wtedy próbować dowiedzieć się o błędzie. RAII zapewnia zwolnienie uchwytu przy wyjściu, ale destruktor nie jest wygodnym kanałem zgłaszania nieudanego zapisu. W API oddziel zatem automatyczne sprzątanie od jawnego zatwierdzenia wyniku.

## Pogłębienie mechanizmu

`app` oznacza dopisywanie na końcu przy zapisach, a `ate` początkowe ustawienie pozycji na końcu po otwarciu. To różne kontrakty: późniejsze przesunięcie pozycji w trybie `ate` może zmienić miejsce zapisu. Zwykły `ofstream` otwiera plik do zapisu z semantyką mogącą usunąć wcześniejszą zawartość. Przed użyciem nazwy dostarczonej przez użytkownika określ, czy nadpisanie jest dozwolone.

`binary` wyłącza platformowe przekształcenia właściwe trybowi tekstowemu; nie zamienia obiektu C++ w przenośny format binarny. Nadal trzeba określić układ pól i kodowanie. W API `read` sprawdzaj również `gcount`, ponieważ końcowy odczyt może zwrócić mniej znaków niż rozmiar bufora. Pętla kopiująca plik musi uwzględnić ten ostatni fragment.

Operacje leksykalne na ścieżce nie rozwiązują symlinków. `lexically_normal` upraszcza zapis komponentów, podczas gdy `canonical` odwołuje się do systemu plików. Nawet ścieżka uznana wcześniej za poprawną może zacząć wskazywać inny obiekt między sprawdzeniem a użyciem. To problem TOCTOU. Ochrona katalogu przed niezaufanymi ścieżkami często wymaga API operującego na uchwytach i reguł specyficznych dla systemu, a nie porównania prefiksu tekstowego.

## Drugi przykład

~~~cpp
#include <cassert>
#include <filesystem>

int main() {
    namespace fs = std::filesystem;
    const fs::path raw = fs::path{"reports"} / "draft" / ".." / "final.txt";
    const auto normalized = raw.lexically_normal();
    assert(normalized == fs::path{"reports"} / "final.txt");
    assert(normalized.filename() == "final.txt");
    assert(normalized.extension() == ".txt");
    const auto renamed = fs::path{normalized}.replace_extension(".csv");
    assert(renamed.filename() == "final.csv");
    assert(normalized.filename() == "final.txt");
}
~~~

Program nie potrzebuje istniejącego katalogu i niczego nie zapisuje. `replace_extension` modyfikuje obiekt ścieżki, na którym zostało wywołane; tutaj jest to kopia. Nie zmienia nazwy rzeczywistego pliku. Takie rozdzielenie pozwala testować logikę nazw bez zależności od uprawnień i zawartości dysku.

## Porównanie i decyzje

Stosuj warianty z `error_code`, gdy niepowodzenie jest oczekiwanym wynikiem przeglądania systemu plików i chcesz jawnie zebrać błędy. Wariant rzucający wyjątek upraszcza przerwanie większej operacji po niepowodzeniu. Nie interpretuj wartości zwrotnej niezależnie od kodu błędu: „nie istnieje” i „nie mogę sprawdzić” mogą wymagać innej reakcji.

Atomowa widoczność nowej wersji pliku i trwałość po utracie zasilania to różne wymagania. `flush` opróżnia bufor warstwy strumienia, ale nie daje uniwersalnej gwarancji zapisu na trwałym nośniku. Schemat plik tymczasowy plus zamiana nazwy wymaga analizy konkretnego systemu plików, granic woluminu i operacji synchronizacji. Samo RAII nie zapewnia transakcji.

## Ćwiczenie z odpowiedzią

Czy `exists(path)` przed otwarciem dowodzi, że otworzysz ten sam plik? Nie: inny proces może go podmienić. Czy normalizacja `a/../b` dowodzi bezpieczeństwa względem dowiązań? Również nie, ponieważ to operacja leksykalna. Dla zwykłego narzędzia raportowego może wystarczyć obsługa błędu otwarcia; dla granicy bezpieczeństwa potrzebny jest silniejszy model dostępu.

Źródło kontraktów operacji: [C++23, filesystem operations](https://timsong-cpp.github.io/cppwp/n4950/fs.op.funcs).

## Powiązane tematy

- [Strumienie](01_strumienie_i_formatowanie.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Kody błędów](../07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

