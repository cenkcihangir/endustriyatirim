#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_posts_json.py
-------------------
Endüstri Yatırım Gündemi sitesini besleyen posts.json dosyasını üretir.

Kullanım fikri:
  Mevcut ihale-parse hattın her ihale için zaten bir sözlük (dict) üretiyor.
  O sözlükleri bu dosyadaki SITE şemasına eşleyip posts.json'a yazdır.
  Site (index.html) bu dosyayı okur; LinkedIn API'sine gerek yok.

Akış:
  1) Hattın ihaleleri parse eder            -> ham kayıtlar
  2) to_site_record() ile şemaya çevir      -> site kayıtları
  3) write_posts_json() ile dosyayı yaz     -> posts.json
  4) (opsiyonel) git commit + push          -> GitHub Pages otomatik yayınlar
"""

import json
import subprocess
from datetime import date
from pathlib import Path

OUT = Path(__file__).parent / "posts.json"

# Kategori kodları (index.html'deki --c-<cat> renkleriyle eşleşmeli)
# yeni kategori eklersen index.html'e de bir --c-xxx rengi ekle.
KATEGORI_KOD = {
    "Yol Yapımı": "yol",
    "Ulaştırma": "yol",
    "Su & Atıksu": "su",
    "İçmesuyu": "su",
    "Enerji": "enerji",
    "GES": "enerji",
    "OSB / Sanayi": "osb",
    "Sanayi": "osb",
    "Bina": "bina",
    "Yapım İşi": "bina",
    "Uluslararası": "uluslararasi",
}

EMOJI = {
    "yol": "🛣️", "su": "💧", "enerji": "⚡",
    "osb": "🏭", "bina": "🏥", "uluslararasi": "🌍",
}


def kod(kategori: str) -> str:
    return KATEGORI_KOD.get(kategori.strip(), "osb")


def to_site_record(r: dict) -> dict:
    """
    Hattının ham ihale kaydını (r) sitenin beklediği şemaya çevirir.
    Sağ taraftaki r.get(...) alan adlarını KENDİ hattının alan adlarıyla
    değiştir. Solda kalan anahtarlar sitenin sabit şemasıdır — dokunma.
    """
    c = kod(r.get("kategori", ""))
    return {
        "emoji":       r.get("emoji") or EMOJI.get(c, "📌"),
        "kategori":    r.get("kategori", ""),
        "cat":         c,
        "il":          r.get("il", r.get("yer", "")),
        "baslik":      r.get("baslik", r.get("proje", "")),
        "ikn":         r.get("ikn", ""),
        "idare":       r.get("idare", ""),
        "yer":         r.get("yer", ""),
        "kapsam":      r.get("kapsam", []),          # liste bekleniyor
        "sure":        r.get("sure", ""),
        "ihaleTarihi": r.get("ihale_tarihi", r.get("ihaleTarihi", "")),
        "usul":        r.get("usul", "Açık ihale (e-teklif, EKAP)"),
        "dokuman":     r.get("dokuman", "https://ekap.kik.gov.tr"),
        "tarih":       r.get("tarih", date.today().isoformat()),  # YYYY-MM-DD sıralama için
        "hashtags":    ensure_brand(r.get("hashtags", [])),
        "linkedinUrl": r.get("linkedin_url", "https://www.linkedin.com/company/endustriyatirim"),
    }


def ensure_brand(tags: list) -> list:
    """Her gönderide #EndüstriYatırım bulunsun (senin kuralın)."""
    tags = list(tags or [])
    if "#EndüstriYatırım" not in tags:
        tags.append("#EndüstriYatırım")
    return tags


def write_posts_json(raw_records: list) -> None:
    site_records = [to_site_record(r) for r in raw_records]
    # en yeni üste gelsin
    site_records.sort(key=lambda x: x.get("tarih", ""), reverse=True)
    OUT.write_text(
        json.dumps(site_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ {len(site_records)} kayıt yazıldı -> {OUT}")


def git_publish(msg: str = None) -> None:
    """
    Opsiyonel: GitHub Pages kullanıyorsan bu fonksiyon posts.json'u
    commit'leyip push'lar; sayfa 30-60 sn içinde otomatik güncellenir.
    """
    msg = msg or f"posts.json güncellendi ({date.today().isoformat()})"
    repo = OUT.parent
    subprocess.run(["git", "add", "posts.json"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=repo, check=True)
    subprocess.run(["git", "push"], cwd=repo, check=True)
    print("✓ GitHub'a push edildi — site birazdan güncellenecek")


# --------------------------------------------------------------------------
# DEMO: hattın çıktısı böyle bir liste olacak. Gerçekte parse'tan gelir.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    ornek_ham_kayitlar = [
        {
            "kategori": "Yol Yapımı",
            "baslik": "Manavgat–Akseki Bağlantı Yolu Yapım İşi",
            "ikn": "2026/812947",
            "idare": "Karayolları 13. Bölge Müdürlüğü",
            "yer": "Antalya / Manavgat",
            "il": "Antalya / Manavgat",
            "kapsam": ["18,4 km bölünmüş yol", "Sanat yapıları", "Üstyapı ve BSK kaplama"],
            "sure": "540 takvim günü",
            "ihale_tarihi": "02.09.2026 – 10:30",
            "usul": "Açık ihale (e-teklif, EKAP)",
            "dokuman": "https://ekap.kik.gov.tr",
            "tarih": "2026-08-11",
            "hashtags": ["#Kamuİhalesi", "#YolYapımı", "#Karayolları"],
            "linkedin_url": "https://www.linkedin.com/company/endustriyatirim",
        },
        # ... hattının ürettiği diğer ihaleler buraya
    ]

    write_posts_json(ornek_ham_kayitlar)
    # GitHub Pages kullanacaksan alttaki satırın başındaki # işaretini kaldır:
    # git_publish()
