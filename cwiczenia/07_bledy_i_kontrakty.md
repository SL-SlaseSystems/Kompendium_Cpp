[← Mapa działu](../07_bledy_i_kontrakty/README.md) · [Spis treści](../README.md)

# Ćwiczenia: wynik i stan po błędzie

Każdą operację opisz parą: co komunikuje odbiorcy i w jakim stanie pozostawia program. Wstrzykuj błędy w konkretne miejsca. Zamiast deklarować ogólną „odporność na wyjątki”, nazwij gwarancję i granicę jej obowiązywania.

## 1. Magazyn oraz historia jako jedna transakcja

**Wejście:** operacja zmienia liczbę sztuk w mapie, a następnie dopisuje wpis do wektora historii. Drugie działanie może rzucić przy alokacji. Wymaganie: albo oba efekty, albo żaden. **Oddaj:** projekt silnej gwarancji i dwa punkty wstrzyknięcia błędu. Zakładamy brak zewnętrznego I/O. **Wskazówka:** samo RAII nie wycofuje zmian wartości biznesowych.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Przygotuj nowy spójny stan magazynu i historii w obiekcie roboczym, a zatwierdź wymianą, której niezgłaszanie zostało uzasadnione dla danych typów i allocatorów. Wyjątek przy kopiowaniu stanu lub dopisywaniu historii niszczy jedynie stan roboczy. To kosztowniejsze od precyzyjnego dziennika cofania, lecz łatwe do udowodnienia. [Gwarancje](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md).

</details>

## 2. Zamknięcie pliku może zawieść

**Wejście:** klasa pliku ma destruktor zamykający uchwyt; błąd zapisu może ujawnić się dopiero przy zamknięciu. Klient chce wiedzieć, czy dane zapisano. **Oddaj:** interfejs jawnego zakończenia i politykę destruktora. Rozważ wcześniejszy wyjątek podczas przetwarzania. **Wskazówka:** destruktor nie jest dobrym jedynym kanałem dostarczania informacji o zapisie.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dodaj jawne `finish` lub `close` zwracające wynik operacji albo zgłaszające wyjątek w kontrolowanym miejscu. Destruktor wykonuje sprzątanie bez propagowania wyjątku, także podczas odwijania stosu. Nie deklaruj sukcesu zapisu tylko dlatego, że obiekt zniknął. Ustal stan po nieudanym zamknięciu oraz zakaz podwójnego zamknięcia tego samego uchwytu. [RAII i noexcept](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md).

</details>

## 3. Brak pola i błędne pole

**Wejście:** konfiguracja może nie zawierać portu; obecna wartość może mieć błędną składnię lub być poza 1–65535. Nieobecność oznacza domyślnie 8080, błąd ma przerwać uruchomienie. **Oddaj:** model wyniku i tabelę dla braku, `abc`, `0`, `65535`. **Wskazówka:** jeden pusty optional nie odróżni wszystkich powodów niepowodzenia.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Możesz użyć `expected<optional<Port>, ConfigError>`: pusty sukces to brak, błąd ma kategorię i lokalizację, a obecny sukces niesie zwalidowany port. Następnie warstwa konfiguracji nakłada domyślne 8080. `abc` oznacza składnię, `0` zakres, `65535` sukces. Nie zastępuj każdego błędu domyślną wartością. [Modele błędów](../07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md).

</details>

## 4. Walidacja, która znika w Release

**Wejście:** serwer wykonuje `assert(parse_request(bytes, request));`, a potem używa `request`. W Release żądanie pozostaje nieprzetworzone. **Oddaj:** poprawny przepływ walidacji i osobny przykład zasadnego assert. Kryterium: usunięcie asercji nie może zmienić wymaganych efektów programu. **Wskazówka:** wyrażenie asercji może w ogóle nie zostać wykonane.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wywołaj parser normalnie, sprawdź wynik i zwróć kontrolowany błąd klientowi. Assert może sprawdzać wewnętrzny niezmiennik już ustalony przez kod, np. zgodność liczby elementów dwóch prywatnych struktur; jego argument nie powinien wykonywać niezbędnej pracy. Dane sieciowe pozostają niezaufane niezależnie od konfiguracji budowania. [Kontrakty](../07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md).

</details>

## 5. Fałszywa obietnica noexcept

**Wejście:** konstruktor przenoszący `Item` jest `noexcept`, ale wywołuje logger mogący rzucać. Typ ma także dostępne kopiowanie i jest elementem wektora. **Oddaj:** skutek wyjątku loggera i poprawkę deklaracji lub implementacji. Wyjaśnij wpływ prawdziwej deklaracji na realokację wektora. **Wskazówka:** noexcept nie przechwytuje wyjątku i nie zamienia go w kod błędu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wyjątek wydostający się z takiej funkcji uruchamia `std::terminate`. Usuń rzucającą operację ze ścieżki przenoszenia albo zdejmij nieprawdziwą deklarację. Jeśli przenoszenie może rzucać, a kopiowanie jest dostępne, wektor może wybierać kopiowanie, aby zachować silną gwarancję. Użycie noexcept wymaga dowodu obejmującego wszystkie wywoływane operacje. [Bezpieczeństwo wyjątków](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md).

</details>

## 6. Przechwycenie zmieniające typ błędu

**Wejście:** `DetailedError` dziedziczy po `std::exception`; warstwa pośrednia wykonuje `catch(std::exception e)` i potem `throw e`. **Oddaj:** analizę utraty informacji i poprawny sposób dopisania diagnostyki bez zmiany dynamicznego typu. Uwzględnij niepowodzenie samego logowania. **Wskazówka:** ponowne zgłoszenie aktywnego wyjątku ma osobną składnię.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Przechwycenie przez wartość kopiuje część bazową i powoduje slicing. `throw e` tworzy nowy wyjątek o statycznym typie `std::exception`. Przechwytuj przez `const std::exception&` i użyj `throw;`. Diagnostyka nie powinna maskować pierwotnego błędu; zastosuj nierzucający logger albo lokalnie obsłuż jego awarię. [Wyjątki](../07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md).

</details>
