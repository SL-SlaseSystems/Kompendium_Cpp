[← Spis treści](../README.md)

# Pierwszy program

Wykonanie programu C++ rozpoczyna się w funkcji `main`. Najprostsza poprawna postać zwraca `int`; dojście do jej końca jest równoważne `return 0`. Argumenty wiersza poleceń są dostępne przez `argc` i `argv`, ale nie trzeba ich deklarować, jeśli program ich nie używa.

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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Pierwszy program”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz przejście od tekstu źródłowego przez analizę składniową i semantyczną do artefaktu wykonywalnego. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie standardu od rozszerzenia kompilatora, ustawienia toolchainu i zachowania platformy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź pełne polecenie kompilacji, wersje narzędzi, diagnostykę oraz wynik uruchomienia w kontrolowanym środowisku. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Program C++ powstaje w łańcuchu źródło–kompilator–linker–środowisko wykonawcze. Standard opisuje zachowanie programu abstrakcyjnego, implementacja wybiera reprezentację i ABI, a system operacyjny dostarcza proces, pliki oraz biblioteki. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Funkcja `main` jest punktem wejścia programu hostowanego, a jej zakończenie zwraca status środowisku. Nagłówki udostępniają deklaracje; samo dołączenie nagłówka nie kopiuje gotowej biblioteki do programu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Pierwszy program” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Pierwszy program
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Pierwszy program”, oceniaj przenośność, powtarzalność budowania, jakość diagnostyki i jawne wymagania wersji standardu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Czytaj pierwszy komunikat diagnostyczny, nie tylko ostatnią lawinę błędów. Kompiluj z wysokim poziomem ostrzeżeń i nie ignoruj ich bez rozumienia przyczyny. Zwracaj sensowny kod wyjścia z narzędzi CLI, błędy kieruj do `std::cerr`, a zasoby reprezentuj obiektami, których destruktory zapewniają sprzątanie.

## Powiązane tematy

- [Typy podstawowe i literały](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Strumienie i formatowanie](../11_io_i_system/01_strumienie_i_formatowanie.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)

