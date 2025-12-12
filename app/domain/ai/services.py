import pandas as pd
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.exceptions import NotFittedError
import threading

from app.domain.ai.entities import AccountSuggestion

class AccountingAssistantService:
    _model_pipeline: Optional[Pipeline] = None
    _is_training: bool = False
    _lock = threading.Lock()

    def __init__(self, db: Session):
        self.db = db
        # If model is not loaded, trigger training in background?
        # For simplicity in this demo, we train on first request or if missing.
        if AccountingAssistantService._model_pipeline is None:
             self._train_model()

    def _train_model(self):
        """
        Trains the TF-IDF + Logistic Regression model using all historical journal entries.
        """
        with AccountingAssistantService._lock:
            if AccountingAssistantService._model_pipeline is not None:
                return # Already trained
            
            AccountingAssistantService._is_training = True
            try:
                # 1. Fetch Data
                # Adjust query based on actual schema. Assuming journal_entries and lines.
                query = text("""
                    SELECT e.description, l.account_code, a.name as account_name
                    FROM journal_entries e
                    JOIN journal_entry_lines l ON e.id = l.entry_id
                    JOIN accounts a ON l.account_code = a.code
                    WHERE e.description IS NOT NULL AND e.description != ''
                """)
                results = self.db.execute(query).fetchall()
                
                if not results:
                    print("AI: No training data found.")
                    AccountingAssistantService._is_training = False
                    return

                df = pd.DataFrame(results, columns=['description', 'account_code', 'account_name'])
                
                # 2. Build Pipeline
                # We want to predict account_code based on description
                # TF-IDF: Convert text to vectors
                # Logistic Regression: Classifier (efficient for sparse text data)
                pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(max_features=1000, stop_words=None)), # Catalan stop words could be added
                    ('clf', LogisticRegression(solver='liblinear', multi_class='auto'))
                ])
                
                # 3. Train
                X = df['description']
                y = df['account_code']
                
                pipeline.fit(X, y)
                
                # Store account names for lookup later
                self._account_names = df.set_index('account_code')['account_name'].to_dict()
                
                AccountingAssistantService._model_pipeline = pipeline
                print("AI: Model trained successfully.")
                
            except Exception as e:
                print(f"AI: Error training model: {e}")
            finally:
                AccountingAssistantService._is_training = False

    def predict_accounts(self, description: str) -> List[AccountSuggestion]:
        if not description or len(description) < 3:
            return []
            
        if AccountingAssistantService._model_pipeline is None:
            if not AccountingAssistantService._is_training:
                self._train_model() # Try to train now
            
            if AccountingAssistantService._model_pipeline is None:
                return [] # Still no model (maybe no data)

        try:
            pipeline = AccountingAssistantService._model_pipeline
            
            # Predict probabilities
            # classes_ contains the account codes
            probs = pipeline.predict_proba([description])[0]
            classes = pipeline.classes_
            
            # Create a list of (account, prob)
            predictions = list(zip(classes, probs))
            
            # Sort by probability DESC
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            suggestions = []
            # Take top 3
            for account_code, prob in predictions[:3]:
                if prob < 0.1: continue # Filter low confidence
                
                # Lookup name (fallback if not in _account_names map, fetch from DB or generic)
                # For this demo we just try to get it from memory or DB check could be added
                account_name = getattr(self, '_account_names', {}).get(account_code, "Compte " + account_code)
                
                suggestions.append(AccountSuggestion(
                    account_code=account_code,
                    account_name=account_name,
                    confidence=round(prob, 2),
                    reason=f"Predicció IA ({int(prob*100)}% de confiança)"
                ))
                
            return suggestions

        except NotFittedError:
             return []
        except Exception as e:
            print(f"AI: Prediction error: {e}")
            return []
