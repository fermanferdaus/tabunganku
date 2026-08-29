from datetime import datetime

BULAN_INDONESIA = {
    1: 'Januari',
    2: 'Februari',
    3: 'Maret',
    4: 'April',
    5: 'Mei',
    6: 'Juni',
    7: 'Juli',
    8: 'Agustus',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'Desember'
}


def format_tanggal_indonesia(tgl):
    """Format tanggal menjadi '12 November 2020'."""
    if not tgl:
        return ''
    if hasattr(tgl, 'day') and hasattr(tgl, 'month') and hasattr(tgl, 'year'):
        return f"{tgl.day} {BULAN_INDONESIA.get(tgl.month, '')} {tgl.year}"
    if isinstance(tgl, str):
        try:
            tgl_clean = tgl.strip()
            if '-' in tgl_clean:
                dt = datetime.strptime(tgl_clean, '%Y-%m-%d')
            elif '/' in tgl_clean:
                dt = datetime.strptime(tgl_clean, '%d/%m/%Y')
            else:
                return tgl_clean
            return f"{dt.day} {BULAN_INDONESIA.get(dt.month, '')} {dt.year}"
        except Exception:
            return tgl
    return str(tgl)


def format_waktu_wib(wkt):
    """Format waktu menjadi 'HH:MM WIB'."""
    if not wkt:
        return ''
    wkt_str = str(wkt).strip()
    parts = wkt_str.split(':')
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)} WIB"
    return f"{wkt_str} WIB"


def format_rupiah(nominal):
    """Format angka menjadi 'Rp 50.000'."""
    if nominal is None:
        return 'Rp 0'
    try:
        nom_int = int(nominal)
        formatted = f"{nom_int:,}".replace(',', '.')
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return f"Rp {nominal}"
