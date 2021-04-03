from datetime import datetime, timedelta

def rango_horas(inicio, fin, delta):
    actual = inicio
    while actual < fin:
        yield actual
        actual += delta

def intervalo_horas():
    ## Hora de inicio
    inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ## Hora fin
    fin = inicio + timedelta(hours=24)
    ## Intervalos (minutos)
    intervalo = 30

    return [ (dt.time(), dt.strftime('%H:%M')) for dt in rango_horas(inicio, fin, timedelta(minutes=intervalo)) ]

def es_numerico(s):
    try:
        float(s)
        return True
    except ValueError:
        return False