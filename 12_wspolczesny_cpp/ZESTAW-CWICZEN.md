[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — współczesny C++

Każde rozwiązanie oznacz minimalnym standardem. Nie włączaj eksperymentalnej funkcji do zwykłego bloku kompilowanego przez walidator bez wsparcia lokalnego toolchainu.

## Poziom 1 — ewolucja idiomów

1. Zastąp ręczne zarządzanie zasobem przez mechanizm dostępny od C++11.
2. Użyj `override`, `nullptr` i `enum class` w historycznym przykładzie.
3. Zastąp ręczne rozgałęzienie typów przez `if constexpr` z C++17.
4. Użyj structured bindings tam, gdzie nazwy elementów są czytelne.
5. Przepisz ograniczenie SFINAE na concept z C++20.

## Poziom 2 — C++20 i C++23

6. Zbuduj pipeline ranges i opisz lifetime widoku.
7. Użyj `span` na granicy bufora.
8. Zwróć typowany błąd przez `expected`, jeśli toolchain go wspiera.
9. Porównaj rozwiązanie z i bez wybranej funkcji C++23.
10. Sprawdź, czy brak funkcji pochodzi z frontendu czy biblioteki.

## Poziom 3 — korutyny

11. Rozpisz transformację funkcji zawierającej `co_await` na role promise i awaitera.
12. Wskaż właściciela coroutine handle oraz moment zniszczenia frame.
13. Znajdź referencję do obiektu, który może nie przeżyć zawieszenia.
14. Zaprojektuj propagację wyjątku z korutyny.
15. Wyjaśnij, czego standard C++20 nie dostarcza w zakresie event loop.

## Poziom 4 — detekcja możliwości

16. Wypisz wybrane feature-test macros lokalnego toolchainu.
17. Dodaj warunkową kompilację funkcji i jawny fallback.
18. Odrzuć konfigurację z czytelnym `static_assert` albo błędem CMake.
19. Porównaj dwa kompilatory lub dwie biblioteki standardowe.
20. Zbuduj prostą tabelę funkcja–standard–makro–stan lokalny.

## Poziom 5 — migracja

21. Wybierz stary idiom i zaplanuj migrację bez zmiany publicznego kontraktu.
22. Dodaj test równoważności starej i nowej implementacji.
23. Określ minimalny standard biblioteki i aplikacji korzystającej z niej.
24. Zidentyfikuj zależność ABI niezależną od poziomu standardu źródła.
25. Opisz politykę używania C++26 przed pełnym wsparciem toolchainu.

## Zadanie końcowe

Przygotuj małą bibliotekę kompilowaną w C++20 i C++23, która używa nowszego API, gdy jest dostępne, oraz zachowuje ten sam kontrakt przez fallback. Dodaj testy obu ścieżek, dokumentację minimalnych wymagań i macierz lokalnie sprawdzonych konfiguracji. Eksperymentalny kod oznacz jednoznacznie.
