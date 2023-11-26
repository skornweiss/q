---
type: Lab Review & Consultation Note
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

apob: 60
apob_goal:
baseline_apob: 60
lp(a):
baseline_lp(a):
lpa_date:
lpa_source:
apoe: 
mthfr:
fhx_ascvd:
smoking_status:
bp_status:
mesa_10:

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
prostate_fhx:

ast: 30
alt: 35
tbili: 0.9

hgb: 16.7
ferritin: 138
egfr: 116
vitd: 75.6

oq_date:
oq_result:

cac:
cac_date:
ccta_date:
ccta_findings:

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

neuro_fhx:
neuro_image_findings:
neuro_plan:

last_colo_endo:
last_colo_endo_findings:
next_colo_endo

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
eag:116
---

[%type]
Document Date: [%date]
Call Date: [%call_date]
Patient: [%patient]

*This was a telehealth consultation for [%patient] with [%participants].*

We reviewed the following documents: [%documents]. The labs discussed herein unless otherwise noted were drawn on [%current_lab_date].

[%patient] is a [%age] year old [%gender] who joined our practice in [%date_joined]. [%nickname] is in year [%years_in].

Since your last visit, [%changes].

---

Your last DEXA was done on [%dexa_date] and revealed an ALMI of [%almi] kg/m^2. VAT was measured at [%vat] g. BMD was [%bmd].

Last CPET was done on [%cpet_date] and revealed a VO2 max of [%vo2max] mL/kg/min.

Next, we moved on to discussing cardiovascular risk.

Your 10-year MESA risk for MACE is [%mesa_10]%. Relevant family history includes [%ascvd_fhx]. You're a [%smoking_status]. You are [%bp_status].

With respect to lipids, your baseline apoB is [%baseline_apob] and your baseline Lp(a) is [%baseline_lp(a)]. Your apoB is currently [%apob] mg/dL on [%lipid_therapy]. Our goal is an apoB below [%apob_goal] mg/dL.

Last Ω3 index was [%oq_result] ([%oq_date]) on [%n3fa_therapy]. Goal is at least 10%.

Our last blood pressure log was obtained on [%bp_log_date] and revealed [%bp_log_results]. You are currently taking [%bp_therapy] for blood pressure management.

A1c is [%a1c]% and insulin is [%insulin] µIU/mL. Your most recent CGM data from [%cgm_date_range] revealed an average glucose of [%cgm_avg] mg/dL with peaks of [%cgm_peaks] mg/dL and a standard deviation of [%cgm_std] mg/dL.

HsCRP is [%hscrp] mg/L. Uric acid is [%uric_acid] mg/dL on [%allopurinol_dose] allopurinol. Homocysteine is [%homocysteine] µmol/L on [%homocysteine_therapy].

TSH is [%tsh] µIU/mL, fT4 is [%ft4] ng/dL, and fT3 is [%ft3] pg/mL on [%thyroid_therapy].

Sex hormones are as follows on [%hormone_therapy].
- Estradiol: [%e2] pg/mL
- FSH: [%fsh] mIU/mL
- LH: [%lh] mIU/mL
- SHBG: [%shbg] nmol/L
- Testosterone: [%total_t] ng/dL
- Free Testosterone: [%free_t] ng/dL

PSA is [%psa] with a [%psa_velocity] ([%psa_velocity_date]) and density of [%psa_density] based on a volume of [%prostate_volume] from [%prostate_volume_source] ([%prostate_volume_date]). First degree relatives with prostate cancer: [%prostate_fhx].

AST is [%ast] U/L and ALT is [%alt] U/L. Total bilirubin is [%tbili] mg/dL. EGFR by Cystatin-C is [%egfr] ml/min/1.73m^2. Hemoglobin is [%hgb] mg/dL and ferritin is [%ferritin] ng/mL. 

Vitamin D is [%vitd] ng/mL on [%vitd_sup].

Regarding your risk for neurodegenrative disease, your ApoE genotype is: [%apoe]. Your family history is relevant for [%neuro_fhx]. Your cognitive tests have revealed [%cog_test_findings] ([%last_cog_test]), and your imaging reveals [%neuro_image_findings]. You're currently on the following risk reduction plan: [%neuro_plan].

|Test|Last|Findings|Next|
|:---|:---|:---|:---|
|Colo/endo|[%last_colo_endo]|[%last_colo_endo_findings]|[%next_coloendo]|
|Prenuvo|[%last_prenuvo]|[%last_prenuvo_findings]|[%next_prenuvo]|
|Grail|[%last_grail]|[%last_grail_findings]|[%next_grail]|
|FBSE|[%last_skin]|[%last_skin_findings]|[%next_skin]|
|Eye|[%last_ophtho]|[%last_ophtho_findings]|[%next_ophtho]|
|Dental|[%last_dental]|[%last_dental_findings]|[%next_dental]|
|Cog|[%last_cog_test]|[%cog_test_findings]|[%next_cog]|

We agreed on the following plan:



---

[%date]


This visit utilized a secure interactive audio-video Zoom telehealth platform. The patient confirmed their current location is within one of the following states CA, NY, HI, TX, CO, CT, IL, FL, WA, GA, MA, MD, NJ, TN, WI, OR, AZ, VI, and that they consent to having a telehealth visit acknowledging the risks of technical difficulties, security concerns, and the potential need for an in person exam in the future depending on patient needs.


Patient Tasks


Physician Tasks


Coordinator Tasks
- Send updated medication/supplement list

Medication changes


Supplement changes


Referrals


Medical records


Next Labs
- Date:
- Standard
- PSA
- OQ
- Galleri
- Other:

Next Visit
- Interval:
- Duration of call:
- PA: