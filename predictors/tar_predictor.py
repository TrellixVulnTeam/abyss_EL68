import numpy as np
import pandas as pd
import pickle as pkl
from predictors.predictor import Predictor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from typing import Optional


class TarPredictor(Predictor):
    def __init__(self):
        super().__init__()

    @staticmethod
    def is_compatible(file_path: str) -> bool:
        """Returns whether a file is compatible with tar predictor.

        Parameters
        ----------
        file_path : str
            Path to file to check compatibility with.

        Returns
        -------
        bool
            Whether file_path is compatible with tar predictor.
        """
        return Predictor.get_extension(file_path) == ".tar"

    @staticmethod
    def train_model(data_path: Optional[str] = "../tar_decompression_results.csv",
                    save_path: Optional[str] = "tar_model.pkl") -> None:
        """Trains and saves a predictor model.

        Parameters
        ----------
        data_path : str
            Path to data to train on.
        save_path : str
            Path to save model.
        """
        data_df = pd.read_csv(data_path)

        x = np.array(data_df.compressed_size)
        y = np.array(data_df.decompressed_size)

        degree = 3
        X = x.reshape(-1, 1)

        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(X, y)

        with open(save_path, "wb") as f:
            pkl.dump(model, f)

    def load_model(self, load_path: Optional[str] = "tar_model.pkl") -> None:
        """Loads model to class.

        Parameters
        ----------
        load_path : str
            Path to predictor model to load.
        """
        with open(load_path, "rb") as f:
            self.model = pkl.load(f)

    def predict(self, file_path: str, file_size: float) -> float:
        """Predicts the size of decompressed .tar file.

        Parameters
        ----------
        file_path : str
            Path of compressed file to predict on.
        file_size : float
            Size of compressed file to predict on.

        Returns
        -------
        float
            Prediction of decompressed .tar file size.
        """
        if not self.model:
            raise ValueError("Model must be loaded before running predictions.")

        x = np.array([file_size]).reshape(1, -1)

        return self.model.predict(x)[0]


if __name__ == "__main__":
    pass
