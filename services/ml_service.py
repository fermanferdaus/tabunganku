import os
import joblib
import numpy as np
import pandas as pd
from matplotlib.colors import rgb_to_hsv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    stacking_model = joblib.load(os.path.join(BASE_DIR, 'models/stacking_model.pkl'))
    label_encoder = joblib.load(os.path.join(BASE_DIR, 'models/label_encoder.pkl'))
    scaler = joblib.load(os.path.join(BASE_DIR, 'models/scaler.pkl'))
    print("[ML Service] Model Stacking Ensemble dan preprocessors berhasil dimuat.")
except Exception as e:
    print(f"[ML Service Warning] Gagal memuat file model: {e}")
    stacking_model, label_encoder, scaler = None, None, None


def extract_features(red, green, blue):
    """
    Mengekstraksi fitur spektrum warna diskriminatif dari pembacaan sensor Red Green Blue
    meliputi rasio normalisasi kromatisitas, kontras dinamis, ruang warna HSV, proyeksi sin cos Hue,
    selisih warna lawan, rasio logaritmik, serta luminansi.
    """
    R = float(red)
    G = float(green)
    B = float(blue)
    eps = 1e-7
    total = R + G + B + eps

    r_ratio = R / total
    g_ratio = G / total
    b_ratio = B / total
    contrast = max(R, G, B) - min(R, G, B)

    rgb_raw = np.array([[[R, G, B]]], dtype=float)
    rgb_norm = (rgb_raw - rgb_raw.min()) / (rgb_raw.max() - rgb_raw.min() + 1e-8)
    hsv_arr = rgb_to_hsv(rgb_norm).reshape(-1, 3)
    hue = hsv_arr[0, 0]
    sat = hsv_arr[0, 1]
    bri = hsv_arr[0, 2]

    if scaler is not None and getattr(scaler, 'n_features_in_', 11) >= 20:
        hue_sin = np.sin(hue * 2 * np.pi)
        hue_cos = np.cos(hue * 2 * np.pi)
        rg_diff = (R - G) / (R + G + eps)
        rb_diff = (R - B) / (R + B + eps)
        gb_diff = (G - B) / (G + B + eps)
        yb_opp = (R + G - 2 * B) / total
        log_rg = np.log((R + 1) / (G + 1))
        log_rb = np.log((R + 1) / (B + 1))
        log_gb = np.log((G + 1) / (B + 1))
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        return pd.DataFrame([{
            'Red': R, 'Green': G, 'Blue': B,
            'R_ratio': r_ratio, 'G_ratio': g_ratio, 'B_ratio': b_ratio,
            'Intensity': total, 'Contrast': contrast,
            'Hue': hue, 'Hue_sin': hue_sin, 'Hue_cos': hue_cos,
            'Saturation': sat, 'Brightness': bri,
            'RG_diff': rg_diff, 'RB_diff': rb_diff, 'GB_diff': gb_diff,
            'YB_opp': yb_opp,
            'Log_RG': log_rg, 'Log_RB': log_rb, 'Log_GB': log_gb,
            'Luminance': lum
        }])
    else:
        return pd.DataFrame([{
            'Red': R, 'Green': G, 'Blue': B,
            'R_ratio': r_ratio, 'G_ratio': g_ratio, 'B_ratio': b_ratio,
            'Intensity': total, 'Contrast': contrast,
            'Hue': hue, 'Saturation': sat, 'Brightness': bri
        }])


def prediksi_nominal_stacking(red, green, blue):
    """
    Memprediksi pecahan nominal uang kertas berdasarkan nilai warna Red Green Blue
    menggunakan model Stacking Ensemble Classifier.
    """
    if stacking_model is None or label_encoder is None or scaler is None:
        raise ValueError("Model ML belum dimuat dengan benar.")

    nilai = extract_features(red, green, blue)
    nilai_scaled = scaler.transform(nilai)
    hasil = stacking_model.predict(nilai_scaled)
    predicted_nominal = label_encoder.inverse_transform(hasil)[0]
    return int(predicted_nominal)
