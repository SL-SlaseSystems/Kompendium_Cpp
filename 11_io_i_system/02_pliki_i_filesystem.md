[← Spis treści](../README.md)

# Pliki i filesystem

`std::ifstream`, `std::ofstream` i `std::fstream` zarządzają uchwytem pliku przez RAII. Tryb otwarcia określa odczyt, zapis, dopisywanie, truncation i binarność. Destruktor zamyka plik, ale błąd końcowego zapisu może wymagać jawnego `flush` lub `close` i sprawdzenia stanu przed destrukcją.

~~~cpp
#include <cassert>
#include <filesystem>
#include <fstream>
#include <string>

int main() {
    const auto path = std::filesystem::temp_directory_path() / "cpp_compendium.txt";
    {
        std::ofstream output{path};
        output << "C++23\n";
        assert(output.good());
    }
    {
        std::ifstream input{path};
        std::string line;
        std::getline(input, line);
        assert(line == "C++23");
    }
    std::filesystem::remove(path);
}
~~~

Walidator kompendium jedynie kompiluje ten blok, więc nie tworzy pliku. W prawdziwym teście nazwa pliku musi być unikalna, cleanup odporny na wyjątki, a środowisko może ograniczać zapis.

`std::filesystem::path` reprezentuje ścieżkę zgodnie z platformą. Operator `/` łączy komponenty bez ręcznego separatora. Funkcje mają wariant rzucający `filesystem_error` oraz overload z `std::error_code`, co pozwala wybrać model błędów. Symlinki, uprawnienia, race między sprawdzeniem a użyciem i różnice kodowania wymagają uwagi.

Odczyt całego pliku do pamięci jest prosty, ale nieodpowiedni dla niezaufanego rozmiaru. Przetwarzaj strumieniowo lub ustaw limit. Atomiczna zamiana pliku często polega na zapisie do pliku tymczasowego, flush/sync zgodnym z wymaganiami i rename, lecz gwarancje trwałości są zależne od systemu plików.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Pliki i filesystem”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz normalizację wejścia, wykonanie operacji systemowej lub bibliotecznej, sprawdzenie wyniku i zamknięcie zasobu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel format danych od obiektu domenowego, czas monotoniczny od kalendarzowego oraz API standardowe od zależności platformowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź kod błędu, liczbę przetworzonych bajtów, stan strumienia, jednostkę pomiaru i wynik dla przerwanej operacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: I/O przekracza granicę procesu i dlatego jest częściowe, opóźnione oraz zależne od reprezentacji. Każda operacja potrzebuje modelu błędów, limitu danych, kodowania lub jednostki oraz zasad własności uchwytu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Ścieżka jest wartością składniową zależną od platformy, a istnienie celu może zmienić się między sprawdzeniem i użyciem. Operację należy wykonać i obsłużyć jej rzeczywisty `error_code` lub wyjątek zamiast ufać wcześniejszemu testowi.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Pliki i filesystem” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Pliki i filesystem
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Pliki i filesystem”, oceniaj jawne kodowanie, kontrolowane limity, odporność na częściowy odczyt, bezpieczne ścieżki i deterministyczne sprzątanie. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Strumienie](01_strumienie_i_formatowanie.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Kody błędów](../07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

