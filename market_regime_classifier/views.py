from django.shortcuts import render
from django.utils import timezone

# Basic regime scoring engine
REGIME_THRESHOLDS = {
    'rangebound': 0.7,
    'bullish': 0.05,
    'bearish': 0.05,
    'volatile': 0.2,
}


def score_regime(atr, vwap_slope, pcr, iv_delta):
    # ATR contraction and small VWAP slope favor rangebound.
    # Large positive/negative slope favors bullish/bearish.
    # High IV increase indicates volatility.
    rangebound = max(0.0, (1.0 - abs(atr * 25)) * 0.6 + (1.0 - abs(vwap_slope)) * 0.4)
    bullish = max(0.0, (vwap_slope / 1.5) + (1 - pcr) * 0.2 - (iv_delta * 0.5))
    bearish = max(0.0, (-vwap_slope / 1.5) + (pcr - 1) * 0.2 - (iv_delta * 0.5))
    volatile = max(0.0, min(1.0, abs(iv_delta) * 5.0))

    total = rangebound + bullish + bearish + volatile
    if total <= 0.0:
        total = 1.0

    return {
        'rangebound': rangebound / total,
        'bullish': bullish / total,
        'bearish': bearish / total,
        'volatile': volatile / total,
    }


def pick_regime(score_map):
    regime = max(score_map, key=score_map.get)
    confidence = int(round(score_map[regime] * 100))
    return regime.upper(), confidence


def build_evidence(atr, vwap_slope, pcr, iv_delta):
    items = []
    if atr < 0.03:
        items.append('ATR contraction')
    else:
        items.append('ATR expansion')

    if abs(vwap_slope) < 0.075:
        items.append('VWAP flat')
    elif vwap_slope > 0:
        items.append('VWAP upward')
    else:
        items.append('VWAP downward')

    if 0.85 <= pcr <= 1.15:
        items.append('PCR stable')
    else:
        items.append('PCR skewed')

    if iv_delta < 0:
        items.append('IV falling')
    else:
        items.append('IV rising')

    return items


def index(request):
    # Loading from query strings for testing; in production, wire to real market data pipeline.
    atr = float(request.GET.get('atr', 0.02))
    vwap_slope = float(request.GET.get('vwap_slope', 0.01))
    pcr = float(request.GET.get('pcr', 0.92))
    iv_delta = float(request.GET.get('iv_delta', -0.06))

    override = request.GET.get('override', '').strip().lower()
    score_map = score_regime(atr, vwap_slope, pcr, iv_delta)
    regime, confidence = pick_regime(score_map)

    if override in ['bullish', 'bearish', 'rangebound', 'volatile']:
        regime = override.upper()
        confidence = 100

    evidence_items = build_evidence(atr, vwap_slope, pcr, iv_delta)

    regime_metrics = [
        {'name': 'Bullish', 'slug': 'bullish', 'value': int(round(score_map['bullish'] * 100))},
        {'name': 'Bearish', 'slug': 'bearish', 'value': int(round(score_map['bearish'] * 100))},
        {'name': 'Rangebound', 'slug': 'rangebound', 'value': int(round(score_map['rangebound'] * 100))},
        {'name': 'Volatile', 'slug': 'volatile', 'value': int(round(score_map['volatile'] * 100))},
    ]

    context = {
        'regime': regime,
        'confidence': confidence,
        'evidence_items': evidence_items,
        'atr': atr,
        'vwap_slope': vwap_slope,
        'pcr': pcr,
        'iv_delta': iv_delta,
        'updated_at': timezone.now(),
        'regime_scores': score_map,
        'regime_metrics': regime_metrics,
        'manual_override': override.upper() if override else None,
    }

    return render(request, 'market_regime_classifier/regime_classifier.html', context)


def live_data(request):
    # Mock live feed values (replace with real API / data pipeline integration as needed)
    import random

    atr = round(random.uniform(0.01, 0.06), 4)
    vwap_slope = round(random.uniform(-0.2, 0.2), 4)
    pcr = round(random.uniform(0.7, 1.3), 2)
    iv_delta = round(random.uniform(-0.1, 0.15), 4)

    score_map = score_regime(atr, vwap_slope, pcr, iv_delta)
    regime, confidence = pick_regime(score_map)
    evidence_items = build_evidence(atr, vwap_slope, pcr, iv_delta)

    response_data = {
        'regime': regime,
        'confidence': confidence,
        'atr': atr,
        'vwap_slope': vwap_slope,
        'pcr': pcr,
        'iv_delta': iv_delta,
        'updated_at': timezone.now().isoformat(),
        'evidence_items': evidence_items,
        'scores': {k: int(round(v * 100)) for k, v in score_map.items()},
        'override': None,
    }

    from django.http import JsonResponse
    return JsonResponse(response_data)


