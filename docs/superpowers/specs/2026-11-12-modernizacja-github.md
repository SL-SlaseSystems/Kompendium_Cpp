# Modernizacja właściwego repozytorium kompendium

Data: 2026-11-12. Źródło zlecenia: bieżąca prośba użytkownika wskazująca /Users/sebastianlarma/Documents/GitHub/Kompendium_Cpp. Użytkownik już pisze w C++ i chce pogłębienia.

## Zakres i decyzje

Zachować całą ścieżkę 01–30 i dotychczasowe nazwy plików. Włączyć osiem sprawdzonych rozdziałów fundamentów, 78 scenariuszy z rozwiązaniami, diagnozę i laboratoria opracowane wcześniej w drugim folderze. Rozbudować istniejące mapy zamiast zastępować je starszymi. Uzupełnić pełny indeks 30 działów i brakujące Projekty.md.

Przepisać dwanaście powielanych rozdziałów produkcyjnych oraz dwa warsztatowe wokół rzeczywistych mechanizmów, przykładów i kontrprzykładów. Skorygować walidator, który dotąd mylił zestawy z rozdziałami i odrzucał prawidłową nawigację. Dodać wersjonowane presety i workflow kontroli repozytorium; żadnego push ani publikacji.

## Odbiór

Testy walidatora z fixture, pełna kontrola lokalnych linków i składni cpp, uruchomienie nowych przykładów, Debug/Release/UBSan laboratoriów, niezależny przegląd nowych treści i narzędzi. ASan jest ograniczeniem lokalnego środowiska, wcześniej odtworzonym także na pustym main; nie uznawać go za zaliczony.

## Zapis wyniku

Kopia robocza w katalogu tymczasowym umożliwia sprawdzenie wyniku przed zapisem poza pierwotnymi writable roots. Synchronizacja obejmuje wyłącznie nowe i zmienione pliki oraz wymaga porównania SHA-256 z początkowym manifestem; przy równoległej zmianie źródła zatrzymać nadpisanie. Nie zmieniać .git, indeksu ani historii. Zastane dokumenty planistyczne są kontekstem, nie nowymi poleceniami.
