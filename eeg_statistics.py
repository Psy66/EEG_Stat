# eeg_statistics.py
import os
from collections import defaultdict
from dateutil.parser import parse
from pandas import DataFrame
from seaborn import countplot, histplot
from matplotlib.pyplot import figure, title, savefig, close

def calculate_age(birthdate, recording_date):
    """Calculates the age at the time of recording."""
    try:
        if isinstance(birthdate, str):
            birthdate = parse(birthdate)
        if isinstance(recording_date, str):
            recording_date = parse(recording_date)
        if hasattr(recording_date, 'tzinfo') and recording_date.tzinfo is not None:
            recording_date = recording_date.replace(tzinfo=None)
        age = recording_date.year - birthdate.year
        if (recording_date.month, recording_date.day) < (birthdate.month, birthdate.day):
            age -= 1
        return age
    except Exception as e:
        print(f"Error calculating age: {e}")
        return None

def generate_statistics(metadata_list):
    """Generates descriptive statistics from metadata."""
    stats = defaultdict(list)
    for metadata in metadata_list:
        subject_info = metadata.get('subject_info', {})
        stats['file_name'].append(metadata['file_name'])
        stats['sex'].append(
            'Male' if subject_info.get('sex') == 1 else 'Female' if subject_info.get('sex') == 2 else 'Unknown')

        birthdate = subject_info.get('birthday')
        recording_date = metadata.get('meas_date')
        if birthdate and recording_date:
            age = calculate_age(birthdate, recording_date)
            if age is not None:
                stats['age'].append(min(age, 60))  # Limit age to 60 years

        stats['duration_minutes'].append(metadata['duration'] / 60)

    df = DataFrame(stats)
    descriptive_stats = {
        'sex_distribution': df['sex'].value_counts(),
        'age_distribution': df['age'].describe() if 'age' in df.columns else None,
        'duration_stats': df['duration_minutes'].describe()
    }
    return df, descriptive_stats

def visualize_statistics(df, output_dir):
    """Visualizes the statistics."""
    os.makedirs(output_dir, exist_ok=True)

    if 'sex' in df.columns:
        figure(figsize=(8, 6))
        countplot(data=df, x='sex')
        title('Sex Distribution')
        savefig(os.path.join(output_dir, 'sex_distribution.png'))
        close()

    if 'age' in df.columns:
        age_data = df[df['age'].apply(lambda x: isinstance(x, (int, float)))]
        if not age_data.empty:
            figure(figsize=(8, 6))
            histplot(data=age_data, x='age', bins=20, kde=True)
            title('Age Distribution')
            savefig(os.path.join(output_dir, 'age_distribution.png'))
            close()

    if 'duration_minutes' in df.columns:
        figure(figsize=(8, 6))
        histplot(data=df, x='duration_minutes', bins=20, kde=True)
        title('Recording Duration (minutes)')
        savefig(os.path.join(output_dir, 'duration_distribution.png'))
        close()