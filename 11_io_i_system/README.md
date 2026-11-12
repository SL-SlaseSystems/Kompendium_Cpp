[← Główny spis treści](../README.md)

# 11. I/O i system

Operacje wejścia/wyjścia łączą kod C++ z danymi oraz zasobami zewnętrznymi. Dział obejmuje strumienie, pliki, ścieżki, czas, losowość i numerykę, a także jasno wyznacza granice biblioteki standardowej w sieci i serializacji.

## Wymagania wstępne

Potrzebujesz RAII, obsługi błędów, biblioteki standardowej, podstaw współbieżności i świadomości zależności platformowych.

## Efekty uczenia się

- kontrolujesz stan strumienia i formatowanie;
- pracujesz ze ścieżkami przez `filesystem` bez ręcznego składania separatorów;
- rozróżniasz zegary, duration i punkty czasu;
- używasz generatorów losowych oraz właściwych rozkładów;
- rozumiesz granice standardowego C++23 dla sieci i serializacji.

## Kolejność rozdziałów

1. [Strumienie i formatowanie](01_strumienie_i_formatowanie.md)
2. [Pliki i filesystem](02_pliki_i_filesystem.md)
3. [chrono i czas](03_chrono_i_czas.md)
4. [random i numeryka](04_random_i_numeryka.md)
5. [Sieć, serializacja i granice std](05_siec_serializacja_i_granice_std.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Bezpieczna praca

Ćwiczenia plikowe wykonuj wyłącznie w katalogu tymczasowym utworzonym dla testu. Nie używaj ścieżek domowych ani ważnych danych. Operacje sieciowe otrzymują timeout i nie są wymagane do podstawowej walidacji repozytorium.

## Pułapki

- ignorowanie bitów stanu strumienia;
- założenie atomowości zwykłego zapisu pliku;
- użycie zegara systemowego do pomiaru czasu trwania;
- modulo zamiast rozkładu losowego;
- nazywanie biblioteki zewnętrznej częścią standardowego C++.

## Samoocena

Potrafisz bezpiecznie zapisać i odczytać dane, obsłużyć błąd bez pozostawienia częściowego stanu, dobrać zegar i rozkład oraz wskazać, które elementy rozwiązania są przenośne, platformowe lub zewnętrzne.

## Co dalej

Przejdź do [współczesnego C++](../12_wspolczesny_cpp/README.md), aby uporządkować pochodzenie używanych mechanizmów i ich dostępność w toolchainie.

## Pogłębienie dla osoby programującej w C++

Przed ponowną lekturą rozwiąż scenariusze i uzasadnij odpowiedzi regułą języka lub kontraktem. Wynik eksperymentu porównuj z przewidywaniem; kompilacja nie jest dowodem poprawności wykonania.

[Sześć zadań z rozwiązaniami](../cwiczenia/11_io_i_system.md) uzupełnia dotychczasowy [zestaw ćwiczeń](ZESTAW-CWICZEN.md). Pełną kolejność pogłębiania opisuje [ścieżka nauki](../sciezka_nauki.md).
