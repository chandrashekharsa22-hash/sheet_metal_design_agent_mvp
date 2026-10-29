import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sheet Metal Design Agent", page_icon="📐", layout="wide")

st.title("📐 Sheet Metal Design Agent")
st.caption("MVP • Bend calculations, flat-length estimate, and configurable design-rule warnings")

st.warning(
    "Engineering note: This is a preliminary calculation assistant, not a substitute for "
    "material-specific bend tables, tooling manuals, validated CAD flat patterns, or an engineer's approval. "
    "Rules vary by material, temper, grain direction, tooling, and shop practice."
)

with st.sidebar:
    st.header("Calculation inputs")
    units = st.selectbox("Units", ["mm", "inch"])
    material = st.selectbox(
        "Material",
        ["Mild steel", "Stainless steel", "Aluminium", "Galvanized steel", "Other / custom"]
    )
    thickness = st.number_input(f"Sheet thickness ({units})", min_value=0.01, value=2.0 if units == "mm" else 0.08, step=0.1 if units == "mm" else 0.01, format="%.4f")
    radius = st.number_input(f"Inside bend radius ({units})", min_value=0.0, value=2.0 if units == "mm" else 0.08, step=0.1 if units == "mm" else 0.01, format="%.4f")
    angle = st.number_input("Bend angle (degrees)", min_value=0.1, max_value=180.0, value=90.0, step=1.0)
    k_factor = st.number_input("K-factor", min_value=0.0, max_value=1.0, value=0.33, step=0.01, format="%.3f")
    st.caption("Bend angle means the amount of material rotation, e.g. 90° for a right-angle bend.")
    st.divider()
    st.subheader("Outside flange dimensions")
    flange_a = st.number_input(f"Flange A outside dimension ({units})", min_value=0.0, value=40.0 if units == "mm" else 1.5, step=1.0 if units == "mm" else 0.1)
    flange_b = st.number_input(f"Flange B outside dimension ({units})", min_value=0.0, value=30.0 if units == "mm" else 1.0, step=1.0 if units == "mm" else 0.1)
    st.caption("Flat length assumes both flange dimensions are outside dimensions measured to the theoretical sharp corner (outside mold line).")
    st.divider()
    st.subheader("Optional rule checks")
    min_flange = st.number_input(f"Shop minimum flange length ({units})", min_value=0.0, value=0.0, step=1.0 if units == "mm" else 0.1)
    min_radius_ratio = st.number_input("Minimum preferred inside radius / thickness ratio", min_value=0.0, value=1.0, step=0.1)
    die_v = st.number_input(f"V-die opening ({units}; optional)", min_value=0.0, value=0.0, step=1.0 if units == "mm" else 0.1)
    hole_edge = st.number_input(f"Nearest hole/slot edge distance from bend line ({units}; optional)", min_value=0.0, value=0.0, step=1.0 if units == "mm" else 0.1)

# Calculations
theta = math.radians(angle)
ba = theta * (radius + k_factor * thickness)
ossb = (radius + thickness) * math.tan(theta / 2.0)
bd = 2.0 * ossb - ba
flat_length = flange_a + flange_b - bd
rt_ratio = radius / thickness if thickness else float("inf")

def fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bend allowance (BA)", f"{fmt(ba)} {units}")
c2.metric("Bend deduction (BD)", f"{fmt(bd)} {units}")
c3.metric("Outside setback (OSSB)", f"{fmt(ossb)} {units}")
c4.metric("Estimated flat length", f"{fmt(flat_length)} {units}")

st.subheader("Calculation details")
details = pd.DataFrame([
    ["Bend angle in radians", "θ = angle × π / 180", f"{theta:.6f} rad"],
    ["Bend allowance", "BA = θ × (R + K × T)", f"{fmt(ba)} {units}"],
    ["Outside setback", "OSSB = (R + T) × tan(θ / 2)", f"{fmt(ossb)} {units}"],
    ["Bend deduction", "BD = 2 × OSSB − BA", f"{fmt(bd)} {units}"],
    ["Flat length estimate", "Lflat = A + B − BD", f"{fmt(flat_length)} {units}"],
    ["Inside radius / thickness", "R/T", f"{fmt(rt_ratio)}"],
], columns=["Item", "Formula", "Result"])
st.dataframe(details, use_container_width=True, hide_index=True)

st.subheader("Design-rule review")
checks = []
def add_check(name, status, note):
    checks.append({"Check": name, "Status": status, "Finding": note})

if thickness <= 0:
    add_check("Thickness", "FAIL", "Thickness must be greater than zero.")
else:
    add_check("Thickness", "PASS", f"Positive thickness entered: {fmt(thickness)} {units}.")

if radius <= 0:
    add_check("Inside radius", "REVIEW", "Zero inside radius is generally not a realistic formed bend; confirm the geometry and process.")
elif rt_ratio < min_radius_ratio:
    add_check("Radius-to-thickness ratio", "REVIEW", f"R/T = {fmt(rt_ratio)}, below the configured preferred ratio of {fmt(min_radius_ratio)}. Confirm material-specific minimum radius.")
else:
    add_check("Radius-to-thickness ratio", "PASS", f"R/T = {fmt(rt_ratio)} meets the configured preferred ratio.")

if angle < 1 or angle > 179:
    add_check("Bend angle", "REVIEW", "Very small or near-flat bend angles may need special handling in the shop/CAD system.")
else:
    add_check("Bend angle", "PASS", f"{fmt(angle)}° is within the app's general calculation range.")

if min_flange > 0:
    shortest = min(flange_a, flange_b)
    if shortest < min_flange:
        add_check("Minimum flange length", "REVIEW", f"Shortest outside flange ({fmt(shortest)} {units}) is below your shop rule ({fmt(min_flange)} {units}).")
    else:
        add_check("Minimum flange length", "PASS", "Both entered outside flange dimensions meet the configured shop minimum.")
else:
    add_check("Minimum flange length", "NOT CHECKED", "Enter a shop-specific minimum to enable this check.")

if die_v > 0:
    # Approximate screening rule only; actual minimum flange depends on tooling and process.
    screening_min = die_v / 2.0 + thickness
    if min(flange_a, flange_b) < screening_min:
        add_check("V-die flange screening", "REVIEW", f"Shortest flange is below the rough screening estimate V/2 + T = {fmt(screening_min)} {units}. Verify with the actual press-brake tooling chart.")
    else:
        add_check("V-die flange screening", "PASS", f"Shortest flange meets the rough V/2 + T screening estimate ({fmt(screening_min)} {units}); verify with tooling data.")
else:
    add_check("V-die flange screening", "NOT CHECKED", "Enter V-die opening to run a rough screening check.")

if hole_edge > 0:
    screening_clearance = 2.0 * thickness + radius
    if hole_edge < screening_clearance:
        add_check("Hole/slot near bend", "REVIEW", f"Edge distance {fmt(hole_edge)} {units} is below the rough screening value R + 2T = {fmt(screening_clearance)} {units}. Check the shop's validated rule.")
    else:
        add_check("Hole/slot near bend", "PASS", f"Edge distance meets the rough screening value R + 2T = {fmt(screening_clearance)} {units}; verify against material/tooling practice.")
else:
    add_check("Hole/slot near bend", "NOT CHECKED", "Enter the nearest hole/slot edge distance to run a rough screening check.")

if flat_length <= 0:
    add_check("Flat length", "FAIL", "Calculated flat length is zero or negative; check flange dimensions, angle, radius, and K-factor.")
else:
    add_check("Flat length", "CALCULATED", "Estimate is based on the entered outside flange dimensions and a single bend.")

check_df = pd.DataFrame(checks)
st.dataframe(check_df, use_container_width=True, hide_index=True)

st.subheader("Download calculation report")
report = pd.DataFrame([
    ["Material", material],
    ["Units", units],
    ["Thickness", fmt(thickness)],
    ["Inside radius", fmt(radius)],
    ["Bend angle (degrees)", fmt(angle)],
    ["K-factor", fmt(k_factor)],
    ["Flange A outside dimension", fmt(flange_a)],
    ["Flange B outside dimension", fmt(flange_b)],
    ["Bend allowance", fmt(ba)],
    ["Outside setback", fmt(ossb)],
    ["Bend deduction", fmt(bd)],
    ["Estimated flat length", fmt(flat_length)],
    ["R/T ratio", fmt(rt_ratio)],
], columns=["Parameter", "Value"])
csv = report.to_csv(index=False).encode("utf-8")
st.download_button("Download calculation summary (CSV)", data=csv, file_name="sheet_metal_calculation_report.csv", mime="text/csv")
checks_csv = check_df.to_csv(index=False).encode("utf-8")
st.download_button("Download design-rule review (CSV)", data=checks_csv, file_name="sheet_metal_design_rule_review.csv", mime="text/csv")

with st.expander("Important assumptions and next development steps"):
    st.markdown("""
    **Current MVP scope**
    - One bend between two outside flange dimensions.
    - BA = θ × (R + K × T).
    - OSSB = (R + T) × tan(θ/2).
    - BD = 2 × OSSB − BA.
    - Flat length = flange A + flange B − BD.

    **Limitations**
    - K-factor must be calibrated to the actual material, thickness, radius, tooling, and process.
    - The V-die and hole-clearance checks are rough screening checks, not universal acceptance criteria.
    - This version does not yet import CAD geometry, generate DXF flat patterns, or validate multi-bend parts.
    - For production use, compare results against a validated bend table and actual press-brake/CAD outputs.
    """)

st.caption("Version 0.1 • Calculation assistant only • Review all outputs before manufacturing.")
