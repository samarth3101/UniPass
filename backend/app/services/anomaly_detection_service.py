"""
Anomaly Detection Service - Phase 2: First Real AI
==================================================

Uses Isolation Forest (unsupervised ML) to detect suspicious attendance patterns:
- Proxy attendance (friend scanning)
- Screenshot abuse (QR sharing)
- Admin misuse (unauthorized overrides)
- Unrealistic patterns (multiple scans in short time)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import joblib
import os
from pathlib import Path

from app.models.attendance import Attendance
from app.models.event import Event
from app.models.student import Student


class AnomalyDetectionService:
    """Phase 2: Detect suspicious attendance patterns using ML"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )
        self.scaler = StandardScaler()
        self.model_path = Path(__file__).parent.parent.parent / "models"
        self.model_path.mkdir(exist_ok=True)
        self.is_trained = False
        self.training_metadata = {}  # Store training info
        self.feature_names = [
            'time_after_event_start',
            'time_since_last_scan',
            'student_attendance_rate',
            'is_admin_override',
            'scan_hour',
            'is_weekend',
            'scans_in_last_hour',
            'event_attendance_ratio'
        ]
        
        # Try to load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available"""
        model_file = self.model_path / "anomaly_detector.pkl"
        scaler_file = self.model_path / "anomaly_scaler.pkl"
        metadata_file = self.model_path / "training_metadata.pkl"
        
        if model_file.exists() and scaler_file.exists():
            try:
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                if metadata_file.exists():
                    self.training_metadata = joblib.load(metadata_file)
                self.is_trained = True
            except Exception as e:
                print(f"Failed to load model: {e}")
                self.is_trained = False
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            joblib.dump(self.model, self.model_path / "anomaly_detector.pkl")
            joblib.dump(self.scaler, self.model_path / "anomaly_scaler.pkl")
            joblib.dump(self.training_metadata, self.model_path / "training_metadata.pkl")
        except Exception as e:
            print(f"Failed to save model: {e}")
    
    def extract_features(self, db: Session, attendance_records: list) -> pd.DataFrame:
        """
        Convert attendance records to ML features
        
        Features engineered:
        1. time_after_event_start: Minutes between event start and scan
        2. time_since_last_scan: Minutes since student's previous scan
        3. student_attendance_rate: Historical attendance percentage
        4. is_admin_override: Binary flag for manual overrides
        5. scan_hour: Hour of day when scan occurred
        6. is_weekend: Binary flag for weekend scans
        7. scans_in_last_hour: Number of scans by student in past hour
        8. event_attendance_ratio: Actual vs. capacity ratio
        """
        features = []
        
        for record in attendance_records:
            event = db.query(Event).filter(Event.id == record.event_id).first()
            
            if not event:
                continue
            
            # Historical features
            student_history = db.query(Attendance)\
                .filter(Attendance.student_prn == record.student_prn)\
                .filter(Attendance.scanned_at < record.scanned_at)\
                .all()
            
            # Count events that occurred before this scan (more accurate than total events)
            past_events = db.query(func.count(Event.id))\
                .filter(Event.start_time < record.scanned_at)\
                .scalar() or 1
            
            # Time between scans feature
            prev_scan = db.query(Attendance)\
                .filter(Attendance.student_prn == record.student_prn)\
                .filter(Attendance.scanned_at < record.scanned_at)\
                .order_by(Attendance.scanned_at.desc())\
                .first()
            
            time_since_last_scan = 9999.0  # Default large value
            if prev_scan:
                time_since_last_scan = (record.scanned_at - prev_scan.scanned_at).total_seconds() / 60
            
            # Scans in last hour feature
            one_hour_ago = record.scanned_at - timedelta(hours=1)
            scans_in_last_hour = db.query(func.count(Attendance.id))\
                .filter(Attendance.student_prn == record.student_prn)\
                .filter(Attendance.scanned_at >= one_hour_ago)\
                .filter(Attendance.scanned_at < record.scanned_at)\
                .scalar() or 0
            
            # Event attendance ratio
            event_attendance_count = db.query(func.count(Attendance.id))\
                .filter(Attendance.event_id == record.event_id)\
                .filter(Attendance.scanned_at <= record.scanned_at)\
                .scalar() or 1
            
            event_attendance_ratio = 0.0
            if event.capacity and event.capacity > 0:
                event_attendance_ratio = event_attendance_count / event.capacity
            
            # Build feature vector
            features.append({
                'attendance_id': record.id,
                'time_after_event_start': (record.scanned_at - event.start_time).total_seconds() / 60,
                'time_since_last_scan': min(time_since_last_scan, 10080.0),  # Cap at 1 week
                'student_attendance_rate': len(student_history) / max(1, past_events) * 100,
                'is_admin_override': 1.0 if record.scan_source == 'admin_override' else 0.0,
                'scan_hour': float(record.scanned_at.hour),
                'is_weekend': 1.0 if record.scanned_at.weekday() >= 5 else 0.0,
                'scans_in_last_hour': float(scans_in_last_hour),
                'event_attendance_ratio': event_attendance_ratio
            })
        
        return pd.DataFrame(features)
    
    def train_anomaly_detector(self, db: Session) -> dict:
        """
        Train Isolation Forest on historical data
        
        Returns training statistics and feature importance
        """
        # Get all attendance records (last 6 months for training)
        six_months_ago = datetime.now() - timedelta(days=180)
        attendance_records = db.query(Attendance)\
            .filter(Attendance.scanned_at >= six_months_ago)\
            .all()
        
        if len(attendance_records) < 10:
            return {
                'error': 'Not enough data for training',
                'minimum_required': 10,
                'current_samples': len(attendance_records)
            }
        
        df = self.extract_features(db, attendance_records)
        
        if df.empty:
            return {
                'error': 'Feature extraction failed',
                'records_processed': len(attendance_records)
            }
        
        # Separate ID from features
        attendance_ids = df['attendance_id'].values
        X = df.drop('attendance_id', axis=1)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Save model for future use
        self._save_model()
        
        # Calculate training statistics
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        anomaly_count = np.sum(predictions == -1)
        
        # Calculate feature importance (based on variance after scaling)
        feature_importance = {}
        for i, col in enumerate(X.columns):
            feature_importance[col] = float(np.var(X_scaled[:, i]))
        
        # Normalize to percentages
        total_variance = sum(feature_importance.values())
        if total_variance > 0:
            feature_importance = {
                k: round((v / total_variance) * 100, 2) 
                for k, v in feature_importance.items()
            }
        
        # Store training metadata
        self.training_metadata = {
            'trained_at': datetime.now().isoformat(),
            'samples_used': len(X),
            'features': list(X.columns),
            'feature_count': len(X.columns),
            'anomalies_detected': int(anomaly_count),
            'anomaly_rate': float(anomaly_count / len(X) * 100),
            'feature_importance': feature_importance,
            'score_distribution': {
                'mean': float(np.mean(anomaly_scores)),
                'std': float(np.std(anomaly_scores)),
                'min': float(np.min(anomaly_scores)),
                'max': float(np.max(anomaly_scores))
            },
            'model_version': '1.0',
            'contamination': float(self.model.contamination),
            'n_estimators': int(self.model.n_estimators)
        }
        
        return {
            'model_trained': True,
            'samples_used': len(X),
            'features': list(X.columns),
            'feature_count': len(X.columns),
            'anomalies_in_training': int(anomaly_count),
            'anomaly_rate': float(anomaly_count / len(X) * 100),
            'feature_importance': feature_importance,
            'model_params': {
                'contamination': self.model.contamination,
                'n_estimators': self.model.n_estimators
            },
            'date_range': {
                'from': six_months_ago.isoformat(),
                'to': datetime.now().isoformat()
            },
            'performance_metrics': {
                'score_mean': float(np.mean(anomaly_scores)),
                'score_std': float(np.std(anomaly_scores)),
                'confidence': 'HIGH' if len(X) > 100 else 'MEDIUM' if len(X) > 50 else 'LOW'
            }
        }
    
    def detect_anomalies(self, db: Session, event_id: int = None) -> dict:
        """
        Detect anomalies in attendance records
        
        Args:
            db: Database session
            event_id: Optional filter for specific event
        
        Returns:
            Dictionary with anomaly detection results
        """
        if not self.is_trained:
            return {
                'error': 'Model not trained yet',
                'action_required': 'Train the model first using /train endpoint'
            }
        
        query = db.query(Attendance)
        if event_id:
            query = query.filter(Attendance.event_id == event_id)
        
        attendance_records = query.all()
        
        if not attendance_records:
            return {
                'anomalies': [],
                'total_checked': 0,
                'message': 'No attendance records found'
            }
        
        df = self.extract_features(db, attendance_records)
        
        if df.empty:
            return {
                'anomalies': [],
                'total_checked': len(attendance_records),
                'message': 'Feature extraction failed'
            }
        
        attendance_ids = df['attendance_id'].values
        X = df.drop('attendance_id', axis=1)
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # Create results
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            if pred == -1:  # Anomaly detected
                record = attendance_records[i]
                features_dict = df.iloc[i].drop('attendance_id').to_dict()
                
                anomalies.append({
                    'attendance_id': int(attendance_ids[i]),
                    'event_id': record.event_id,
                    'student_prn': record.student_prn,
                    'scanned_at': record.scanned_at.isoformat(),
                    'anomaly_score': float(score),
                    'severity': 'HIGH' if score < -0.5 else 'MEDIUM',
                    'scan_source': record.scan_source,
                    'features': features_dict,
                    'explanation': self.explain_anomaly(features_dict)
                })
        
        return {
            'total_checked': len(attendance_records),
            'anomalies_detected': len(anomalies),
            'anomaly_rate': round(len(anomalies) / len(attendance_records) * 100, 2) if attendance_records else 0,
            'anomalies': sorted(anomalies, key=lambda x: x['anomaly_score']),
            'model_info': {
                'is_trained': self.is_trained,
                'features_used': list(X.columns)
            }
        }
    
    def explain_anomaly(self, features: dict) -> str:
        """
        Generate human-readable explanation for detected anomaly
        
        Args:
            features: Feature dictionary from anomaly detection
        
        Returns:
            Human-readable explanation string
        """
        reasons = []
        
        if features['time_since_last_scan'] < 5:
            reasons.append("🚨 Scanned too soon after previous event (< 5 minutes)")
        
        time_diff = abs(features['time_after_event_start'])
        if time_diff > 30:
            hours = time_diff / 60
            if hours >= 1:
                reasons.append(f"🚨 Scanned {hours:.1f} hours {'after' if features['time_after_event_start'] > 0 else 'before'} event start")
            else:
                reasons.append(f"🚨 Scanned {int(time_diff)} minutes {'after' if features['time_after_event_start'] > 0 else 'before'} event start")
        
        if features['is_admin_override'] == 1:
            reasons.append("⚠️ Manual admin override (requires review)")
        
        scan_hour = int(features['scan_hour'])
        if scan_hour < 6 or scan_hour > 22:
            reasons.append(f"🚨 Unusual scan time ({scan_hour}:00 - outside 6 AM - 10 PM)")
        
        if features['student_attendance_rate'] < 10:
            reasons.append(f"⚠️ Low historical attendance ({features['student_attendance_rate']:.0f}%)")
        
        if features['scans_in_last_hour'] >= 3:
            reasons.append(f"🚨 Multiple scans in last hour ({int(features['scans_in_last_hour'])} scans)")
        
        if features['event_attendance_ratio'] > 1.2:
            reasons.append("⚠️ Event over-capacity (possible duplicate scans)")
        
        return " | ".join(reasons) if reasons else "Multiple anomaly indicators detected"
    
    def get_anomaly_summary(self, db: Session) -> dict:
        """
        Get overall anomaly statistics for the system
        
        Returns:
            Summary statistics of anomalies
        """
        if not self.is_trained:
            return {
                'error': 'Model not trained yet',
                'is_trained': False
            }
        
        result = self.detect_anomalies(db)
        
        if 'error' in result:
            return result
        
        # Group by severity
        high_severity = [a for a in result['anomalies'] if a['severity'] == 'HIGH']
        medium_severity = [a for a in result['anomalies'] if a['severity'] == 'MEDIUM']
        
        # Group by scan source
        admin_overrides = [a for a in result['anomalies'] if a['scan_source'] == 'admin_override']
        qr_scans = [a for a in result['anomalies'] if a['scan_source'] == 'qr_scan']
        
        return {
            'is_trained': True,
            'total_checked': result['total_checked'],
            'total_anomalies': result['anomalies_detected'],
            'anomaly_rate': result['anomaly_rate'],
            'by_severity': {
                'high': len(high_severity),
                'medium': len(medium_severity)
            },
            'by_source': {
                'admin_override': len(admin_overrides),
                'qr_scan': len(qr_scans),
                'other': result['anomalies_detected'] - len(admin_overrides) - len(qr_scans)
            },
            'requires_review': len(high_severity)
        }
