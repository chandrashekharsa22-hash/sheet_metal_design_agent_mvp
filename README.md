# Sheet Metal Design Agent — MVP v0.1

A local Streamlit application for preliminary sheet-metal bend calculations and configurable rule screening.

## Included
- Bend allowance (BA)
- Outside setback (OSSB)
- Bend deduction (BD)
- Estimated flat length for a single bend between two outside flange dimensions
- Configurable R/T, minimum flange, rough V-die flange, and hole/slot proximity checks
- CSV downloads for calculation and review reports

## Run on Windows
1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Extract this ZIP.
3. Open Command Prompt in the extracted folder.
4. Run:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```
5. The app opens in your browser, normally at http://localhost:8501.

## Calculation basis
- BA = theta_rad * (R + K*T)
- OSSB = (R + T) * tan(theta/2)
- BD = 2*OSSB - BA
- Flat length = outside flange A + outside flange B - BD

The angle is the bend rotation angle (e.g. 90 degrees). The flat-length formula assumes outside flange dimensions measured to the theoretical sharp corner (outside mold line).

## Engineering limitations
This is an MVP, not a certified engineering product. K-factor and bend results depend on material, temper, grain direction, tooling, process, and the CAD/shop convention. The V-die and hole-clearance rules are rough screening checks only. Validate all results against material-specific bend tables, tooling data, company procedures, and verified CAD flat patterns before fabrication.

## Suggested next versions
1. Multi-bend flat-length calculator with per-bend parameters.
2. Material/thickness bend tables calibrated to your press-brake tooling.
3. DXF/DWG geometry import and drawing checks.
4. SolidWorks/Inventor integration.
5. AI chat interface that explains calculations and retrieves approved company rules.
6. User roles, audit log, revision control, and controlled engineering approval workflow.
