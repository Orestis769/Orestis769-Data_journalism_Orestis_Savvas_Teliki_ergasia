# Ανάλυση πολιτικού λόγου στο TikTok (ΕΔΔΕ2)

Ανάλυση μεγάλων δεδομένων σε **155 βίντεο** του επίσημου λογαριασμού του Κυριάκου
Μητσοτάκη στο TikTok (`@kyriakosmitsotakis_`), περίοδος 2022–2026. Τα δεδομένα
εξορύχθηκαν από το διαδίκτυο (web scraping με yt-dlp) και απομαγνητοφωνήθηκαν
τοπικά με το μοντέλο Whisper.

**Συγγραφέας:** Σάββας Ορέστης — orestissavas@gmail.com
**Μάθημα:** ΕΔΔΕ2 – Ανάλυση Μεγάλων Δεδομένων μέσω της Γλώσσας Python

## Δομή

```
.
├── analysis.py               # Κύρια ανάλυση (βήματα 2–12 της εργασίας)
├── greek_nlp.py              # Ελληνικά stopwords, stemmer, λεξικό συναισθήματος
├── make_pdf.py               # Δημιουργία του άρθρου PDF
├── requirements_analysis.txt # Εξαρτήσεις
├── dataset_processed.csv     # Πλήρες επεξεργασμένο dataframe (155 εγγραφές)
├── dataset_sample.csv        # Δείγμα 20 εγγραφών
├── tiktok_output/
│   ├── transcripts/          # 161 απομαγνητοφωνήσεις (.txt)
│   └── _audio/               # μεταδεδομένα (.info.json) — χωρίς τα mp3
└── charts/                   # Όλα τα γραφήματα (PNG)
```

> Τα αρχεία ήχου (.mp3, ~242MB) δεν ανεβαίνουν στο repo. Τα κείμενα και τα
> μεταδεδομένα αρκούν ώστε να τρέχει πλήρως ο κώδικας.

## Εκτέλεση

```bash
pip install -r requirements_analysis.txt
python analysis.py     # -> dataset_processed.csv + φάκελος charts/
python make_pdf.py     # -> το άρθρο σε PDF
```

## Αντιστοίχιση βημάτων εργασίας → κώδικα

| Βήμα | Υλοποίηση |
|---|---|
| Scraping | yt-dlp + Whisper (παραγωγή `tiktok_output/`) |
| Φόρτωση σε DataFrame | `load_dataframe()` |
| Καθαρισμός (NaN, διπλότυπα, HTML/περίεργοι χαρακτήρες) | `clean_dataframe()` |
| Επεξεργασία κειμένου (lowercase, stopwords, stemming) | `greek_nlp.py`, `add_nlp_columns()` |
| Νέες στήλες (year, month, αριθμός λέξεων, ποσοστά) | `add_feature_columns()` |
| Αριθμητικές αναλύσεις + γραφήματα | `charts/06*` |
| WordCloud, Top-15, bigrams | `charts/07*` |
| Ημερομηνία ως index + `resample()` | `ts = df.set_index("date")` |
| Sentiment (polarity, sentiment) | `sentiment_scores()` |
| Sentiment στον χρόνο | `charts/10*` |
| Similarity (CountVectorizer + cosine + heatmap) | `count_vectorize()`, `charts/11a` |

## Σημείωση για το μέγεθος δείγματος

Η εκφώνηση αναφέρει ≥500 «άρθρα». Εδώ αναλύονται 155 βίντεο (όσα υπάρχουν στο
δείγμα). Ο κώδικας είναι πλήρως επαναχρησιμοποιήσιμος: εκτελώντας ξανά το
`tiktok_transcribe.py` σε περισσότερα/άλλα προφίλ, ο αριθμός αυξάνεται χωρίς
αλλαγή στην ανάλυση.
