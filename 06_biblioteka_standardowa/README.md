[← Główny spis treści](../README.md)

# 06. Biblioteka standardowa

Biblioteka standardowa dostarcza typy wartościowe, kontenery i algorytmy budujące wspólny język współczesnego C++. Celem działu jest dobór abstrakcji na podstawie własności, kosztu oraz invalidacji, a nie zapamiętanie wszystkich metod.

## Wymagania wstępne

Potrzebujesz podstaw lifetime, copy/move, klas i szablonów. Szczególnie ważne jest rozumienie referencji i niewłaścicielskich widoków.

## Efekty uczenia się

- dobierasz reprezentację tekstu i świadomie używasz `string_view`;
- wybierasz kontener na podstawie dostępu, stabilności i kosztu modyfikacji;
- rozumiesz własności kontenerów uporządkowanych i haszowanych;
- śledzisz invalidację iteratorów, referencji i wskaźników;
- składasz algorytmy, lambdy, ranges i views;
- modelujesz złożone wyniki przez `pair`, `tuple`, `variant` i `any` tylko wtedy, gdy poprawiają kontrakt.

## Kolejność rozdziałów

1. [string, string_view i tekst](01_string_string_view_i_tekst.md)
2. [vector, array, deque i list](02_vector_array_deque_list.md)
3. [map, set, unordered i hash](03_map_set_unordered_i_hash.md)
4. [Iteratory i invalidacja](04_iteratory_i_invalidacja.md)
5. [Algorytmy i lambdy](05_algorytmy_i_lambdy.md)
6. [Ranges i views](06_ranges_i_views.md)
7. [tuple, pair, variant i any](07_tuple_pair_variant_any.md)
8. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Sposób pracy

Dla każdej operacji zapisuj oczekiwaną złożoność i elementy, które mogą zostać unieważnione. Porównuj rozwiązanie ręczną pętlą z algorytmem nazwanym. Widoki testuj razem z lifetime danych źródłowych.

## Pułapki

- wybieranie `list` na podstawie samej złożoności asymptotycznej;
- używanie unieważnionego iteratora po realokacji;
- przechowywanie `string_view` do krótkotrwałego tekstu;
- słaby hash albo naruszenie zgodności hash/equality;
- pipeline ranges zwracający widok do zniszczonego źródła.

## Samoocena

Potrafisz uzasadnić kontener i algorytm dla rzeczywistego wzorca dostępu, wskazać wszystkie zależności lifetime, oszacować koszt oraz napisać testy dla pustego wejścia, duplikatów i invalidacji.

## Co dalej

Przejdź do rozdziału [Wyjątki: try, catch i throw](../07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md), aby zacząć opisywać niepowodzenia operacji na typach i kontenerach bez utraty inwariantów.
