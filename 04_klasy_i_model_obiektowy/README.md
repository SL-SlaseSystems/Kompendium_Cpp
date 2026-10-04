[← Główny spis treści](../README.md)

# 04. Klasy i model obiektowy

Klasa w C++ może być prostym typem wartościowym, właścicielem zasobu, granicą modułu albo uczestnikiem polimorfizmu. Dział pokazuje, jak dobrać ten model świadomie i jak utrzymywać inwariant zamiast ukrywać dane bez celu.

## Wymagania wstępne

Wymagana jest znajomość funkcji, referencji, wskaźników, lifetime, RAII oraz podstaw copy i move.

## Efekty uczenia się

- projektujesz klasy z jawnym inwariantem i małym interfejsem;
- rozumiesz kolejność konstrukcji, destrukcji i inicjalizacji składowych;
- stosujesz rule of zero i poprawne przeciążenia operatorów;
- wybierasz kompozycję lub dziedziczenie na podstawie relacji domenowej;
- korzystasz z wirtualności i RTTI tylko tam, gdzie potrzebny jest polimorfizm runtime;
- modelujesz warianty danych przez `enum class`, `variant` lub polimorfizm.

## Kolejność rozdziałów

1. [struct, class i enkapsulacja](01_struct_class_i_enkapsulacja.md)
2. [Konstruktory i destruktory](02_konstruktory_i_destruktory.md)
3. [Funkcje specjalne i operatory](03_funkcje_specjalne_i_operatory.md)
4. [Dziedziczenie i polimorfizm](04_dziedziczenie_i_polimorfizm.md)
5. [virtual, override i RTTI](05_virtual_override_i_rtti.md)
6. [enum, union i variant](06_enum_union_i_variant.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Sposób pracy

Najpierw zapisz inwariant i dozwolone operacje, dopiero potem pola. Testuj zachowanie publiczne, nie układ prywatnych składowych. Dla hierarchii narysuj ownership osobno od relacji polimorficznej.

## Pułapki

- getter i setter dla każdego pola bez ochrony inwariantu;
- wywoływanie funkcji wirtualnych z konstruktora lub destruktora;
- brak wirtualnego destruktora w polimorficznej bazie usuwanej przez wskaźnik bazowy;
- dziedziczenie użyte wyłącznie do ponownego wykorzystania kodu;
- przeciążony operator o zaskakującej semantyce.

## Samoocena

Potrafisz zaprojektować typ wartościowy, klasę RAII i mały interfejs polimorficzny, a następnie uzasadnić, dlaczego każdy z nich ma inną politykę kopiowania, destrukcji i rozszerzania.

## Co dalej

Przejdź do [szablonów i generyczności](../05_szablony_i_generycznosc/README.md), aby te same kontrakty wyrażać dla rodzin typów i algorytmów.
