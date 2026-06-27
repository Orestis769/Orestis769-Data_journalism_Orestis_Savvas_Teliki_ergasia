# -*- coding: utf-8 -*-
"""Δημιουργία του τελικού άρθρου (PDF) με ενσωματωμένα γραφήματα — reportlab."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "charts")

# --- Ελληνική γραμματοσειρά ---
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], fontName="DejaVu-Bold", fontSize=19, leading=23, spaceAfter=6, textColor=colors.HexColor("#0d3b66"))
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="DejaVu", fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=14)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="DejaVu-Bold", fontSize=13, leading=16, spaceBefore=12, spaceAfter=5, textColor=colors.HexColor("#0d3b66"))
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontName="DejaVu", fontSize=10.5, leading=15.5, alignment=TA_JUSTIFY, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=styles["Normal"], fontName="DejaVu", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=12)

AUTHOR = "Σάββας Ορέστης"
EMAIL = "orestissavas@gmail.com"

def fig(name, w=15.5):
    p = os.path.join(CH, name)
    from PIL import Image as PImage
    iw, ih = PImage.open(p).size
    width = w * cm
    height = width * ih / iw
    return Image(p, width=width, height=height)

def P(t): return Paragraph(t, BODY)

story = []
story.append(Paragraph("Ο πολιτικός λόγος στο TikTok: Ανάλυση 155 βίντεο του Κυριάκου Μητσοτάκη", H1))
story.append(Paragraph(f"{AUTHOR} &nbsp;({EMAIL})<br/>ΕΔΔΕ2 – Ανάλυση Μεγάλων Δεδομένων μέσω της Γλώσσας Python", SUB))

story.append(Paragraph("Εισαγωγή και δεδομένα", H2))
story.append(P(
 "Η παρούσα εργασία μελετά την ψηφιακή πολιτική επικοινωνία στην Ελλάδα μέσα από ένα σύγχρονο "
 "κανάλι: τον επίσημο λογαριασμό του πρωθυπουργού Κυριάκου Μητσοτάκη στο TikTok "
 "(@kyriakosmitsotakis_). Το TikTok έχει εξελιχθεί σε βασικό εργαλείο άμεσης επικοινωνίας με το "
 "κοινό, ιδίως τους νεότερους ψηφοφόρους, και αποτελεί ένα ιδιαίτερα ενδιαφέρον πεδίο για την "
 "ανάλυση μεγάλων δεδομένων ελληνικής ειδησεογραφικής και πολιτικής φύσης. Το σύνολο δεδομένων "
 "δημιουργήθηκε με τεχνικές εξόρυξης από το διαδίκτυο (web scraping): κατέβηκε ο ήχος των δημόσιων "
 "βίντεο με το yt-dlp και στη συνέχεια κάθε βίντεο απομαγνητοφωνήθηκε τοπικά στα ελληνικά με το "
 "μοντέλο τεχνητής νοημοσύνης Whisper. Έτσι προέκυψαν 161 απομαγνητοφωνήσεις, οι οποίες μετά τον "
 "καθαρισμό κατέληξαν σε 155 έγκυρες εγγραφές που καλύπτουν την περίοδο Μαΐου 2022 έως Μαΐου 2026. "
 "Κάθε εγγραφή συνοδεύεται από πλήρη μεταδεδομένα αλληλεπίδρασης (προβολές, like, σχόλια, "
 "κοινοποιήσεις, αποθηκεύσεις, διάρκεια και ημερομηνία ανάρτησης), τα οποία επιτρέπουν τόσο "
 "ποσοτική όσο και κειμενική ανάλυση."
))
story.append(P(
 "Η επεξεργασία έγινε εξ ολοκλήρου σε Python. Τα δεδομένα εισήχθησαν σε pandas DataFrame, "
 "καθαρίστηκαν από κενές και ελλιπείς εγγραφές (NaN, πολύ μικρά κείμενα, διπλότυπα) και "
 "εμπλουτίστηκαν με νέες παραμέτρους-στήλες όπως ο μήνας, το έτος, το τρίμηνο, ο δείκτης "
 "αλληλεπίδρασης (engagement) και το ποσοστό engagement επί των προβολών. Για την επεξεργασία του "
 "κειμένου αφαιρέθηκαν τα ελληνικά stopwords και εφαρμόστηκε απλός stemmer για την προσέγγιση της "
 "λημματοποίησης."
))

story.append(Paragraph("Τι λέει ο λόγος: λέξεις, διγράμματα και θεματολογία", H2))
story.append(P(
 "Η ανάλυση συχνότητας λέξεων αποκαλύπτει με σαφήνεια τη θεματική ταυτότητα του λογαριασμού. Στο "
 "νέφος λέξεων (wordcloud) και στο διάγραμμα των 15 πιο συχνών λέξεων κυριαρχούν όροι όπως «ευρώ», "
 "«σήμερα», «πρώτη», «εργασίας», «πρόγραμμα», «νέους» και «Ελλάδα». Πρόκειται για το λεξιλόγιο της "
 "θετικής εξαγγελίας: ανακοινώσεις μέτρων («από σήμερα…»), οικονομικά μεγέθη σε ευρώ, και έμφαση "
 "στην εργασία, στους νέους και στα κρατικά προγράμματα. Τα πιο συχνά διγράμματα (bigrams) "
 "επιβεβαιώνουν την εικόνα, αναδεικνύοντας σταθερές εκφράσεις γύρω από τον κατώτατο μισθό, τις "
 "θέσεις εργασίας και τα εθνικά προγράμματα."
))
story.append(fig("07a_wordcloud.png", 14))
story.append(Paragraph("Εικόνα 1. Νέφος λέξεων (wordcloud) από το σύνολο των απομαγνητοφωνήσεων.", CAP))
story.append(fig("07b_top15_words.png", 13))
story.append(Paragraph("Εικόνα 2. Οι 15 πιο συχνές λέξεις μετά την αφαίρεση stopwords.", CAP))

story.append(Paragraph("Αριθμητική ανάλυση: προβολές, αλληλεπίδραση και συσχετίσεις", H2))
story.append(P(
 "Σε επίπεδο απήχησης, τα 155 βίντεο συγκέντρωσαν συνολικά πάνω από 123 εκατομμύρια προβολές, με "
 "μέσο όρο περίπου 796.000 και διάμεσο 540.000 προβολές ανά βίντεο — ένδειξη ότι λίγες ιδιαίτερα "
 "ιξώδεις (viral) αναρτήσεις τραβούν τον μέσο όρο προς τα πάνω. Το πιο δημοφιλές βίντεο, με τίτλο "
 "«Γιατί άνοιξε TikTok;», ξεπέρασε τα 4,2 εκατομμύρια προβολές. Ο πίνακας συσχετίσεων (Εικόνα 3) "
 "δείχνει πολύ ισχυρή θετική συσχέτιση μεταξύ προβολών και like (r≈0,95), κάτι αναμενόμενο, ενώ η "
 "διάρκεια του βίντεο συσχετίζεται ελαφρώς αρνητικά με τις προβολές (r≈-0,15): τα πιο σύντομα "
 "βίντεο τείνουν να αποδίδουν καλύτερα, σε συμφωνία με τη λογική της πλατφόρμας. Το μέσο ποσοστό "
 "engagement διαμορφώθηκε στο 4,5% των προβολών."
))
story.append(fig("06a_correlation.png", 12))
story.append(Paragraph("Εικόνα 3. Πίνακας συσχέτισης (Pearson) των αριθμητικών μεταβλητών.", CAP))
story.append(fig("06b_monthly_views.png", 15))
story.append(Paragraph("Εικόνα 4. Μηνιαία εξέλιξη του μέσου όρου προβολών και like (resample).", CAP))

story.append(Paragraph("Χρονοσειρές και ένταση παραγωγής", H2))
story.append(P(
 "Αξιοποιώντας την ημερομηνία ως δείκτη (index) του DataFrame και τη συνάρτηση resample(), "
 "μελετήσαμε την εξέλιξη στον χρόνο. Η παραγωγή περιεχομένου δεν είναι ομοιόμορφη: το 2023 "
 "καταγράφεται η εντονότερη δραστηριότητα (70 βίντεο), προφανώς λόγω της προεκλογικής περιόδου των "
 "βουλευτικών εκλογών, ενώ ακολουθούν το 2025 (38 βίντεο) και το 2022 (18). Η μηνιαία και "
 "τριμηνιαία ομαδοποίηση των προβολών αναδεικνύει περιόδους υψηλής απήχησης που συμπίπτουν με "
 "πολιτικά κομβικά γεγονότα."
))

story.append(Paragraph("Πολικότητα και συναίσθημα", H2))
story.append(P(
 "Για κάθε κείμενο υπολογίστηκε η πολικότητα (θετική–αρνητική) με λεξικό συναισθήματος ελληνικών "
 "λέξεων και απλό χειρισμό άρνησης, και αποθηκεύτηκε σε νέες στήλες μαζί με το κυρίαρχο συναίσθημα. "
 "Τα αποτελέσματα είναι χαρακτηριστικά του πολιτικού αυτο-προβαλλόμενου λόγου: το 54,8% των βίντεο "
 "είναι θετικά, το 31,0% ουδέτερα και μόλις το 14,2% αρνητικά, με μέση πολικότητα +0,38. Πρόκειται "
 "για επικοινωνία προσανατολισμένη στην αισιοδοξία, στα επιτεύγματα και στις θετικές εξαγγελίες. "
 "Η τριμηνιαία χρονοσειρά της πολικότητας (Εικόνα 6) παραμένει σχεδόν πάντα σε θετικό έδαφος, με "
 "κορύφωση το 2024 (+0,59) και πιο συγκρατημένο τόνο το 2026 (+0,26)."
))
story.append(fig("10c_sentiment_dist.png", 10))
story.append(Paragraph("Εικόνα 5. Κατανομή της πολικότητας των βίντεο (θετικά / ουδέτερα / αρνητικά).", CAP))
story.append(fig("10b_polarity_quarterly.png", 15))
story.append(Paragraph("Εικόνα 6. Μέση πολικότητα ανά τρίμηνο (resample 'QE').", CAP))

story.append(Paragraph("Ομοιότητα κειμένων", H2))
story.append(P(
 "Τέλος, με διανυσματοποίηση των κειμένων (CountVectorizer) και υπολογισμό της ομοιότητας συνημιτόνου "
 "(cosine similarity) εντοπίσαμε βίντεο με κοινή θεματολογία. Τα πιο όμοια ζεύγη αφορούν "
 "επαναλαμβανόμενες ανακοινώσεις για τον κατώτατο μισθό (ομοιότητα 0,71) και για το εθνικό "
 "διαστημικό πρόγραμμα δορυφόρων (0,71). Ο θερμικός χάρτης (heatmap) της Εικόνας 7 αποτυπώνει "
 "οπτικά αυτές τις θεματικές «γειτονιές»: η φωτεινή διαγώνιος αντιστοιχεί στην ταύτιση κάθε βίντεο "
 "με τον εαυτό του, ενώ τα διάσπαρτα φωτεινά σημεία εκτός διαγωνίου δείχνουν επαναλαμβανόμενα μοτίβα "
 "μηνυμάτων."
))
story.append(fig("11a_cosine_heatmap.png", 12))
story.append(Paragraph("Εικόνα 7. Heatmap ομοιότητας συνημιτόνου σε δείγμα 40 βίντεο.", CAP))

story.append(Paragraph("Συμπεράσματα", H2))
story.append(P(
 "Η ανάλυση 155 βίντεο TikTok δείχνει μια συνεκτική στρατηγική ψηφιακής επικοινωνίας: σύντομα βίντεο, "
 "έντονα θετικός τόνος, σταθερή εστίαση στην οικονομία, στην εργασία και στους νέους, και κορύφωση "
 "της παραγωγής σε προεκλογικές περιόδους. Η συντριπτική κυριαρχία θετικού περιεχομένου και η σχεδόν "
 "απουσία αρνητικού λόγου επιβεβαιώνουν ότι το κανάλι λειτουργεί ως εργαλείο προβολής έργου και "
 "εξαγγελιών παρά ως χώρος αντιπαράθεσης. Μεθοδολογικά, η εργασία κάλυψε ολόκληρο τον κύκλο της "
 "ανάλυσης μεγάλων δεδομένων — από το scraping και τον καθαρισμό μέχρι τη NLP επεξεργασία, τις "
 "χρονοσειρές, την ανάλυση συναισθήματος και την ομοιότητα κειμένων — αναδεικνύοντας τη δύναμη της "
 "Python στην εξαγωγή νοήματος από μη δομημένο ελληνικό κείμενο."
))
story.append(Spacer(1, 6))
story.append(Paragraph(f"Συγγραφέας: {AUTHOR} — {EMAIL}", CAP))

doc = SimpleDocTemplate(os.path.join(HERE, "Savvas_teliki_ergasia.pdf"), pagesize=A4,
                        topMargin=1.6*cm, bottomMargin=1.4*cm,
                        leftMargin=1.8*cm, rightMargin=1.8*cm,
                        title="Ο πολιτικός λόγος στο TikTok", author=AUTHOR)
doc.build(story)
print("PDF created.")

# Έλεγχος πλήθους λέξεων του άρθρου
import re
text = " ".join(p.text for p in story if hasattr(p, "text"))
text = re.sub(r"<[^>]+>", " ", text)
print("Λέξεις άρθρου (περ.):", len(text.split()))
