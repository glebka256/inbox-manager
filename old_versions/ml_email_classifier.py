import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import os
from datetime import datetime

class EmailMLClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.label_mapping = {}
        self.reverse_mapping = {}
        
    def load_training_data(self, csv_file="email_training_data.csv"):
        """Load training data from CSV file"""
        try:
            df = pd.read_csv(csv_file)
            print(f"📊 Loaded {len(df)} training samples from {csv_file}")
            
            # Check data quality
            print(f"   Labels: {df['label'].unique()}")
            print(f"   Label distribution:")
            for label, count in df['label'].value_counts().items():
                print(f"     {label}: {count} samples")
            
            return df
        except Exception as e:
            print(f"❌ Error loading training data: {e}")
            return None
    
    def prepare_data(self, df):
        """Prepare data for training"""
        # Remove samples with missing feature text
        df = df.dropna(subset=['feature_text'])
        
        # Filter out labels with too few samples (less than 2)
        label_counts = df['label'].value_counts()
        valid_labels = label_counts[label_counts >= 2].index
        df = df[df['label'].isin(valid_labels)]
        
        if len(df) == 0:
            raise ValueError("No valid training data after filtering")
        
        # Create label mappings for consistency
        unique_labels = sorted(df['label'].unique())
        self.label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
        self.reverse_mapping = {idx: label for label, idx in self.label_mapping.items()}
        
        # Extract features and labels
        X = df['feature_text'].tolist()
        y = df['label'].map(self.label_mapping).tolist()
        
        print(f"📚 Prepared data:")
        print(f"   Features: {len(X)} text samples")
        print(f"   Labels: {len(set(y))} unique classes")
        print(f"   Average text length: {np.mean([len(text) for text in X]):.1f} characters")
        
        return X, y
    
    def train_model(self, X, y, test_size=0.2, random_state=42):
        """Train the machine learning model"""
        print("🤖 Training ML Email Classifier...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Create pipeline with TF-IDF and Naive Bayes
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),  # Use both unigrams and bigrams
                min_df=1,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train the model
        print(f"   Training on {len(X_train)} samples...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"   Test Accuracy: {accuracy:.3f}")
        
        # Cross-validation for more robust evaluation
        if len(X_train) > 10:  # Only if we have enough data
            cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=min(5, len(X_train)//2))
            print(f"   Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Detailed classification report
        print("\n📋 Classification Report:")
        label_names = [self.reverse_mapping[i] for i in sorted(self.reverse_mapping.keys())]
        print(classification_report(y_test, y_pred, target_names=label_names, zero_division=0))
        
        return accuracy
    
    def save_model(self, model_path="email_classifier.pkl", vectorizer_path="vectorizer.pkl"):
        """Save the trained model and vectorizer"""
        try:
            if self.pipeline is None:
                print("❌ No trained model to save")
                return False
            
            # Save the complete pipeline
            joblib.dump(self.pipeline, model_path)
            
            # Also save just the vectorizer for compatibility
            joblib.dump(self.pipeline.named_steps['tfidf'], vectorizer_path)
            
            # Save label mappings
            label_mapping_path = "label_mappings.pkl"
            joblib.dump({
                'label_mapping': self.label_mapping,
                'reverse_mapping': self.reverse_mapping
            }, label_mapping_path)
            
            print(f"💾 Model saved successfully:")
            print(f"   Pipeline: {model_path}")
            print(f"   Vectorizer: {vectorizer_path}")
            print(f"   Label mappings: {label_mapping_path}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def load_model(self, model_path="email_classifier.pkl"):
        """Load a trained model"""
        try:
            self.pipeline = joblib.load(model_path)
            
            # Load label mappings
            label_mapping_path = "label_mappings.pkl"
            if os.path.exists(label_mapping_path):
                mappings = joblib.load(label_mapping_path)
                self.label_mapping = mappings['label_mapping']
                self.reverse_mapping = mappings['reverse_mapping']
            
            print(f"✅ Model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict(self, text_samples, return_probabilities=False):
        """Predict labels for new text samples"""
        if self.pipeline is None:
            print("❌ No trained model available")
            return None
        
        try:
            if isinstance(text_samples, str):
                text_samples = [text_samples]
            
            # Get predictions
            predictions = self.pipeline.predict(text_samples)
            
            # Convert back to label names
            predicted_labels = [self.reverse_mapping[pred] for pred in predictions]
            
            if return_probabilities:
                probabilities = self.pipeline.predict_proba(text_samples)
                return predicted_labels, probabilities
            
            return predicted_labels
        except Exception as e:
            print(f"❌ Error making predictions: {e}")
            return None
    
    def test_predictions(self, test_samples):
        """Test the model with sample texts"""
        print("🧪 Testing Model Predictions:")
        print("=" * 50)
        
        for i, sample in enumerate(test_samples, 1):
            predictions, probabilities = self.predict([sample], return_probabilities=True)
            
            if predictions:
                print(f"{i}. Text: \"{sample[:60]}...\"")
                print(f"   Predicted: {predictions[0]}")
                
                # Show top 3 probabilities
                prob_dict = dict(zip(self.reverse_mapping.values(), probabilities[0]))
                sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:3]
                
                print("   Top probabilities:")
                for label, prob in sorted_probs:
                    print(f"     {label}: {prob:.3f}")
                print()

def main():
    print("🚀 Email ML Classifier Training")
    print("=" * 50)
    
    # Initialize classifier
    classifier = EmailMLClassifier()
    
    # Load training data
    df = classifier.load_training_data("email_training_data.csv")
    if df is None:
        print("❌ Could not load training data")
        return
    
    # Prepare data
    try:
        X, y = classifier.prepare_data(df)
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return
    
    # Train model
    accuracy = classifier.train_model(X, y)
    
    if accuracy > 0.5:  # Lower threshold due to small dataset
        # Save the model
        print("\n" + "=" * 50)
        classifier.save_model()
        
        # Test with some sample emails
        print("\n" + "=" * 50)
        test_samples = [
            "LinkedIn job alert software engineer",
            "Python programming tutorial machine learning",
            "Government contract solicitation RFP bid",
            "Bonfire custom apparel fundraising campaign",
            "API documentation REST endpoint integration",
            "Freight load hotshot trucking rate",
            "Rate confirmation pickup delivery schedule"
        ]
        
        classifier.test_predictions(test_samples)
    else:
        print(f"⚠️ Model accuracy ({accuracy:.3f}) is too low to save")
    
    print("\n✅ Training completed!")

if __name__ == "__main__":
    main()