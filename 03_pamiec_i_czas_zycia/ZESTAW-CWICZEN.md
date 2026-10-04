[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — pamięć i czas życia

Przy każdym zadaniu nazwij właściciela i niewłaścicielskie obserwatory. Jeśli używasz sanitizera, opisz również regułę języka, którą narusza błędny wariant.

## Poziom 1 — model lifetime

1. Oznacz storage duration wszystkich obiektów w programie z globalem, lokalną zmienną i `static`.
2. Narysuj kolejność konstrukcji oraz destrukcji obiektów w dwóch zagnieżdżonych zakresach.
3. Wyjaśnij różnicę między pamięcią przydzieloną a rozpoczętym lifetime obiektu.
4. Znajdź referencję do zniszczonego obiektu lokalnego.
5. Sprawdź zachowanie pustego `std::span` bez dereferencji.

## Poziom 2 — RAII

6. Zastąp parę ręcznych operacji acquire/release klasą RAII.
7. Dodaj wyjątek między pozyskaniem a użyciem zasobu i wykaż poprawne sprzątanie.
8. Zaimplementuj scope guard dla prostej operacji rollback albo użyj dostępnego odpowiednika.
9. Zarządzaj uchwytem pliku przez typ z niestandardowym deleterem.
10. Porównaj destrukcję deterministyczną z ręcznym blokiem cleanup.

## Poziom 3 — copy i move

11. Zaobserwuj liczbę kopii oraz przeniesień typu śledzącego operacje specjalne.
12. Usuń ręczne operacje specjalne z klasy korzystającej wyłącznie z typów wartościowych.
13. Zaimplementuj typ move-only zarządzający prostym uchwytem.
14. Zdefiniuj poprawny, łatwy do zniszczenia stan obiektu po przeniesieniu.
15. Wyjaśnij, kiedy `std::move` nie wykonuje żadnego przeniesienia.

## Poziom 4 — smart pointery

16. Przepisz drzewo z wyłącznym ownership na `std::unique_ptr`.
17. Znajdź cykl `shared_ptr` i przerwij go przez `weak_ptr`.
18. Porównaj fabrykę zwracającą wartość z fabryką zwracającą `unique_ptr`.
19. Dodaj niestandardowy deleter dla zasobu z API C.
20. Uzasadnij, dlaczego przekazanie `shared_ptr` przez wartość komunikuje inną intencję niż `const T&`.

## Poziom 5 — widoki i diagnostyka

21. Znajdź `string_view` wskazujący na tymczasowy `std::string`.
22. Zmień API tak, aby lifetime bufora był widoczny w kontrakcie.
23. Przetestuj kod z AddressSanitizerem dla use-after-free i opisz raport.
24. Sprawdź invalidację widoku po realokacji `std::vector`.
25. Zaprojektuj zestaw testów dla funkcji przechowującej niewłaścicielski callback.

## Zadanie końcowe

Zaprojektuj bufor wiadomości z jednoznacznym ownership, możliwością przenoszenia i bezpiecznym widokiem do odczytu. Dodaj testy konstrukcji, przeniesienia, pustego bufora, realokacji oraz wyjątku podczas przygotowania danych. Odbiór wymaga rule of zero albo jawnego uzasadnienia każdej funkcji specjalnej oraz czystego przebiegu AddressSanitizera.
