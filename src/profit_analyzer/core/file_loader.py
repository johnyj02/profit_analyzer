import os
import glob
import pandas as pd

class FileLoader:
    def __init__(self, folder_path: str, include_patterns: list[str]):
        self.folder_path = folder_path
        self.include_patterns = include_patterns

    def load_files(self) -> pd.DataFrame:
        frames = []
        for pat in self.include_patterns:
            for fp in glob.glob(os.path.join(self.folder_path, pat)):
                df = pd.read_csv(fp)
                # Skip truly empty frames to avoid dtype warnings on concat
                if df is None or df.empty or len(df.columns) == 0:
                    continue
                df['__source_file__'] = os.path.basename(fp)
                frames.append(df)
        if not frames:
            raise FileNotFoundError(f"No files matched patterns {self.include_patterns} under {self.folder_path}")
        # Concat only non-empty frames
        return pd.concat(frames, ignore_index=True, copy=False)
