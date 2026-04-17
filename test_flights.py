#!/usr/bin/env python3
"""
Teste basico do scraper fast-flights
Verifica se as dependencias estao instaladas e se consegue fazer uma busca
"""

from fast_flights import Passengers, get_flights_round_trip


def test_flights():
    """Testa busca por periodo de datas"""
    print("=" * 70)
    print("Busca de voos por periodo")
    print("=" * 70)

    try:
        print("\n[INFO] Buscando ida e volta GRU -> HND (2026-12-18 a 2027-01-11)...")
        results = get_flights_round_trip(
            from_airport="GRU",
            to_airport="NRT",
            date_from="2026-12-18",
            date_to="2027-01-11",
            seat="economy",
            passengers=Passengers(adults=1),
            language="pt-BR",
            currency="BRL",
        )

        print("[OK] Busca concluida!\n")

        if results:
            count = len(results)
            precos = [f.price for f in results]
            preco_min = min(precos)
            preco_max = max(precos)
            preco_medio = sum(precos) // len(precos)

            airlines_set = set()
            for flight in results:
                airlines_set.update(flight.airlines)

            print("[RESUMO]")
            print(f"  Total de voos: {count}")
            print(f"  Preco: R$ {preco_min} - R$ {preco_max} (medio: R$ {preco_medio})")
            print(f"  Companhias: {', '.join(sorted(airlines_set))}")

            print(f"\n[TOP 5 VOOS MAIS BARATOS]")
            for i, flight in enumerate(sorted(results, key=lambda f: f.price)[:5], 1):
                try:
                    if flight.flights and len(flight.flights) >= 2:
                        leg_out = flight.flights[0]
                        leg_ret = flight.flights[1]

                        # Formata horários com validação
                        def format_time(time_tuple):
                            if not time_tuple or len(time_tuple) == 0:
                                return "N/A"
                            if len(time_tuple) >= 2:
                                return f"{time_tuple[0]:02d}:{time_tuple[1]:02d}"
                            return f"{time_tuple[0]:02d}:00"

                        dep_out = format_time(leg_out.departure.time)
                        arr_out = format_time(leg_out.arrival.time)
                        dep_ret = format_time(leg_ret.departure.time)
                        arr_ret = format_time(leg_ret.arrival.time)

                        print(f"  {i}. {flight.airlines[0]:10s} | IDA: {dep_out}-{arr_out} | VOLTA: {dep_ret}-{arr_ret} | R$ {flight.price:5d}")
                except Exception as e:
                    print(f"  {i}. {flight.airlines[0]:10s} | R$ {flight.price:5d} (erro ao formatar horários)")
        else:
            print("[WARN] Nenhum voo encontrado")

        print("\n" + "-" * 70)

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_flights()

    print("\n" + "=" * 70)
    if success:
        print("[OK] Teste concluido com sucesso!")
    else:
        print("[ERROR] Teste falhou!")
    print("=" * 70)
