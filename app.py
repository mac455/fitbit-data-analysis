import streamlit as st 
import pandas as pd 
import plotly.express as px 
import os 

st.set_page_config(page_title="Fitbit Data Analysis", layout="wide")

st.title("Fitbit Data Analysis")
st.header("Phase 1")
st.markdown("The objective this project to explore behavioural and exercise habits. These insights would guide the production of ML model for fitness professional to develop optimised and adaptive fitness plans")
# -- Compare ML Model --
tab1, tab2 = st.tabs(["Phase 1: RandomForest Regression & Gradient Boosting", "Base Gradient Boosting vs Tuned Gradient Boosting"])

with tab1: 
    st.markdown("The objective was to build a model able to accurately predict calories expenditure.")
    st.info("**Key Insight** : Both Model needed further tuning to improve RMSE.  \nSurprisingly, the RF model had a lower RMSE than GB model, meaning it was actually better at prediction compared to the GB model. This result is interesting as GB model work by correcting errors made by previous trees. As such, it should be theortically better than RF model which is based on an average of paralell predictions")
    # 1. Dynamically build the absolute path relative to THIS app.py file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    p1_path = os.path.join(script_dir, "data", "model_data.csv")
    
    # 2. Correctly use the path check in an IF statement
    if os.path.exists(p1_path):    
        df1 = pd.read_csv(p1_path)
        fig1 = px.bar(
            df1, x="Model", y="RMSE", text="RMSE", 
            title="Random Forest vs Gradient Boosting", 
            labels={"RMSE":"RMSE (Calories)"}, # Note: Fixed 'label' to 'labels'
            color="RMSE", color_continuous_scale="Oranges_r"
        )
        fig1.update_traces(texttemplate='%{text:.1f} cal') 
        fig1.update_layout(yaxis_range=[0,600], coloraxis_showscale=False, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

with tab2: 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    p2_path = os.path.join(script_dir, "data", "model_data_gradient.csv")

    st.markdown("Base Gradient Boosting vs Tuned Gradient Boosting")
    st.info("**Feature Engineering** : Developed a new feature `calories_intensity_ratio`.  \nThis feature provided context about the relationship between exercise intensity and calorie burn.  \nTuned Gradient Model model was able to accurately predict calorie burn with an RMSE of 25 calories")
    if os.path.exists(p2_path): 
        df2 = pd.read_csv(p2_path)
        fig2 = px.bar(df2, x="Model", y="RMSE", text="RMSE", 
                    title="Model Prediction Improvement", 
                    labels={"RMSE:" "RMSE(Calories)"}, 
                    color="RMSE", color_continuous_scale="Reds_r")
        fig2.update_traces(texttemplate='%{text:.1f} cal', textposition='outside')
        fig2.update_layout(yaxis_range=[0,300], coloraxis_showscale=False, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
import streamlit as st
import numpy as np


st.header("Phase 2")
st.markdown("Gradient boosting classifier for predicting if users will achieve their daily step")
st.markdown("Adjust the sliders to see how the Calorie Intensity Ratio changes the model's prediction context.")
tab_grad1, tab_grad2 = st.tabs(["GB Model v0", "GB Model v1"])
with tab_grad1: 
    st.info("**Input Features** `total_calories`, `total_intensity`, `avg_intensity`, `max_intensity`") 
    
    # 1. Main Metrics Row
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.metric(label="Accuracy", value="83.87%")
    with col_g2: 
        st.metric(label="Cross-Validation", value="Chronological Split")
    with col_g3:
        st.metric(label="Hyperparameters", value="GridSearchCV Optimized")

    st.markdown("---")
    
    # 2. Side-by-Side: Hyperparameters & Performance Report
    col_report_left, col_report_right = st.columns([1, 2])
    
    with col_report_left:
        st.markdown("###  Best Parameters")
        st.json({
            'learning_rate': 0.05, 
            'max_depth': 3, 
            'n_estimators': 50
        })

    with col_report_right:
        st.markdown("### Classification Report")
        # Raw string preserving the spaces for clean terminal look
        report_text = """
               precision    recall  f1-score   support

           0       0.87      0.90      0.88       124
           1       0.78      0.75      0.76        63

    accuracy                           0.84       187
    macro avg      0.83     0.82       0.82       187
    weighted avg   0.84     0.84       0.84         187
        """
        st.code(report_text, language="text")
    

with tab_grad2:
    st.info("**Input Features** `calorie_intesity_ratio`, `total_calories`, `total_intensity`, `avg_intensity`, `max_intensity`") 
    
    # 1. Main Metrics Row
    col_g1_1, col_g2_1, col_g3_1 = st.columns(3)
    with col_g1_1:
        st.metric(label="Accuracy", value="89.98%")
    with col_g2_1: 
        st.metric(label="Cross-Validation", value="Chronological Split")
    with col_g3_1:
        st.metric(label="Hyperparameters", value="GridSearchCV Optimized")

    st.markdown("---")
    
    # 2. Side-by-Side: Hyperparameters & Performance Report
    col_report_left_1, col_report_right_1 = st.columns([1, 2])
    
    with col_report_left_1:
        st.markdown("###  Best Parameters")
        st.json({
            'learning_rate': 0.01, 
            'max_depth': 5, 
            'n_estimators': 100
        })

    with col_report_right_1:
        st.markdown("### Classification Report")
        # Raw string preserving the spaces for clean terminal look
        report_text = """
            precision    recall  f1-score   support

        0       0.92      0.94      0.93       134
        1       0.84      0.79      0.82        53

accuracy                            0.90       187
macro avg       0.88      0.87      0.87       187
weighted avg    0.90      0.90      0.90       187
        """
        st.code(report_text, language="text")
st.info(
    "**Model Comparison: Feature Engineering Impact**  \n\n"
    "* **The Big Difference:** The first model used only raw data. This updated model includes a new feature: `Calorie_Intensity_Ratio`. This tells the model how efficiently you move per calorie burned.  \n"
    "* **Better Tuning:** The new feature allowed the model to use deeper trees (depth 5 instead of 3) and learn at a more precise pace (0.01 instead of 0.05).  \n\n"
    "**Result:** Overall prediction accuracy jumped from **83.87% to 89.84%**."
)
