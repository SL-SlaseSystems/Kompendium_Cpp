[← Spis treści](../README.md)

# Kompilatory i toolchain

Typowy toolchain C++ składa się z kompilatora, implementacji biblioteki standardowej, linkera, debuggera i systemu budowania. Na Linuksie najczęściej spotyka się GCC lub Clang, na Windows MSVC, Clang-cl albo MinGW, a na macOS Apple Clang. Wybór kompilatora nie powinien być ukrytym założeniem biblioteki, jeśli projekt deklaruje przenośność.

Minimalna kompilacja pojedynczej jednostki translacji wygląda następująco:

~~~text
clang++ -std=c++23 -Wall -Wextra -Wpedantic main.cpp -o app
./app
~~~

`-std=c++23` wybiera dialekt, `-Wall -Wextra -Wpedantic` włącza wartościowy zestaw ostrzeżeń, a `-o` nadaje nazwę wynikowi. Ostrzeżenia są częścią procesu jakości, ale nie zastępują analizy statycznej ani sanitizerów. W projekcie MSVC analogiczne intencje wyrażają między innymi `/std:c++latest`, `/W4` i `/permissive-`.

~~~cpp
#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Użycie: program NAZWA\n";
        return EXIT_FAILURE;
    }
    std::cout << "Witaj, " << argv[1] << "!\n";
    return EXIT_SUCCESS;
}
~~~

Debug build powinien zachowywać symbole i ułatwiać diagnostykę, na przykład `-g -O0` lub `-Og`. Release build włącza optymalizację, zwykle `-O2` albo `-O3`, ale dokładny profil należy kontrolować w systemie budowania. Sanitizery dodaje się do kompilacji i linkowania, np. `-fsanitize=address,undefined`.

## Dobra konfiguracja

W CI warto kompilować co najmniej Clangiem i GCC, a kod przenośny na Windows również MSVC. Ustal wersję minimalną kompilatora, standard języka i politykę ostrzeżeń. Nie wpisuj globalnych flag platformowych w kodzie; konfiguruj je per target w CMake. Narzędzia `clang-format`, `clang-tidy`, `lldb` i `gdb` rozwiązują inne problemy i powinny mieć osobne kroki w pipeline.

## Jak to działa krok po kroku

Wywołanie `clang++` jest zwykle uruchomieniem sterownika, który dobiera kolejne narzędzia oraz domyślne biblioteki. Najpierw znajdź rzeczywisty plik wykonywalny i odczytaj jego wersję. Następnie zanotuj target: architekturę i system, dla których powstaje kod. Program uruchomiony na ARM może budować kod x86, jeżeli ma odpowiedni zestaw narzędzi i sysroot. To kompilacja krzyżowa, a nie automatyczna zdolność każdego pliku binarnego do pracy na obu procesorach.

Włącz ostrzeżenia, kompiluj minimalny przykład i uruchom go. Dopiero potem dołącz bibliotekę zewnętrzną. Przy błędzie sprawdź pełne polecenie kompilacji: katalogi `-I`, definicje `-D`, standard, sysroot i ścieżki bibliotek. Plik `compile_commands.json` pozwala narzędziom analizy używać takich samych parametrów jak właściwy build. Analiza nagłówka w przypadkowej konfiguracji może produkować błędy, których nie ma w projekcie.

## Pogłębienie mechanizmu

Frontend parsuje C++ i sprawdza semantykę; optimizer przekształca reprezentację pośrednią; backend generuje kod dla procesora. Biblioteka standardowa dostarcza część kodu w nagłówkach, a część w bibliotekach binarnych. Linker rozwiązuje odwołania między jednostkami. Debugger korzysta z informacji o nazwach, typach i lokalizacjach źródła. Jeden komunikat „build failed” może zatem oznaczać problemy na bardzo różnych poziomach.

`-Wall` nie znaczy „wszystkie ostrzeżenia”. Zestawy są zależne od kompilatora i wersji. `-Werror` zamienia ostrzeżenia w błędy, co bywa przydatne dla własnego kodu w ustalonym CI, ale może utrudnić aktualizację kompilatora lub budowanie cudzych nagłówków. Traktuj ostrzeżenia z własnego kodu świadomie i ograniczaj wyciszenia do konkretnej przyczyny.

Optymalizacja zmienia widoczność zmiennych w debuggerze. Obiekt może zostać usunięty, zmienna istnieć tylko w rejestrze, a funkcja zostać wstawiona do wywołującego. Brak możliwości obejrzenia zmiennej nie dowodzi błędu kompilatora. Symbole debugowania i optymalizacja są osobnymi ustawieniami: da się budować zoptymalizowany program z symbolami, co jest przydatne do profilowania rzeczywistych kosztów.

## Drugi przykład

Poniższe polecenia dotyczą Clang/GCC w środowisku z dostępnym runtime sanitizerów; użyj pliku `main.cpp` z przykładu powyżej.

~~~text
clang++ --version
clang++ -std=c++23 -Wall -Wextra -Wpedantic -g -O0 main.cpp -o app-debug
./app-debug Ada
clang++ -std=c++23 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer main.cpp -o app-sanitized
./app-sanitized Ada
clang++ -std=c++23 -O2 -g main.cpp -o app-release
./app-release Ada
~~~

W jednym poleceniu kompilującym i linkującym flaga sanitizera trafia do obu etapów. Przy oddzielnym `-c` i linkowaniu trzeba zachować ją także w końcowym kroku. Program bez argumentu powinien zakończyć się niepowodzeniem, a z `Ada` wypisać powitanie. Porównujesz zachowanie wariantów, nie czas jednego krótkiego wypisania tekstu.

## Porównanie i decyzje

Dobieraj konfigurację do pytania. Do śledzenia instrukcji wybierz build łatwy do debugowania. Do wykrywania naruszeń pamięci użyj ASan i UBSan. Do oceny szybkości uruchom zoptymalizowany program bez instrumentacji, z reprezentatywnymi danymi. Czas zmierzony w sanitizerze opisuje także koszt instrumentacji, więc nie stanowi pomiaru docelowej wersji.

Osobny katalog budowania dla każdej konfiguracji zapobiega mieszaniu obiektów z różnych ustawień. Zapisuj wersje narzędzi, zamiast polegać na tym, co akurat znajduje się pierwsze w `PATH`. Wersjonowana konfiguracja budowania pozwala odtworzyć problem innej osobie bez odgadywania lokalnych ustawień IDE.

## Ćwiczenie z odpowiedzią

Kompilacja z `-fsyntax-only` przechodzi, ale pełny build zgłasza brak symbolu. W jakiej warstwie szukać? Przede wszystkim w definicjach i linkowaniu: sprawdź, czy odpowiedni plik obiektowy lub biblioteka rzeczywiście bierze udział w końcowym poleceniu. Dodawanie kolejnych `#include` nie dostarcza brakującej binarnej definicji zwykłej funkcji.

Dokumentacja poleceń i zakresu flag: [Clang Compiler User’s Manual](https://clang.llvm.org/docs/UsersManual.html). Konkretne flagi są właściwością toolchainu, nie składnią ISO C++.

## Powiązane tematy

- [Proces budowania](05_proces_budowania.md)
- [Ostrzeżenia i analiza statyczna](../09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md)
- [CMake](../08_budowanie_i_organizacja/05_cmake.md)

