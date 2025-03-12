import os
from seaborn import countplot, histplot
from matplotlib.pyplot import figure, title, savefig, close
from pandas import DataFrame

class EDFVisualizer:
    def __init__(self, directory):
        self.directory = directory
        self.output_dir = os.path.join(self.directory, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def visualize_statistics(self, df):
        """Визуализация статистики."""
        if 'sex' in df.columns:
            figure(figsize=(8, 6))
            countplot(data=df, x='sex')
            title('Распределение по полу')
            savefig(os.path.join(self.output_dir, 'sex_distribution.png'))
            close()

        if 'age' in df.columns:
            age_data = df[df['age'].apply(lambda x: isinstance(x, (int, float)))]
            if not age_data.empty:
                figure(figsize=(8, 6))
                histplot(data=age_data, x='age', bins=20, kde=True)
                title('Распределение по возрасту')
                savefig(os.path.join(self.output_dir, 'age_distribution.png'))
                close()

        if 'duration_minutes' in df.columns:
            figure(figsize=(8, 6))
            histplot(data=df, x='duration_minutes', bins=20, kde=True)
            title('Длительность записи (минуты)')
            savefig(os.path.join(self.output_dir, 'duration_distribution.png'))
            close()