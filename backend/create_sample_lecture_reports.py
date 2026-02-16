"""
Create Sample Lecture Reports for Testing (No OpenAI API Required)
Perfect for student projects and local testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models.lecture_report import LectureReport
from app.models.event import Event
from app.models.user import User
from datetime import datetime, timezone
import json


def create_sample_reports():
    """Generate sample lecture reports for testing without OpenAI API"""
    
    db: Session = SessionLocal()
    
    try:
        # Get first admin/organizer user
        user = db.query(User).filter(User.role.in_(["ADMIN", "ORGANIZER"])).first()
        if not user:
            print("❌ No admin or organizer user found. Create one first:")
            print("   python create_admin.py")
            return False
        
        # Get all events
        events = db.query(Event).limit(5).all()
        if not events:
            print("❌ No events found in database. Create an event first.")
            return False
        
        print(f"\n✅ Found {len(events)} events")
        print(f"✅ Using user: {user.email}\n")
        
        created_count = 0
        
        for event in events:
            # Check if report already exists
            existing = db.query(LectureReport).filter(
                LectureReport.event_id == event.id
            ).first()
            
            if existing:
                print(f"⏭️  Event #{event.id} '{event.title}' - Report already exists (ID: {existing.id})")
                continue
            
            # Generate sample data based on event
            sample_transcript = f"""
Welcome everyone to {event.title}. Today's session is going to be incredibly valuable for all participants.

Let me start by introducing the key objectives. We'll be covering fundamental concepts, practical applications, and real-world examples. This knowledge will be crucial for your academic and professional development.

First, let's discuss the theoretical foundations. Understanding these core principles is essential before we move to advanced topics. The concepts we're exploring today have applications across multiple domains.

Now, moving to practical demonstrations. I'll walk you through several examples that illustrate these principles in action. Pay close attention to the methodology and approach being used here.

For the technical implementation, we need to consider several factors: scalability, maintainability, and performance. These are critical aspects that often determine the success of any solution.

Let's also discuss some common challenges and how to overcome them. Many students face similar issues, so learning these problem-solving strategies will be highly beneficial.

The industry applications of what we're learning today are extensive. Companies are actively seeking professionals with these skills, making this knowledge highly marketable.

Before we wrap up, let's have a Q&A session. I encourage you to ask questions about anything that wasn't clear or if you need further clarification on specific topics.

Thank you all for your attention and participation. Remember to practice what we've learned today, as hands-on experience is the best way to solidify your understanding.
"""
            
            # Sample keywords
            sample_keywords = [
                "fundamentals",
                "practical applications",
                "theoretical foundations",
                "implementation",
                "problem-solving",
                "industry applications",
                "methodology",
                "best practices",
                "core concepts",
                "real-world examples",
                "scalability",
                "professional development",
                "hands-on experience",
                "technical skills",
                "Q&A session"
            ]
            
            # Sample structured summary
            sample_summary = {
                "event_overview": f"{event.title} provided comprehensive coverage of fundamental and advanced concepts with emphasis on practical application and real-world relevance. The session successfully bridged theoretical knowledge with industry practices.",
                "key_topics_discussed": [
                    "Theoretical Foundations and Core Principles",
                    "Practical Implementation Strategies",
                    "Real-World Applications and Case Studies",
                    "Common Challenges and Solutions",
                    "Industry Best Practices",
                    "Scalability and Performance Optimization",
                    "Professional Development Pathways",
                    "Interactive Q&A and Problem-Solving"
                ],
                "important_quotes": [
                    "Understanding these core principles is essential before we move to advanced topics",
                    "Hands-on experience is the best way to solidify your understanding",
                    "Companies are actively seeking professionals with these skills",
                    "Pay close attention to the methodology and approach being used"
                ],
                "technical_highlights": f"The session delved into both theoretical and practical aspects of {event.title if event.title else 'the subject'}. Key technical discussions included implementation methodologies, scalability considerations, and performance optimization techniques. Participants gained exposure to industry-standard practices and modern approaches to problem-solving in this domain.",
                "audience_engagement_summary": "High level of audience engagement throughout the session. Students actively participated in discussions and asked thoughtful questions during the Q&A segment. Multiple requests for additional resources and follow-up sessions indicate strong interest in the topic. The interactive format facilitated better understanding and practical learning.",
                "recommended_followup_actions": [
                    "Practice the concepts covered through hands-on projects",
                    "Review the session materials and supplementary resources",
                    "Form study groups to discuss and solve practice problems together",
                    "Research advanced topics and prepare questions for next session",
                    "Apply learned concepts to current coursework or personal projects",
                    "Attend office hours for individual clarification on complex topics",
                    "Explore industry case studies related to the topics covered"
                ]
            }
            
            # Create report
            report = LectureReport(
                event_id=event.id,
                audio_filename=f"sample_lecture_{event.id}.mp3",
                transcript=sample_transcript,
                keywords=sample_keywords,
                summary=json.dumps(sample_summary, indent=2),
                generated_at=datetime.now(timezone.utc),
                generated_by=user.id,
                status="completed"
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            print(f"✅ Created report for Event #{event.id} '{event.title}' (Report ID: {report.id})")
            created_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ SAMPLE REPORTS CREATED: {created_count}")
        print(f"{'='*60}\n")
        
        if created_count > 0:
            print("🎉 SUCCESS! You can now test the Cortex LIE feature:")
            print("\n📋 Next Steps:")
            print("1. Start your backend: cd backend && uvicorn app.main:app --reload")
            print("2. Start your frontend: cd frontend && npm run dev")
            print("3. Navigate to: http://localhost:3000/cortex/lecture-ai")
            print(f"4. Enter Event ID (e.g., {events[0].id}) and click 'View Existing Report'\n")
            
            print("📝 Available Event IDs with Reports:")
            for event in events[:created_count]:
                print(f"   - Event #{event.id}: {event.title}")
        else:
            print("ℹ️  No new reports created (all events already have reports)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating sample reports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CORTEX LIE - SAMPLE REPORT GENERATOR")
    print("Student Project Testing - No OpenAI API Required")
    print("="*60 + "\n")
    
    success = create_sample_reports()
    
    if not success:
        sys.exit(1)
