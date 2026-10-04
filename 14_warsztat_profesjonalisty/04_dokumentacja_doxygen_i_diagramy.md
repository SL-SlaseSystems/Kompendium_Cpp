[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Dokumentacja: Doxygen i diagramy

Dokumentacja techniczna ma pomagać podjąć decyzję bez ponownego odczytywania całej implementacji. Doxygen zbiera komentarze strukturalne oraz informacje z kodu i tworzy nawigowalny opis symboli. Największą wartość daje na publicznej granicy: kontrakcie wejścia, własności, czasie życia, błędach, bezpieczeństwie wątkowym i kosztach. Komentarz powtarzający nazwę funkcji tylko zwiększa powierzchnię wymagającą aktualizacji.

~~~cpp
#include <cassert>
#include <optional>
#include <string_view>

/// Zwraca pozycję pierwszego separatora; brak separatora nie jest błędem.
[[nodiscard]] constexpr std::optional<std::size_t>
first_separator(std::string_view text) noexcept {
    const auto position = text.find(':');
    if (position == std::string_view::npos) return std::nullopt;
    return position;
}

int main() {
    assert(first_separator("host:443") == 4);
    assert(!first_separator("localhost"));
}
~~~

Kod pokazuje, że typ wyniku może dokumentować więcej niż rozbudowany komentarz. `optional` wyraża oczekiwany brak wartości, `string_view` sygnalizuje niewłasnościowy widok, `noexcept` ogranicza zachowanie, a `nodiscard` przypomina klientowi o wyniku. Doxygen powinien dopowiedzieć znaczenie domenowe, a nie tłumaczyć ponownie składnię C++.

## Jak to działa krok po kroku

Najpierw określ odbiorcę. Użytkownik biblioteki potrzebuje stabilnego API, przykładów i kontraktów. Osoba rozwijająca moduł potrzebuje dodatkowo architektury, decyzji oraz instrukcji diagnostycznych. Nie publikuj automatycznie wszystkich prywatnych symboli, bo szum utrudnia znalezienie właściwej informacji i może utrwalić szczegóły implementacyjne jako rzekomy interfejs.

Utwórz minimalny `Doxyfile`, wskaż katalogi publicznych nagłówków i ustaw katalog wyjściowy poza źródłami. Włącz ostrzeżenia dla brakujących lub błędnych odwołań, ale wdrażaj rygor stopniowo w istniejącym projekcie. Wygeneruj HTML lokalnie, otwórz kilka typów i sprawdź nawigację. Sam kod wyjścia nie wykryje nieaktualnego opisu, dlatego review nadal musi zestawiać kontrakt z implementacją i testami.

Diagram dodaj wtedy, gdy relacja jest trudniejsza do zrozumienia w zdaniu lub tabeli. Diagram zależności modułów, sekwencja ważnego protokołu albo lifecycle zasobu mogą być użyteczne. Ogromny automatyczny graf wszystkich klas zwykle pokazuje szczegóły bez hierarchii informacji. Utrzymuj diagram blisko dokumentowanego kontraktu i generuj go deterministycznie, jeśli ma być artefaktem projektu.

## Pogłębienie mechanizmu

Komentarz jest kopią wiedzy i może się zestarzeć. Preferuj konstrukcje, które kompilator weryfikuje: typy jednostek, `enum class`, atrybuty, ograniczenia templates i nazwy funkcji. Komentarz powinien opisywać to, czego system typów nie wyraża: kolejność protokołu, wymaganie zewnętrzne, złożoność, model współbieżności albo powód nietypowej decyzji.

Dokumentowanie wyjątków wymaga precyzji. Nie wystarczy lista klas wyjątków, jeśli klient nie wie, czy operacja zmieniła obiekt. Opisz gwarancję po błędzie oraz warunki wstępne. Dla API niewyjątkowego wskaż model błędu i żywotność treści w obiekcie wyniku. Te zapisy powinny mieć odzwierciedlenie w testach kontraktu.

Doxygen może wykorzystywać Graphviz do części diagramów, ale jest to osobna zależność środowiska. Jeżeli brak diagramu ma zatrzymywać build dokumentacji, zadeklaruj zależność jawnie. Jeżeli diagram jest dodatkiem, skonfiguruj łagodną degradację. Publikując HTML, pamiętaj, że dokumentacja może ujawnić ścieżki, prywatne nazwy i fragmenty kodu — przeglądaj artefakt przed udostępnieniem.

## Drugi przykład

Konfiguracja startowa ogranicza zakres zamiast generować wszystko:

~~~ini
PROJECT_NAME           = "Example Library"
INPUT                  = include README.md
RECURSIVE              = YES
EXTRACT_PRIVATE        = NO
GENERATE_HTML          = YES
GENERATE_LATEX         = NO
WARN_IF_DOC_ERROR      = YES
OUTPUT_DIRECTORY       = out/docs
QUIET                  = YES
~~~

Po wygenerowaniu dokumentacji sprawdź trzy ścieżki: wejście z README do głównego typu, przejście między powiązanymi funkcjami oraz widoczność modelu błędu. Dodaj krótki przykład użycia kompilowany w testach; Doxygen może go prezentować, ale kompilator pilnuje aktualności. Dzięki temu dokumentacja nie staje się osobnym, nietestowanym programem.

## Porównanie i decyzje

README świetnie prowadzi przez cel i pierwsze uruchomienie. Doxygen skaluje się dla referencji symboli. Dokument decyzji architektonicznej wyjaśnia kontekst i kompromisy, a diagram syntetyzuje relacje. Próba umieszczenia wszystkiego w komentarzach API tworzy trudny do przeglądania monolit.

Generowanie przy każdym lokalnym buildzie daje szybkie ostrzeżenia, ale wydłuża zwykłą pętlę. Osobny cel `docs` oraz kontrola w CI zwykle wystarczają. Dla krytycznych przykładów zachowaj natomiast kompilację w standardowym zestawie testów, nawet jeżeli publikacja strony odbywa się rzadziej.

## Powiązane tematy

- [Projektowanie API](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
- [CMake Presets i Ninja](03_cmake_presets_i_ninja.md)
- [Podręcznik Doxygen](https://www.doxygen.nl/manual/index.html)
