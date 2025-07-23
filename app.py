import streamlit as st
import lasio
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

st.set_page_config(page_title="Well Log Analyzer", layout="wide")
st.title("🛢️ Well Log Analyzer")

def normalize_columns(df):
    """Normalizes DataFrame column names to uppercase and strips whitespace."""
    df.columns = df.columns.str.upper().str.strip()
    return df

def find_column(df, possible_names):
    """
    Finds a column in the DataFrame based on a list of possible names.
    Case-insensitive and strips whitespace.
    """
    for name in possible_names:
        for col in df.columns:
            if col.strip().upper() == name.strip().upper():
                return col
    return None

uploaded_file = st.file_uploader("📤 Upload a LAS File", type=["las"])

if uploaded_file is not None:
    try:
        raw_file_content = uploaded_file.getvalue().decode("utf-8")
        cleaned_file_content = raw_file_content.replace('\xa0', ' ')
        stringio = io.StringIO(cleaned_file_content)
        las = lasio.read(stringio)

    except Exception as e:
        st.error(f"❌ Failed to read LAS file: {e}")
    else:
        df = las.df().dropna()
        df = normalize_columns(df)

        if df.empty:
            st.warning("⚠️ LAS file loaded, but contains no usable curve data.")
        else:
            st.success(f"✔️ Loaded LAS with {df.shape[0]} rows and {df.shape[1]} logs")

            # Display Curve Information
            with st.expander("📄 Curve Info"):
                for curve in las.curves:
                    st.write(f"- **{curve.mnemonic.strip()}**: {curve.unit} — {curve.descr}")

            # Display Raw Data Preview
            st.subheader("🧾 Raw Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # --- Log Plotting ---
            st.subheader("📈 Select Logs to Plot")
            default_logs = [log for log in ["RESD", "DT", "SP"] if log in df.columns.tolist()]
            selected_logs = st.multiselect("Choose logs", df.columns.tolist(), default=default_logs)

            if selected_logs:
                fig, ax = plt.subplots(figsize=(12, 6))
                for log in selected_logs:
                    ax.plot(df[log], df.index, label=log)
                ax.invert_yaxis()
                ax.set_xlabel("Log Value")
                ax.set_ylabel("Depth")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
            else:
                st.info("ℹ️ Select at least one log to display.")

            # --- Porosity Calculation ---
            st.subheader("🧮 Porosity Calculation")
            matrix_density = st.number_input("Matrix Density (ρma)", value=2.65)
            fluid_density = st.number_input("Fluid Density (ρf)", value=1.0)

            rhob_col = find_column(df, ["RHOB", "RHOP"])
            if rhob_col:
                df["Density Porosity"] = (matrix_density - df[rhob_col]) / (matrix_density - fluid_density)
                st.line_chart(df["Density Porosity"])
                st.success("✅ Porosity calculated from RHOB.")
            else:
                st.warning("RHOB/RHOP curve not found.")

            # --- Hydrocarbon Zone Detection ---
            st.subheader("🛢️ Hydrocarbon Zone Detection")
            gr_col = find_column(df, ["GR"])
            nphi_col = find_column(df, ["NPHI", "NEUTRON"])

            gr_cutoff = st.slider("GR Cutoff (API)", 20, 150, 60)
            nphi_cutoff = st.slider("NPHI Cutoff", 0.0, 0.5, 0.2)

            if gr_col and nphi_col:
                df["PayZone"] = ((df[gr_col] < gr_cutoff) & (df[nphi_col] > nphi_cutoff)).astype(int)
                st.line_chart(df["PayZone"])
                st.success("✅ Pay zones flagged.")
            else:
                st.warning("GR or NPHI curve missing for pay zone detection.")

            # --- Triple Combo Track Plot ---
            st.subheader("📊 Triple Track Well Log Plot")
            resistivity_col = find_column(df, ["RESD", "RT", "RESISTIVITY"])

            if gr_col and rhob_col and nphi_col and resistivity_col:
                # Calculate VSH (Volume of Shale) based on GR
                # Assuming GR_clean = 30 and GR_shale = 100 for VSH calculation
                df["VSH"] = (df[gr_col] - 30) / (100 - 30)
                df["VSH"] = df["VSH"].clip(0, 1) # Clip values between 0 and 1
                depth = df.index

                fig, axs = plt.subplots(1, 3, figsize=(14, 10), sharey=True)
                fig.subplots_adjust(wspace=0.3) # Adjust spacing between subplots

                # Track 1: Lithology (GR and VSH)
                axs[0].plot(df[gr_col], depth, color='green', label='GR')
                axs[0].fill_betweenx(depth, 0, df["VSH"] * 150, color="lime", alpha=0.4, label="VSH (Scaled)") # Scale VSH for visual representation
                axs[0].invert_yaxis() # Invert Y-axis for depth
                axs[0].set_xlim(0, 150) # Typical GR range
                axs[0].set_xlabel("GR (GAPI) / VSH")
                axs[0].set_title("Track 1: Lithology")
                axs[0].grid(True)
                axs[0].legend()

                # Track 2: Resistivity (Logarithmic Scale)
                axs[1].semilogx(df[resistivity_col], depth, color='red', label=resistivity_col)
                axs[1].set_xlim(0.2, 2000) # Typical resistivity range (log scale)
                axs[1].set_xlabel("Resistivity (Ohm·m)")
                axs[1].set_title("Track 2: Resistivity")
                axs[1].grid(True)
                axs[1].legend()

                # Track 3: Porosity (RHOB and NPHI)
                axs[2].plot(df[rhob_col], depth, color='black', label='RHOB')
                axs[2].set_xlim(3.0, 1.8)  # RHOB typically from 1.8 to 3.0, inverted for logs
                axs[2].set_xlabel("RHOB (G/CC)") # Label for RHOB axis

                # Create a twin x-axis for NPHI
                ax3 = axs[2].twiny()
                ax3.plot(df[nphi_col], depth, color='blue', linestyle='--', label='NPHI')
                ax3.set_xlim(0.45, -0.15) # Typical NPHI range, inverted for porosity
                ax3.set_xlabel("NPHI (V/V)") # Label for NPHI axis

                axs[2].invert_yaxis()

                axs[2].set_title("Track 3: Porosity")
                axs[2].grid(True)

                # Combine legends from both axes
                lines, labels = axs[2].get_legend_handles_labels()
                lines2, labels2 = ax3.get_legend_handles_labels()
                axs[2].legend(lines + lines2, labels + labels2, loc='upper right')

                st.pyplot(fig)
            else:
                st.warning("❗ Missing one or more logs for triple combo track (GR, RHOB, NPHI, RESD).")

            # --- Export to Excel ---
            st.subheader("📤 Export Results")
            if st.button("Export to Excel"):
                if not os.path.exists("results"):
                    os.makedirs("results")
                df.reset_index(inplace=True)
                df.to_excel("results/well_analysis.xlsx", index=False)
                st.success("📁 Exported to 'results/well_analysis.xlsx'")
