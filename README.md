# پیش‌بینی ثبت‌نام دانشجو با Decision Tree

## فایل‌ها
- `database.sql`: ساخت دیتابیس، سه جدول، داده نمونه و سه View
- `app.py`: اتصال به SQL Server، آموزش مدل و فرم پیش‌بینی
- `requirements.txt`: کتابخانه‌های پایتون

## اجرا
1. در SSMS فایل `database.sql` را باز کنید و کل آن را اجرا کنید.
2. در CMD وارد پوشه پروژه شوید و بزنید:
   `pip install -r requirements.txt`
3. برنامه را اجرا کنید:
   `streamlit run app.py`

پیش‌فرض اتصال: سرور `localhost`، دیتابیس `StudentEnrollmentDB` و Windows Authentication.
اگر نام سرور شما چیز دیگری است، در CMD قبل از اجرا بزنید:
`set SQL_SERVER=نام_سرور`

## ساختار
جدول Student مشخصات دانشجو، Course مشخصات درس و Enrollment نتیجه هر جفت دانشجو و درس را نگه می‌دارد.
در Enrollment مقدار `IsEnrolled=1` یعنی ثبت‌نام کرده و `0` یعنی ثبت‌نام نکرده است. وجود هر دو حالت برای آموزش مدل لازم است.
سه View به نام‌های `vw_Student`، `vw_Course` و `vw_Enrollment` ساخته می‌شوند.
مدل Decision Tree با 75 درصد داده آموزش می‌بیند و با 25 درصد باقی‌مانده آزمایش می‌شود.

**توجه:** داده‌ها ساختگی و صرفاً برای تمرین دانشگاهی هستند.
