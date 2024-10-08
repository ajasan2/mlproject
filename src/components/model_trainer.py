import os
import sys
from dataclasses import dataclass

from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, train_arr, test_arr):
        try:
            X_train, y_train, X_test, y_test = (
                train_arr[:,:-1],
                train_arr[:,1],
                test_arr[:,:-1],
                test_arr[:,1],
            )

            models = {
                'Decision Tree': DecisionTreeRegressor(),
                'Random Forest': RandomForestRegressor(),
                'Gradient Boosting': GradientBoostingRegressor(),
                'Linear Regression': LinearRegression(),
                'K-Nearest Neighbors': KNeighborsRegressor(),
                'XGBRegressor': XGBRegressor(),
                'AdaBoostRegressor': AdaBoostRegressor(),
            }

            params = {
                'Decision Tree': {
                    # 'criterion':['squared_error', 'friedman_mse', 'poisson'],
                    'max_features':[None, 'log2'],
                },
                'Random Forest':{
                    # 'criterion':['squared_error', 'friedman_mse', 'poisson'],
                    'n_estimators': [16, 32, 64, 128, 256]
                },
                'Gradient Boosting':{
                    'loss':['squared_error', 'huber', 'quantile'],
                    'learning_rate':[.1, .01, .05, .001],
                    'criterion':['squared_error', 'friedman_mse'],
                    # 'subsample':[0.6, 0.75, 0.9],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [16, 32, 64, 128, 256]
                },
                'Linear Regression':{},
                'K-Nearest Neighbors':{},
                'XGBRegressor':{
                    'learning_rate':[.1, .01, .05, .001],
                    'n_estimators': [16, 32, 64, 128, 256]
                },
                'AdaBoostRegressor':{
                    'learning_rate':[.1, .01, 0.5, .001],
                    'loss':['linear','square','exponential'],
                    'n_estimators': [16, 32, 64, 128, 256]
                }
                
            }

            model_report:dict = evaluate_models(X_train, y_train, X_test, y_test, models, params)

            best_model_name = max(model_report, key=model_report.get)
            best_model_score = model_report[best_model_name]
            best_model = models[best_model_name]
            print(f'Best Model: {best_model_name} with R2 Score: {best_model_score}')

            if best_model_score < 0.6:
                raise CustomException('Best model score is less than 0.6', sys)
            
            linear_regression_score = model_report['Linear Regression']
            if linear_regression_score >= best_model_score - 0.05:
                best_model_name = 'Linear Regression'
                best_model_score = linear_regression_score
                best_model = models[best_model_name]
                print(f'Linear Regression selected for its simplicity with R2 Score: {best_model_score}')

            logging.info('Model evaluation completed successfully')

            save_object(
                file_path = self.model_trainer_config.trained_model_file_path,
                obj = best_model
            )

            predicted = best_model.predict(X_test)
            return r2_score(y_test, predicted)
            
        except Exception as e:
            raise CustomException(e, sys)