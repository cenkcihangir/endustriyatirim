#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_posts_json.py  (haber portalı sürümü)
-------------------------------------------
index.html'in okuduğu posts.json'u üretir. LinkedIn API'sine gerek yok.

Haber portalı şeması — her haber şu alanları taşır:
  slug        : haber sayfası adresi (boşsa başlıktan üretilir)
  kategori    : görünen kategori adı ("Yol / Ulaştırma" vb.)
  cat         : kategori kodu (index.html'deki renk/emoji ile eşleşir)
  baslik      : haber başlığı (manşet)
  spot        : özet/giriş cümlesi
  gorsel      : kapak görseli URL'si (BOŞSA otomatik markalı kapak üretilir)
  govde       : haber metni — paragraf listesi (dizi)
  kaynak      : "EKAP / Kamu İhale Bülteni", "EBRD" vb.
  + ihale alanları: ikn, idare, yer, kapsam[], sure, ihaleTarihi, usul, dokuman
  + hashtags[], linkedinUrl, tarih (YYYY-MM-DD)

Kullanım:
  Hattın ürettiği ham kayıtları to_site_record() ile şemaya çevir,
  write_posts_json() ile yaz, istersen git_publish() ile yayınla.
"""

import json, re, subprocess
from datetime import date
from pathlib import Path

OUT = Path(__file__).parent / "posts.json"

KATEGORI_KOD = {
    "Yol / Ulaştırma":"yol","Yol Yapımı":"yol","Ulaştırma":"yol",
    "Su & Atıksu":"su","İçmesuyu":"su",
    "Enerji":"enerji","GES":"enerji",
    "OSB / Sanayi":"osb","Sanayi":"osb",
    "Bina":"bina","Yapım İşi":"bina","Sağlık":"bina",
    "Uluslararası":"uluslararasi",
    "Şirket & Ekonomi":"sirket","Ekonomi":"sirket","Şirket":"sirket",
}
EMOJI = {"yol":"🛣️","su":"💧","enerji":"⚡","osb":"🏭","bina":"🏥","uluslararasi":"🌍","sirket":"🏢"}


def kod(k): return KATEGORI_KOD.get((k or "").strip(), "osb")

def slugify(s):
    s = (s or "").lower()
    tr = str.maketrans("ıİğüşöçâîû","iigusoçaiu".replace("ç","c"))  # kaba çeviri
    s = s.translate(str.maketrans("ığüşöçİ","igusoci"))
    s = re.sub(r"[^a-z0-9]+","-",s).strip("-")
    return s[:70]

def ensure_brand(tags):
    tags = list(tags or [])
    if "#EndüstriYatırım" not in tags:
        tags.append("#EndüstriYatırım")
    return tags


def to_site_record(r: dict) -> dict:
    """Ham kaydı (r) site şemasına çevir. Sağdaki r.get(...) anahtarlarını
    kendi hattının alan adlarıyla değiştir; soldakiler sabit şema."""
    c = kod(r.get("kategori",""))
    return {
        "slug":        r.get("slug") or slugify(r.get("baslik","")),
        "kategori":    r.get("kategori",""),
        "cat":         c,
        "baslik":      r.get("baslik",""),
        "spot":        r.get("spot",""),
        "gorsel":      r.get("gorsel",""),           # boşsa site otomatik kapak üretir
        "govde":       r.get("govde",[]),            # paragraf listesi
        "kaynak":      r.get("kaynak","EKAP / Kamu İhale Bülteni"),
        "ikn":         r.get("ikn",""),
        "idare":       r.get("idare",""),
        "yer":         r.get("yer",""),
        "kapsam":      r.get("kapsam",[]),
        "sure":        r.get("sure",""),
        "ihaleTarihi": r.get("ihale_tarihi", r.get("ihaleTarihi","")),
        "usul":        r.get("usul","Açık ihale (e-teklif, EKAP)"),
        "dokuman":     r.get("dokuman","https://ekap.kik.gov.tr"),
        "tarih":       r.get("tarih", date.today().isoformat()),
        "hashtags":    ensure_brand(r.get("hashtags",[])),
        "linkedinUrl": r.get("linkedin_url","https://www.linkedin.com/company/endustriyatirim"),
    }


def write_posts_json(raw_records: list) -> None:
    recs = [to_site_record(r) for r in raw_records]
    recs.sort(key=lambda x: x.get("tarih",""), reverse=True)   # en yeni üstte
    OUT.write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {len(recs)} haber yazıldı -> {OUT}")


def git_publish(msg=None):
    """GitHub Pages kullanıyorsan: posts.json'u commit'leyip push'lar."""
    msg = msg or f"posts.json güncellendi ({date.today().isoformat()})"
    repo = OUT.parent
    subprocess.run(["git","add","posts.json"], cwd=repo, check=True)
    subprocess.run(["git","commit","-m",msg], cwd=repo, check=True)
    subprocess.run(["git","push"], cwd=repo, check=True)
    print("✓ GitHub'a push edildi — site birazdan güncellenecek")


# --------------------------------------------------------------------------
# DEMO kayıtlar (index.html'deki örneklerle aynı; gerçekte hattından gelir)
# --------------------------------------------------------------------------
DEMO = [
    {
        "kategori":"Yol / Ulaştırma",
        "baslik":"Manavgat–Akseki bağlantı yolu ihaleye çıktı: 18,4 km bölünmüş yol",
        "spot":"Karayolları 13. Bölge, Antalya'nın iç kesimlerini kıyıya bağlayacak 18,4 km'lik bölünmüş yol için e-teklif sürecini başlattı.",
        "gorsel":"",
        "govde":[
            "Karayolları Genel Müdürlüğü 13. Bölge Müdürlüğü, Manavgat ile Akseki arasındaki bağlantı yolunun yapımı için ihale ilanını yayımladı.",
            "İhale kapsamında 18,4 kilometrelik bölünmüş yol, sanat yapıları ve BSK üstyapı imalatı bulunuyor. Son teklif tarihi 2 Eylül 2026.",
        ],
        "ikn":"2026/812947","idare":"Karayolları 13. Bölge Müdürlüğü","yer":"Antalya / Manavgat",
        "kapsam":["18,4 km bölünmüş yol","Sanat yapıları","BSK üstyapı kaplama"],
        "sure":"540 takvim günü","ihale_tarihi":"02.09.2026 – 10:30",
        "usul":"Açık ihale (e-teklif, EKAP)","dokuman":"https://ekap.kik.gov.tr",
        "tarih":"2026-08-11","kaynak":"EKAP / Kamu İhale Bülteni",
        "hashtags":["#Kamuİhalesi","#YolYapımı","#Karayolları"],
    },
    {
        "kategori":"Su & Atıksu",
        "baslik":"EBRD finansmanlı Malatya su ve atıksu projesi ihaleye hazırlanıyor",
        "spot":"MASKİ, EBRD kredisiyle finanse edilen içmesuyu ve atıksu şebekesi iyileştirmesi için uluslararası ihale sürecini yürütüyor.",
        "gorsel":"",
        "govde":[
            "Malatya Su ve Kanalizasyon İdaresi (MASKİ), EBRD finansmanıyla yürütülen içmesuyu ve atıksu şebekesi iyileştirme projesinin ihale hazırlıklarını sürdürüyor.",
            "Yaklaşık 140 km isale ve şebeke hattı, terfi merkezleri ve SCADA otomasyonunu kapsayan proje EBRD kurallarına göre ihale edilecek.",
        ],
        "ikn":"EBRD-55644","idare":"MASKİ Genel Müdürlüğü","yer":"Malatya (merkez ilçeler)",
        "kapsam":["~140 km isale/şebeke hattı","Terfi merkezleri","SCADA otomasyonu"],
        "sure":"720 takvim günü","ihale_tarihi":"18.09.2026 – 14:00",
        "usul":"Uluslararası açık ihale (EBRD)","dokuman":"https://www.ebrd.com/procurement",
        "tarih":"2026-08-09","kaynak":"EBRD Procurement",
        "hashtags":["#EBRD","#SuAltyapısı","#Atıksu"],
    },
    {
        "kategori":"Enerji",
        "baslik":"Konya Karapınar'da 240 MW'lik güneş santrali için EPC ihalesi",
        "spot":"Karapınar Enerji İhtisas Bölgesi'nde 240 MWe kapasiteli GES sahasının yapımı için davetli EPC ihalesi açıldı.",
        "gorsel":"",
        "govde":[
            "Konya Karapınar'da kurulacak 240 MWe kapasiteli güneş enerjisi santralinin saha yapımı için davetli EPC ihalesi başladı.",
            "İhale kapsamında panel montajı, OSS ve 36 kV OG dağıtım altyapısı bulunuyor. Yapım süresi 420 takvim günü.",
        ],
        "ikn":"2026/799210","idare":"Özel Sektör Yatırımcı","yer":"Konya / Karapınar",
        "kapsam":["240 MWe panel montajı","OSS ve trafo merkezi","36 kV OG dağıtım"],
        "sure":"420 takvim günü","ihale_tarihi":"25.09.2026 – 11:00",
        "usul":"Davetli EPC ihalesi","dokuman":"https://www.linkedin.com/company/endustriyatirim",
        "tarih":"2026-08-08","kaynak":"Yatırımcı duyurusu",
        "hashtags":["#Enerji","#GüneşEnerjisi","#GES"],
    },
    {
        "kategori":"OSB / Sanayi",
        "baslik":"HAVELSAN, Ankara Uzay ve Havacılık OSB altyapı inşaatını ihale ediyor",
        "spot":"Kahramankazan'daki ihtisas OSB'nin yol, altyapı ve enerji hatları için ön yeterlikli ihale süreci yürütülüyor.",
        "gorsel":"",
        "govde":[
            "HAVELSAN A.Ş., Ankara Kahramankazan'daki Uzay ve Havacılık İhtisas OSB'nin altyapı inşaatı için ihale sürecini başlattı.",
            "Yol, altyapı, yağmursuyu, atıksu, içmesuyu ve enerji hatlarını kapsayan proje ön yeterlik sonrası ihale edilecek.",
        ],
        "ikn":"2026/770118","idare":"HAVELSAN A.Ş.","yer":"Ankara / Kahramankazan",
        "kapsam":["Yol ve altyapı","Yağmursuyu ve atıksu","İçmesuyu ve enerji hatları"],
        "sure":"600 takvim günü","ihale_tarihi":"30.09.2026 – 10:00",
        "usul":"Ön yeterlik + belli istekliler arası","dokuman":"https://ekap.kik.gov.tr",
        "tarih":"2026-08-07","kaynak":"EKAP",
        "hashtags":["#OSB","#Sanayi","#Altyapı"],
    },
    {
        "kategori":"Bina",
        "baslik":"Hatay Şehir Hastanesi ihalesi: 1.000 yataklı dev sağlık kampüsü",
        "spot":"Sağlık Bakanlığı, Antakya'da kurulacak 1.000 yataklı şehir hastanesinin yapımı için e-teklif sürecini başlattı.",
        "gorsel":"",
        "govde":[
            "Sağlık Bakanlığı, Hatay Antakya'da 1.000 yataklı şehir hastanesinin yapımı için ihale ilanı yayımladı.",
            "Ana bina, 17.500 kVA jeneratör grubu ve tam tıbbi gaz sistemlerini kapsayan projenin süresi 900 takvim günü.",
        ],
        "ikn":"2026/770483","idare":"Sağlık Bakanlığı","yer":"Hatay / Antakya",
        "kapsam":["1.000 yatak ana bina","17.500 kVA jeneratör","Tam tıbbi gaz sistemleri"],
        "sure":"900 takvim günü","ihale_tarihi":"08.10.2026 – 11:30",
        "usul":"Açık ihale (e-teklif, EKAP)","dokuman":"https://ekap.kik.gov.tr",
        "tarih":"2026-08-05","kaynak":"EKAP / Kamu İhale Bülteni",
        "hashtags":["#ŞehirHastanesi","#Sağlık","#Yapımİşi"],
    },
    {
        "kategori":"Uluslararası",
        "baslik":"Karabağ sulama kanalı rehabilitasyonu: IsDB finansmanlı yeni fırsat",
        "spot":"Azerbaycan'da IsDB finansmanıyla yürütülecek Karabağ sulama kanalı projesinin inşaat ihaleleri 2027'de bekleniyor.",
        "gorsel":"",
        "govde":[
            "Azerbaycan'ın Karabağ bölgesinde, IsDB finansmanıyla yürütülecek sulama kanalı rehabilitasyon projesinin ön hazırlıkları sürüyor.",
            "Ana kanal, su alma yapıları ve pompa istasyonlarını kapsayan projenin inşaat ihaleleri 2027'de bekleniyor.",
        ],
        "ikn":"IsDB-AZ-2027","idare":"Azərsu ASC","yer":"Azerbaycan / Karabağ",
        "kapsam":["Ana kanal rehabilitasyonu","Su alma yapıları","Pompa istasyonları"],
        "sure":"İnşaat ihaleleri 2027 bekleniyor","ihale_tarihi":"İlan öncesi (ön bilgi)",
        "usul":"IsDB finansmanlı uluslararası ihale","dokuman":"https://www.isdb.org",
        "tarih":"2026-08-04","kaynak":"IsDB Project Procurement",
        "hashtags":["#IsDB","#Sulama","#Azerbaycan"],
    },
]

if __name__ == "__main__":
    write_posts_json(DEMO)
    # GitHub Pages kullanıyorsan alttaki satırı aç:
    # git_publish()
