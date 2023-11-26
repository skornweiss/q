---
type:
patient:
nickname:
date:
age:
gender:
date_joined:
years_in:
documents:
call_date:
participants:
last_lab_date:
current_lab_date:

changes:

bp_therapy:
lipid_therapy:
homocysteine_therapy:
n3fa_therapy:
allopurinol_dose:
thyroid_therapy:
hormone_therapy:
metabolic_meds:
vitd_sup:
rapamycin_status:
5ari_status:

ascvd_fhx:
prostate_fhx:
neuro_fhx:

cac:
cac_date:
ccta_date:
ccta_findings:

neuro_image_findings:
neuro_plan:

apob: 60
apob_goal:
baseline_apob: 60
ontx_lp(a):
baseline_lp(a):
lpa_date:
lpa_source:
apoe: 
smoking_status:
bp_status:

oq_result:
oq_date:

bp_log_results:
bp_log_date:

exercise_team:
exercise_focus:
dexa_date:
almi:
vat:
bmd:
cpet_date:
vo2max:

sleep_therapy:
sleep_score:
total_sleep:
rem:
deep:

nutrition_team_involvement:

cgm_avg:
cgm_peaks:
cgm_std:
cgm_date_range:

last_colo_endo:
last_colo_endo_findings:
next_colo_endo:

last_prenuvo:
last_prenuvo_findings:
next_prenuvo:

last_grail:
last_grail_findings:
next_grail:

last_skin:
last_skin_findings:
next_skin:

last_ophtho:
last_ophtho_findings:
next_ophtho:

last_dental:
last_dental_findings:
next_dental:

last_cog_test:
cog_test_findings:
next_cog_test:

homocysteine: 8.4
hscrp: 0.68
uric_acid: 4
insulin: 3.8
a1c: 5.7

tsh: 1.4
ft4: 1.19
ft3: 3.4

e2: 21.2
fsh: 2.5
lh: 2.4
shbg: 49.9
total_t: 551.2
free_t: 8.46

psa:  
psa_date:
psa_velocity: 
psa_velocity_date:
prostate_volume:
prostate_volume_source:
prostate_volume_date:
psa_density:

ast: 30
alt: 35
tbili: 0.9

hgb: 16.7
ferritin: 138
egfr: 116
vitd: 75.6
eag:116
---

<style>body{font-family:'avenir'; font-size:1.4em;} p{margin-top:20px;}</style>

**‌[%type] for [%patient] on [%call_date]**
- [%nickname] joined [%date_joined] and is in year [%years_in]
- Documents: [%documents]
- Participants: [%participants]
- Lab Draw Date: [%current_lab_date]

**Questions for Peter**

**Changes since last labs** ([%last_lab_date])
[%changes]

**Proposed Plan**

**Lipids**
- ApoB is [%apob] mg/dL
	- Lipid Tx: [%lipid_therapy]

**ASCVD Risk**
- CAC: [%cac] ([%cac_date])
- CCTA: [%ccta_findings] ([%ccta_date])
- Baseline apoB: [%baseline_apob]
- Baseline Lp(a): [%baseline_lp(a)] ([%base_lpa_date])
	- On-therapy Lp(a): [%lp(a)] ([%lpa_date])
- Omega-3 is [%oq_result] % ([%oq_date])
	- [%n3fa_therapy]
- Blood Pressure: [%bp_status]
	- Antihypertensives: [%bp_therapy]
	- Last BP Log | ([%bp_log_date]) | [%bp_log_results]
- Fhx: [%ascvd_fhx]
- Smoking: [%smoking_status]

**Metabolic**
- Molecules: [%metabolic_meds]
- A1c: [%a1c]%
- Fasting insulin: [%insulin] µIU/mL
- Uric acid: [%uric_acid] mg/dL
	- [%allopurinol_dose] allopurinol
- Homocysteine: [%homocysteine]
	- [%homocysteine_therapy]
- hsCRP: [%hscrp]
- CGM ([%cgm_date_range]): [%cgm_avg] +/- [%cgm_std] with peaks of [%cgm_peaks]

**VitD**
- VitD is [%vitd]
	- [%vitd_sup]

**Liver**
- AST/ALT: [%ast]/[%alt]

**Renal**
- eGFR/Cystatin C: [%egfr]

**Thyroid**
- Thyroid therapy: [%thyroid_therapy]
- TSH: [%tsh]
- FT4: [%ft4]
- FT3: [%ft3]

**Sex Hormones**
- TRT/HRT: [%hormone_therapy]
- E2: [%e2]
- FSH: [%fsh]
- LH: [%lh]
- SHBG [%shbg]
- Testosterone: [%total_t]
- Free T: [%free_t]

**PSA**
- 5ari status: [%5ari_status]
- PSA: [%psa]
	- Corrected PSA:
- Velocity: [%psa_velocity] ([%psa_velocity_date])
- PSA Density: [%psa_density]
- Prostate volume: [%prostate_volume] from [%prostate_volume_source] on [%prostate_volume_date]

**Heme**
- Hb: [%hgb]
- Ferritin: [%ferritin]

**Exercise**
- Team: [%exercise_team]
- Focus: [%exercise_focus]
- DEXA [%dexa_date]
	- ALMI: [%almi]
	- VAT: [%vat]
	- BMD: [%bmd]
- CPET [%cpet_date]
	- VO2Max: [%vo2max]

**Nutrition**
- Nutrition Team: [%nutrition_team_involvement]

**Neuro**
- ApoE: [%apoe]
- Risk factors
	- [%neuro_fhx]
	- [%neuro_image_findings]
- Plan: [%neuro_plan]

**Sleep**
- Therapy: [%sleep_therapy]
- OURA
	- Score: [%sleep_score]
	- [%total_sleep] total sleep, [%rem] REM, [%deep] deep

**Geroprotective Agents**
- Rapamycin: [%rapamycin_status]

**Screening**
|Test|Last|Findings|Next|
|:----|:----|:---|:---|
|Colo/endo|[%last_colo_endo]|[%last_colo_endo_findings]|[%next_coloendo]|
|Prenuvo|[%last_prenuvo]|[%last_prenuvo_findings]|[%next_prenuvo]|
|Grail|[%last_grail]|[%last_grail_findings]|[%next_grail]|
|FBSE|[%last_skin]|[%last_skin_findings]|[%next_skin]|
|Eye|[%last_ophtho]|[%last_ophtho_findings]|[%next_ophtho]|
|Dental|[%last_dental]|[%last_dental_findings]|[%next_dental]|
|Cog|[%last_cog_test]|[%cog_test_findings]|[%next_cog]|

