"""
Test Anomaly Detection Phase 2 Implementation
==============================================

Run this script to test the anomaly detection functionality.

Usage:
    python test_anomaly_phase2.py
"""

from app.db.database import SessionLocal
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.models import Attendance, Event, Student

print("\n" + "="*70)
print("AI PHASE 2 - ANOMALY DETECTION TEST")
print("="*70)

db = SessionLocal()
service = AnomalyDetectionService()

# Test 1: Check model status
print("\n📊 Test 1: Model Status")
print("-" * 70)
print(f"Model trained: {service.is_trained}")
print(f"Model path: {service.model_path}")

# Test 2: Check data availability
print("\n📊 Test 2: Data Availability")
print("-" * 70)
total_attendance = db.query(Attendance).count()
total_events = db.query(Event).count()
total_students = db.query(Student).count()

print(f"Total attendance records: {total_attendance}")
print(f"Total events: {total_events}")
print(f"Total students: {total_students}")

if total_attendance < 10:
    print("\n⚠️  WARNING: Need at least 10 attendance records for training")
    print(f"   Current: {total_attendance} records")
    print("   Action: Add more attendance data before training the model")
else:
    print(f"\n✅ Sufficient data for training ({total_attendance} records)")

# Test 3: Feature extraction
print("\n📊 Test 3: Feature Extraction")
print("-" * 70)
try:
    sample_records = db.query(Attendance).limit(3).all()
    if sample_records:
        df = service.extract_features(db, sample_records)
        print(f"Features extracted: {len(df)} records")
        print(f"Feature columns: {list(df.columns)}")
        print("\nSample features:")
        print(df.head())
    else:
        print("⚠️  No attendance records found for feature extraction")
except Exception as e:
    print(f"❌ Feature extraction failed: {e}")

# Test 4: Train model (if enough data)
if total_attendance >= 10:
    print("\n📊 Test 4: Model Training")
    print("-" * 70)
    try:
        result = service.train_anomaly_detector(db)
        if 'error' in result:
            print(f"❌ Training failed: {result['error']}")
        else:
            print("✅ Model trained successfully!")
            print(f"   Samples used: {result['samples_used']}")
            print(f"   Features: {result['feature_count']}")
            print(f"   Anomalies in training: {result['anomalies_in_training']}")
            print(f"   Anomaly rate: {result['anomaly_rate']:.2f}%")
    except Exception as e:
        print(f"❌ Training failed with exception: {e}")
        import traceback
        traceback.print_exc()

    # Test 5: Anomaly detection
    print("\n📊 Test 5: Anomaly Detection")
    print("-" * 70)
    try:
        result = service.detect_anomalies(db)
        if 'error' in result:
            print(f"❌ Detection failed: {result['error']}")
        else:
            print(f"✅ Anomaly detection completed!")
            print(f"   Total checked: {result['total_checked']}")
            print(f"   Anomalies detected: {result['anomalies_detected']}")
            print(f"   Anomaly rate: {result['anomaly_rate']:.2f}%")
            
            if result['anomalies_detected'] > 0:
                print(f"\n   Top 3 anomalies:")
                for i, anomaly in enumerate(result['anomalies'][:3], 1):
                    print(f"\n   {i}. Attendance ID: {anomaly['attendance_id']}")
                    print(f"      Student: {anomaly['student_prn']}")
                    print(f"      Severity: {anomaly['severity']}")
                    print(f"      Score: {anomaly['anomaly_score']:.4f}")
                    print(f"      Explanation: {anomaly['explanation']}")
    except Exception as e:
        print(f"❌ Detection failed with exception: {e}")
        import traceback
        traceback.print_exc()

    # Test 6: Anomaly summary
    print("\n📊 Test 6: Anomaly Summary")
    print("-" * 70)
    try:
        summary = service.get_anomaly_summary(db)
        if 'error' in summary:
            print(f"❌ Summary failed: {summary['error']}")
        else:
            print(f"✅ Summary generated!")
            print(f"   Total checked: {summary['total_checked']}")
            print(f"   Total anomalies: {summary['total_anomalies']}")
            print(f"   By severity:")
            print(f"      High: {summary['by_severity']['high']}")
            print(f"      Medium: {summary['by_severity']['medium']}")
            print(f"   By source:")
            print(f"      Admin override: {summary['by_source']['admin_override']}")
            print(f"      QR scan: {summary['by_source']['qr_scan']}")
            print(f"   Requires review: {summary['requires_review']}")
    except Exception as e:
        print(f"❌ Summary failed with exception: {e}")
else:
    print("\n⏭️  Skipping tests 4-6 (insufficient data for training)")

db.close()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\n💡 Next Steps:")
print("   1. If model is trained: Access anomaly detection via API")
print("   2. Frontend: http://localhost:3000/analytics/anomaly")
print("   3. API endpoints:")
print("      POST /analytics/anomaly/train")
print("      GET  /analytics/anomaly/detect")
print("      GET  /analytics/anomaly/explain/{id}")
print("      GET  /analytics/anomaly/summary")
print("      GET  /analytics/anomaly/status")
print()
