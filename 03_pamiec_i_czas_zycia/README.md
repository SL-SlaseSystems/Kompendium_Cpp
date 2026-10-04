[← Główny spis treści](../README.md)

# 03. Pamięć i czas życia

C++ pozwala dokładnie kontrolować zasoby, ale wymaga rozróżnienia storage duration, lifetime, ownership oraz samego adresu. Ten dział buduje model, dzięki któremu RAII, przenoszenie, smart pointery i widoki stają się konsekwencją reguł, a nie listą recept.

## Wymagania wstępne

Potrzebujesz znajomości typów, funkcji, referencji, wskaźników i podstawowych kontenerów składniowych z działu 02.

## Efekty uczenia się

- oddzielasz miejsce przechowywania od czasu życia obiektu;
- stosujesz RAII do wszystkich zasobów, nie tylko pamięci;
- rozumiesz copy, move i stan obiektu po przeniesieniu;
- dobierasz `unique_ptr`, `shared_ptr`, `weak_ptr` albo zwykłą wartość;
- rozpoznajesz dangling view i niejawne zależności lifetime.

## Kolejność rozdziałów

1. [Storage duration i lifetime](01_storage_duration_i_lifetime.md)
2. [Stos, sterta i dynamiczna pamięć](02_stos_sterta_i_dynamiczna_pamiec.md)
3. [RAII i destruktory](03_raii_i_destruktory.md)
4. [Copy, move i rule of zero](04_copy_move_i_rule_of_zero.md)
5. [Smart pointery](05_smart_pointery.md)
6. [Widoki, span, string_view i dangling](06_widoki_span_string_view_i_dangling.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Dla każdego przykładu wskaż właściciela zasobu, moment rozpoczęcia i zakończenia lifetime oraz wszystkie obiekty niewłaścicielskie. Używaj AddressSanitizera jako narzędzia pomocniczego, ale najpierw uzasadnij poprawność na podstawie kontraktu.

## Pułapki

- utożsamianie sterty z lifetime, a stosu z bezpieczeństwem;
- ręczne `new`/`delete` w kodzie aplikacyjnym bez klasy zarządzającej;
- tworzenie `shared_ptr` zamiast podjęcia decyzji o ownership;
- widok przeżywający bufor;
- implementowanie destruktora, kopiowania i przenoszenia, gdy wystarcza rule of zero.

## Samoocena

Umiesz przeanalizować ścieżki wyjątków i wczesnych wyjść, wykazać automatyczne zwolnienie zasobów, zaprojektować jednoznaczny ownership oraz wskazać, dlaczego poprawny adres nie zawsze oznacza żywy obiekt.

## Co dalej

Przejdź do [klas i modelu obiektowego](../04_klasy_i_model_obiektowy/README.md). Eksperckie przypadki lifetime i aliasingu znajdują się później w katalogu `zaawansowane`.
