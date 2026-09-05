[← Spis treści](../README.md)

# Pierwszy program

W typowym środowisku hosted funkcja `main` jest punktem wejścia logiki programu C++; inicjalizacja części obiektów statycznych może zachodzić przed jej wywołaniem. Najprostsza poprawna postać zwraca `int`; dojście do jej końca jest równoważne `return 0`. Argumenty wiersza poleceń są dostępne przez `argc` i `argv`, ale nie trzeba ich deklarować, jeśli program ich nie używa.

~~~cpp
#include <iostream>
#include <string>

int main() {
    const std::string language = "C++23";
    std::cout << "Uczę się " << language << '\n';
}
~~~

Dyrektywa `#include <iostream>` jest obsługiwana przez preprocesor i udostępnia deklaracje strumieni. `std::cout` reprezentuje standardowe wyjście, operator `<<` zapisuje kolejne wartości, a znak `\n` kończy wiersz bez wymuszania natychmiastowego opróżnienia bufora. `std::endl` dodatkowo wykonuje flush i dlatego nie powinien być automatycznym zamiennikiem nowej linii.

Przestrzeń nazw `std` zawiera elementy biblioteki standardowej. Zapis `using namespace std;` bywa spotykany w krótkich przykładach, lecz w nagłówkach i większych programach wprowadza ryzyko kolizji nazw. Jawne `std::` jasno pokazuje pochodzenie typu lub funkcji.

## Błędy kompilacji, linkowania i wykonania

Brak średnika albo nieznana nazwa powodują błąd kompilacji. Zadeklarowanie funkcji bez dostarczenia definicji może ujawnić się dopiero podczas linkowania. Dzielenie przez zero, wyjście poza zakres tablicy czy użycie wiszącej referencji może prowadzić do błędu wykonania albo undefined behavior, nawet jeśli program został skompilowany.

## Jak to działa krok po kroku

Zapisz program w pliku tekstowym z rozszerzeniem `.cpp`, a następnie skompiluj go z wybranym standardem. Nagłówki dostarczają deklaracji potrzebnych do sprawdzenia kodu. Kompilator musi rozpoznać typ `std::string` przed utworzeniem zmiennej `language`, a operator wyjścia musi obsługiwać przekazywane wartości. Sama nazwa pliku wykonywalnego nie musi być taka sama jak nazwa źródła.

Po uruchomieniu środowisko przygotowuje proces i wywołuje `main`. Część inicjalizacji obiektów statycznych może odbyć się wcześniej, dlatego `main` nie jest pierwszą możliwą operacją napisaną w C++. W typowym programie hosted jest jednak punktem wejścia logiki aplikacji. Środowiska freestanding, na przykład niektóre systemy wbudowane, mają dodatkowe reguły startu określane przez implementację.

Wewnątrz funkcji inicjalizacja `language` tworzy napis, a wyrażenie ze strumieniem zapisuje tekst. Instrukcje są zakończone średnikami. Nawiasy klamrowe wyznaczają ciało funkcji i zakres lokalnych obiektów. Wyjście z funkcji niszczy lokalny napis, po czym kod zakończenia jest przekazywany środowisku.

## Pogłębienie mechanizmu

`main` ma specjalne reguły: zwraca `int`, a dojście do końca jego ciała oznacza sukces. Nie przenoś tego wyjątku na zwykłą funkcję zwracającą liczbę; ona powinna dostarczyć wynik na odpowiedniej ścieżce. Przenośnym sposobem oznaczenia powodzenia jest `0` lub `EXIT_SUCCESS`, a niepowodzenia `EXIT_FAILURE` z `<cstdlib>`. Znaczenie innych kodów ustala otoczenie programu.

Znak `\n` wewnątrz literału oznacza nową linię. Pojedyncze cudzysłowy tworzą literał znaku, a podwójne literał tablicy znaków. Sam napis `"C++23"` i obiekt `std::string` są różnymi bytami: drugi przechowuje wartość i udostępnia operacje tekstowe. Tę różnicę warto rozumieć przed nauką wskaźników i własności.

Strumień wejściowy nie zgaduje intencji użytkownika. Niepoprawny tekst, koniec danych i błąd urządzenia mogą uniemożliwić odczyt. Sprawdzaj wynik operacji, zanim użyjesz wartości. Inicjalizacja zmiennej na zero daje określony stan początkowy, lecz nie zamienia błędnego wejścia w poprawną liczbę. Oba zagadnienia trzeba obsłużyć osobno.

## Drugi przykład

~~~cpp
#include <cstdlib>
#include <iostream>
#include <string>

int main() {
    std::cout << "Podaj imię: ";
    std::string name;
    if (!std::getline(std::cin, name)) {
        std::cerr << "Nie udało się odczytać wiersza.\n";
        return EXIT_FAILURE;
    }
    if (name.empty()) {
        std::cerr << "Imię nie może być puste.\n";
        return EXIT_FAILURE;
    }
    std::cout << "Witaj, " << name << "!\n";
    return EXIT_SUCCESS;
}
~~~

Program rozróżnia brak odczytu i poprawnie odczytany pusty wiersz. `getline` zachowuje spacje wewnątrz imienia; w przeciwieństwie do `operator>>` dla napisu nie kończy na pierwszej spacji. Zwykłe powiązanie `cin` ze strumieniem `cout` pomaga opróżnić wyjście przed odczytem, więc komunikat może pojawić się bez ręcznego `endl`.

## Porównanie i decyzje

Na początku wybieraj krótkie programy z jednym nowym pojęciem. Jeśli jednocześnie dodasz klasy, pliki i wielowątkowość, komunikat o błędzie będzie trudniej przypisać do przyczyny. Zmieniaj jeden warunek: poprawne imię, pusta linia, a następnie koniec wejścia. W każdym przypadku określ tekst wyjścia oraz kod zakończenia.

Nie rozwiązuj znikającego okna programu przez zależne od systemu `system("pause")`. Uruchom go w terminalu, który już jest otwarty, lub użyj ustawień debuggera. Dzięki temu obsługa wejścia pozostaje częścią zadania programu, a nie sztucznym opóźnieniem zakończenia.

## Ćwiczenie z odpowiedzią

Dlaczego po błędzie odczytu program nie powinien wypisywać zwykłego powitania? Ponieważ nie uzyskał wymaganych danych. Wczesne `return EXIT_FAILURE` kończy tę ścieżkę i nadal niszczy lokalne obiekty. Zastąpienie go wywołaniem `std::exit` zmienia reguły sprzątania lokalnych obiektów, więc nie jest równoważną zmianą stylu.

Reguły punktu wejścia i kończenia programu: [C++23, main function](https://timsong-cpp.github.io/cppwp/n4950/basic.start.main).

## Powiązane tematy

- [Typy podstawowe i literały](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Strumienie i formatowanie](../11_io_i_system/01_strumienie_i_formatowanie.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)

