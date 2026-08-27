[← Spis treści](../README.md)

# Korutyny

Korutyna może zawiesić wykonanie i później je wznowić, zachowując stan w coroutine frame. Słowa `co_await`, `co_yield` i `co_return` uruchamiają transformację kompilatora. C++20 dostarcza mechanikę, ale nie standardowy typ `task`, event loop ani model I/O async.

Minimalny generator wymaga własnego `promise_type`, zarządzania uchwytem i iteratora, dlatego pełny przykład jest dłuższy niż zwykła funkcja. Poniższy szkic pokazuje kształt API biblioteki, nie samowystarczalny C++23:

~~~cpp,notest
generator<int> sequence() {
    for (int value = 0; value < 3; ++value) {
        co_yield value;
    }
}

task<Response> fetch(Client& client) {
    Response response = co_await client.get("/status");
    co_return response;
}
~~~

Typ zwracany wybiera `promise_type`. Kompilator tworzy frame, wywołuje `get_return_object`, `initial_suspend`, a przy końcu `final_suspend`. Wyrażenie `co_await` jest przekształcane do awaitera z metodami `await_ready`, `await_suspend` i `await_resume`. Szczegóły są opisane w dziale zaawansowanym.

Zawieszenie nie tworzy automatycznie nowego wątku. To awaiter/executor decyduje, kiedy i gdzie nastąpi wznowienie. Dane referencyjne przechowywane w frame muszą żyć wystarczająco długo. Zniszczenie uchwytu kończy frame; biblioteka musi precyzyjnie określić własność coroutine handle.

Anulowanie jest kooperacyjne i wymaga kontraktu cancellation safety. Operacja przerwana w połowie nie może zgubić odpowiedzi, blokady lub bajtów protokołu w sposób mylący kolejne wywołanie.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Korutyny”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz identyfikację wymaganej funkcji, sprawdzenie feature-test macro, wybór implementacji i weryfikację na wszystkich wspieranych toolchainach. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wersję języka ustawioną flagą od faktycznej implementacji funkcji i dostępności odpowiedniego komponentu biblioteki standardowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wartość makra funkcji, wynik kompilacji minimalnego przykładu, status implementacji i test na najstarszym wspieranym narzędziu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Edycje standardu dodają język i bibliotekę, lecz ich obecność w dokumencie nie oznacza kompletnego wsparcia toolchainu. Kod produkcyjny potrzebuje macierzy kompilator–biblioteka–platforma oraz polityki fallbacku. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Korutyna jest transformowana do maszyny stanów z ramką przechowującą parametry i lokale żyjące przez zawieszenie. Typ zwracany oraz `promise_type` definiują protokół, a sam język nie dostarcza schedulera.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Korutyny” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Korutyny
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Korutyny”, oceniaj wartość funkcji dla projektu, dojrzałość implementacji, koszt fallbacku, wpływ na ABI oraz termin wsparcia toolchainu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Mechanika korutyn](../zaawansowane/12_korutyny_promise_awaitery_i_frame.md)
- [future i async](../10_wspolbieznosc/03_future_promise_async.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)

