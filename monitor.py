import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(layout="wide")
st.title("🔍 Real-Time Token Usage Monitor")

token_log_path  = "log_module/token_usage_log.csv"
time_log_path = "log_module/time_log.csv"

# Show warning if file doesn't exist yet
if not os.path.exists(token_log_path ):
    st.warning("Token log file not found. Waiting for agent to start...")
    time.sleep(3)  # Small delay before rechecking
    st.rerun()()

# Sidebar refresh control
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 2, 30, 2)

# Toggle for X-axis type
x_axis_mode = st.sidebar.radio(
    "X-axis mode", ["Timestamps", "Step Index"], index=1
)

# Main placeholders
input_output_chart_placeholder = st.empty()
cumulative_chart_placeholder = st.empty()
stats_placeholder = st.empty()
time_log_chart_placeholder = st.empty()

while True:
    try:
        df = pd.read_csv(token_log_path )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["cumulative_tokens"] = df["total_tokens"].cumsum()

        if x_axis_mode == "Timestamps":
            df_plot = df.set_index("timestamp")
        else:
            df["step"] = range(len(df))
            df_plot = df.set_index("step")

        # Input / Output tokens chart
        with input_output_chart_placeholder.container():
            st.subheader("Input and Output Tokens (LLM Assistant)")
            st.bar_chart(df_plot[["input_tokens","output_tokens"]], 
                         stack=False,
                         y_label="Nº Tokens")


        # Cumulative tokens line chart
        with cumulative_chart_placeholder.container():
            st.subheader("Cumulative Token Usage")
            st.line_chart(df_plot[["cumulative_tokens"]],
                          y_label="Nº Tokens (sum)")

        # Stats
        latest = df.iloc[-1]
        total = df["total_tokens"].sum()
        with stats_placeholder.container():
            st.markdown("### 📊 Latest Stats")
            st.write(f"**Last input tokens:** {latest['input_tokens']}")
            st.write(f"**Last output tokens:** {latest['output_tokens']}")
            st.write(f"**Cumulative tokens so far:** {int(total)}")
            
         # --- Time Log Visualization ---
        if os.path.exists(time_log_path):
            time_df = pd.read_csv(time_log_path)
            time_df["timestamp"] = pd.to_datetime(time_df["timestamp"])
            time_df["step"] = range(len(time_df))

            with time_log_chart_placeholder.container():
                st.subheader("⏱️ Step Timing Log")
                st.dataframe(time_df[["step", "label", "timestamp", "delta"]])

                # Optional: show a bar chart of step durations
                st.bar_chart(data=time_df.set_index("step")[["delta"]],
                             y_label="Duration (seconds)")


        time.sleep(refresh_interval)

    except Exception as e:
        st.error(f"Error reading token log: {e}")
        time.sleep(5)