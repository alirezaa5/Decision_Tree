import os
import pandas as pd
import pyodbc
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.set_page_config(page_title="پیش‌بینی ثبت‌نام دانشجو", page_icon="🎓")
st.title("🎓 پیش‌بینی ثبت‌نام دانشجو")
st.write("اطلاعات از SQL Server خوانده می‌شود و مدل Decision Tree نتیجه ثبت‌نام را پیش‌بینی می‌کند.")

def read_database():
    server = os.getenv("SQL_SERVER", "localhost")
    database = os.getenv("SQL_DATABASE", "StudentEnrollmentDB")
    driver = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    connection_string = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;"
    )
    cn = pyodbc.connect(connection_string)
    students = pd.read_sql("SELECT * FROM dbo.vw_Student", cn)
    courses = pd.read_sql("SELECT * FROM dbo.vw_Course", cn)
    enrollments = pd.read_sql("SELECT * FROM dbo.vw_Enrollment", cn)
    cn.close()
    return students, courses, enrollments

try:
    students, courses, enrollments = read_database()
except Exception as exc:
    st.error("اتصال به دیتابیس برقرار نشد. فایل database.sql را اجرا و نام سرور را بررسی کنید.")
    st.code(str(exc))
    st.stop()

# ترکیب اطلاعات سه View برای ساخت داده آموزشی
data = enrollments.merge(students, on="StudentID").merge(courses, on="CourseID")
features = ["Age","Major","GPA","CompletedCredits","RelatedMajor","Credits","Capacity","Difficulty"]
X = data[features]
y = data["IsEnrolled"].astype(int)

if y.nunique() < 2:
    st.error("داده‌ها باید هم نمونه ثبت‌نام‌شده (1) و هم ثبت‌نام‌نشده (0) داشته باشند.")
    st.stop()

# تقسیم داده‌ها: 75 درصد آموزش و 25 درصد آزمایش
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# تبدیل رشته‌ها به ستون‌های عددی قابل فهم برای مدل
transformer = ColumnTransformer(
    [("text", OneHotEncoder(handle_unknown="ignore"), ["Major","RelatedMajor"])],
    remainder="passthrough"
)
train_ready = transformer.fit_transform(X_train)
test_ready = transformer.transform(X_test)

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(train_ready, y_train)
test_prediction = model.predict(test_ready)
accuracy = accuracy_score(y_test, test_prediction)
st.success(f"مدل آموزش داده شد. دقت روی داده آزمایش: {accuracy:.1%}")

st.subheader("پیش‌بینی برای دانشجو و درس انتخابی")
student_id = st.selectbox("دانشجو", students["StudentID"],
    format_func=lambda x: students.loc[students.StudentID==x,"FullName"].iloc[0])
course_id = st.selectbox("درس", courses["CourseID"],
    format_func=lambda x: courses.loc[courses.CourseID==x,"CourseName"].iloc[0])

s = students.loc[students.StudentID==student_id].iloc[0]
c = courses.loc[courses.CourseID==course_id].iloc[0]
st.write(f"سن: {s['Age']} | رشته: {s['Major']} | معدل: {s['GPA']} | واحد گذرانده: {s['CompletedCredits']}")
st.write(f"درس: {c['CourseName']} | واحد درس: {c['Credits']}")

if st.button("پیش‌بینی کن"):
    new_data = pd.DataFrame([{
        "Age":s["Age"], "Major":s["Major"], "GPA":s["GPA"],
        "CompletedCredits":s["CompletedCredits"], "RelatedMajor":c["RelatedMajor"],
        "Credits":c["Credits"], "Capacity":c["Capacity"], "Difficulty":c["Difficulty"]
    }])
    new_ready = transformer.transform(new_data[features])
    answer = int(model.predict(new_ready)[0])
    probability = model.predict_proba(new_ready)[0][1]
    if answer == 1:
        st.success(f"پیش‌بینی: دانشجو ثبت‌نام می‌کند. احتمال تخمینی: {probability:.1%}")
    else:
        st.warning(f"پیش‌بینی: دانشجو ثبت‌نام نمی‌کند. احتمال ثبت‌نام: {probability:.1%}")

st.caption("داده‌های این پروژه ساختگی و آموزشی هستند؛ نتیجه پیش‌بینی قطعی نیست.")
