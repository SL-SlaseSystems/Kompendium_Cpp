[← Główny spis treści](../README.md)

# 14. Warsztat profesjonalisty

Ten dział zamienia pojedyncze polecenia w powtarzalny lokalny przepływ pracy. Formatowanie usuwa jałowe różnice, analiza statyczna wykrywa ryzyko przed uruchomieniem programu, presety CMake opisują wspólną konfigurację, a dokumentacja i Git utrwalają decyzje zespołu. Ostatni krok łączy te narzędzia w szybkie kontrole przed wysłaniem zmiany.

## Wymagania wstępne

Przydadzą się podstawy kompilacji z [działu 08](../08_budowanie_i_organizacja/README.md) oraz testowania z [działu 09](../09_testowanie_i_jakosc/README.md). Przykłady zakładają projekt C++23 zarządzany w Git, ale opisane granice można przenieść do innych standardów i systemów budowania.

## Efekty uczenia się

- rozdzielasz styl kodu, analizę semantyczną i kompilację;
- wersjonujesz konfigurację, a lokalne szczegóły pozostawiasz użytkownikowi;
- uruchamiasz ten sam preset CMake ręcznie i w automatyzacji;
- dokumentujesz publiczny kontrakt bez przepisywania implementacji;
- tworzysz małe, odwracalne commity i czytelne przeglądy;
- budujesz szybki zestaw kontroli uruchamiany przed wysłaniem zmian.

## Kolejność rozdziałów

1. [Formatowanie: clang-format i EditorConfig](01_formatowanie_clang_format_editorconfig.md)
2. [Analiza statyczna: clang-tidy i Cppcheck](02_analiza_statyczna_clang_tidy_cppcheck.md)
3. [CMake Presets i Ninja](03_cmake_presets_i_ninja.md)
4. [Dokumentacja: Doxygen i diagramy](04_dokumentacja_doxygen_i_diagramy.md)
5. [Git i praca z repozytorium](05_git_i_praca_z_repozytorium.md)
6. [Automatyzacja lokalna i pre-commit](06_automatyzacja_lokalna_i_pre_commit.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Przechodź przez dział na małym repozytorium ćwiczeniowym. Po każdej zmianie uruchom narzędzie ręcznie, zapisz konfigurację w repozytorium i sprawdź zachowanie od czystego klonu. Nie kopiuj rozbudowanego pliku konfiguracyjnego bez zrozumienia: włącz kilka reguł, zobacz ich efekt i dopiero rozszerzaj politykę.

## Kryterium ukończenia

Potrafisz pobrać świeży klon projektu, skonfigurować go presetem, zbudować przez Ninja, uruchomić testy, analizę i kontrolę formatowania jednym udokumentowanym poleceniem. Wiesz też, które pliki są wspólną polityką projektu, a które pozostają lokalną konfiguracją programisty.

## Co dalej

Narzędzia z tego działu wrócą jako bramki jakości w późniejszym dziale o CI/CD. Zanim automatyzacja otrzyma dostęp do sekretów i publikacji, przejdź także przez kolejny dział o bezpiecznym C++.
