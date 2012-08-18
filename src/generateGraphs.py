#!/opt/local/bin/python

import numpy as np
import matplotlib.pyplot as plt

width = .5
data = (20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 20, 35, 30, 35, 27, 12,22,23,24,54,56 )
labels = ('(1) AIDS', '(2) AIDS with TB', '(3) Anemia', '(4) Asthma', '(5) Bite of Venomous Animal', '(6) Breast Cancer', '(7) Cervical Cancer', '(8) Cirrhosis', '(9) Colorectal Cancer', '(10) COPD', '(11) Diabetes with Coma', '(12) Diabetes with Renal Failure', '(13) Diabetes with Skin Infection/Sepsis', '(14) Diarrhea/Dysentery', '(15) Drowning', '(16) Epilepsy', '(17) Esophageal Cancer', '(18) Falls', '(19) Fires', '(20) Hemorrhage', '(21) Homicide', '(22) Hypertensive Disorder', '(23) IHD ? Acute Myocardial Infarction', '(24) IHD ? Congestive Heart Failure', '(25) Inflammatory Heart Disease', '(26) Leukemia', '(27) Lung Cancer', '(28) Lymphomas', '(29) Malaria', '(30) Other Cancers', '(31) Other Cardiovascular Diseases', '(32) Other Digestive Diseases', '(33) Other Infectious Diseases', '(34) Other Injuries', '(35) Other Non-communicable Diseases', '(36) Other Pregnancy-Related Deaths', '(37) Pneumonia', '(38) Poisonings', '(39) Prostate Cancer', '(40) Renal Failure', '(41) Road Traffic', '(42) Sepsis', '(43) Stomach Cancer', '(44) Stroke', '(45) Suicide', '(46) TB')

plt.bar(range(1,len(data)+1),data, width)
plt.ylabel('CSMF')
plt.title('CSMF for Adult in Bohol by Cause')

plt.xticks(range(1,len(labels)+1), labels, rotation=90)
plt.tick_params(axis='both', which='major', labelsize=7)

plt.savefig('barchart.png', dpi=200,bbox_inches='tight', pad_inches=.25)
plt.show()

