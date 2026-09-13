import pandas as pd

# استبدل الاسم بمسار ملف الـ CSV الفعلي لديك
file_path = 'cicids2017_data.csv' 
df = pd.read_csv(file_path)

print("شكل البيانات (صفوف، أعمدة):", df.shape)
print("\nتوزيع الحالات (حركة طبيعية مقابل هجمات):")
print(df['Label'].value_counts())
