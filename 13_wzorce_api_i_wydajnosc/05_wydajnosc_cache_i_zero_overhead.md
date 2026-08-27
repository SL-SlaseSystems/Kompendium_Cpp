[← Spis treści](../README.md)

# Wydajność, cache i zero-overhead

Zasada zero-overhead mówi, że nieużywane mechanizmy nie powinny kosztować, a użyte abstrakcje mają być konkurencyjne z ręczną implementacją. Nie oznacza, że każdy szablon, iterator lub lambda jest zawsze szybsza. Wydajność zależy od algorytmu, reprezentacji danych, pamięci, optymalizatora i sprzętu.

~~~cpp
#include <cassert>
#include <numeric>
#include <vector>

int sum(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

int main() {
    const std::vector values{10, 20, 12};
    assert(sum(values) == 42);
}
~~~

Iteratorowy algorytm może zostać zoptymalizowany do zwykłej pętli bez obiektu sterującego runtime. Największe zyski często wynikają jednak z wyboru złożoności i układu danych, nie mikrooptymalizacji składni. Ciągły vector zwykle wykorzystuje cache lepiej niż lista z osobnymi węzłami.

Koszty obejmują alokacje, cache misses, branch misprediction, synchronizację, kopiowanie, rozrost kodu po monomorfizacji i brak inline przez granice ABI. Small-buffer optimization jest detalem konkretnego typu/implementacji, jeśli standard go nie gwarantuje. Copy elision może być gwarantowana w wybranych kontekstach, ale `std::move` lokalnego wyniku może ją utrudnić.

Buduj release z odpowiednią optymalizacją, a przy whole-program scenariuszach rozważ LTO. Profile-guided optimization wykorzystuje reprezentatywne wykonania. Każda opcja zmienia czas budowania, debugowalność i czasem ABI; włączaj ją przez kontrolowane profile.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Wydajność, cache i zero-overhead”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz ustanowienie kontraktu typu, rozdzielenie interfejsu od implementacji, wykonanie operacji i zmierzenie kosztu na granicy abstrakcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie domenowe od mechanizmu implementacyjnego, publiczne ABI od prywatnego layoutu i hipotezę wydajności od pomiaru. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź przykładowe użycie API, rozmiar i layout typu, symbole biblioteki, profil CPU oraz liczbę alokacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projektowanie C++ łączy semantykę wartości, własność, stabilność ABI i koszt abstrakcji. Dobra abstrakcja utrudnia niewłaściwe użycie, ale pozostawia kompilatorowi wystarczającą informację do optymalizacji. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Lokalność danych często wpływa na wydajność bardziej niż liczba instrukcji źródłowych. Zero-overhead abstractions należy oceniać na assembly i profilu; szablon może usunąć dispatch, ale zwiększyć kod i presję instruction cache.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Wydajność, cache i zero-overhead” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Wydajność, cache i zero-overhead
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Wydajność, cache i zero-overhead”, oceniaj łatwość poprawnego użycia, value semantics, stabilność kontraktu, koszt kompilacji i zmierzona wydajność krytycznej ścieżki. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Najpierw mierz profil całej aplikacji. Zapisz baseline i budżet, popraw gorącą ścieżkę, a potem potwierdź wynik oraz regresje pamięci. Nie poświęcaj lifetime safety i czytelności dla niezmierzonej oszczędności.

## Powiązane tematy

- [Benchmarki i profilowanie](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [Kontenery sekwencyjne](../06_biblioteka_standardowa/02_vector_array_deque_list.md)
- [SIMD i optymalizacja](../zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

