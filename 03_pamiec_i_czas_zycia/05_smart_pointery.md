[← Spis treści](../README.md)

# Smart pointery

Smart pointer reprezentuje własność dynamicznego obiektu przez RAII. `std::unique_ptr<T>` oznacza jednego właściciela, jest niekopiowalny i przenoszalny. `std::shared_ptr<T>` współdzieli własność przez blok kontrolny z licznikami. `std::weak_ptr<T>` obserwuje obiekt zarządzany przez `shared_ptr`, ale nie przedłuża jego życia.

~~~cpp
#include <cassert>
#include <memory>
#include <string>

struct User {
    std::string name;
};

int main() {
    auto owner = std::make_shared<User>(User{"Ada"});
    std::weak_ptr<User> observer = owner;

    if (auto user = observer.lock()) {
        assert(user->name == "Ada");
    }

    owner.reset();
    assert(observer.expired());
}
~~~

Preferuj `std::make_unique` i `std::make_shared`, ponieważ łączą konstrukcję z przejęciem własności i upraszczają exception safety. `make_shared` zwykle umieszcza obiekt i blok kontrolny w jednej alokacji, ale pamięć obiektu może pozostać zarezerwowana, dopóki istnieją słabe referencje.

`shared_ptr` nie czyni samego obiektu bezpiecznym wątkowo. Niezależne instancje smart pointerów mogą współdzielić blok kontrolny, lecz równoczesny dostęp do pól `T` nadal wymaga synchronizacji. Cykle silnych referencji nie znikają automatycznie: co najmniej jedna krawędź w cyklu powinna być słaba albo model własności powinien zostać uproszczony.

Surowy wskaźnik uzyskany przez `.get()` jest niewłaścicielski. Nie wolno tworzyć z niego drugiego niezależnego `unique_ptr` lub `shared_ptr`. Jeśli obiekt ma żyć dokładnie w jednym zakresie, zwykła wartość jest prostsza niż dynamiczna alokacja.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Smart pointery”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `unique_ptr` koduje wyłączną własność i ma mały koszt, `shared_ptr` utrzymuje współdzielony control block, a `weak_ptr` obserwuje bez tworzenia cyklu. Wybór wynika z grafu własności, nie z chęci uniknięcia jawnej decyzji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Smart pointery” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Smart pointery
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Smart pointery”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Dynamiczna pamięć](02_stos_sterta_i_dynamiczna_pamiec.md)
- [RAII](03_raii_i_destruktory.md)
- [Współbieżność i mutex](../10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)

