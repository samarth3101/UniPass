"use client";

type Event = {
  id: number;
  title: string;
  location: string;
  start_time: string;
  end_time: string;
};

type Props = {
  event: Event;
  onClick: () => void;
};

function formatDate(iso: string) {
  const d = new Date(iso);

  const day = String(d.getDate()).padStart(2, "0");
  const month = d.toLocaleString('en-US', { month: 'short' });
  const year = d.getFullYear();

  // Use 12-hour format instead of 24-hour
  const hours = d.getHours();
  const mins = String(d.getMinutes()).padStart(2, "0");
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const hours12 = hours % 12 || 12;

  return { date: `${month} ${day}, ${year}`, time: `${String(hours12).padStart(2, "0")}:${mins} ${ampm}` };
}

function getEventStatus(startTime: string, endTime: string) {
  const now = new Date();
  const start = new Date(startTime);
  const end = new Date(endTime);

  if (now >= start && now <= end) return "ongoing";
  if (now < start) return "upcoming";
  return "completed";
}

export default function EventCard({ event, onClick }: Props) {
  const { date, time } = formatDate(event.start_time);
  const status = getEventStatus(event.start_time, event.end_time);

  return (
    <div className="event-card" onClick={onClick}>
      <div className="card-header">
        <span className={`status-badge ${status}`}>
          {status === "ongoing" && "Live"}
          {status === "upcoming" && "Upcoming"}
          {status === "completed" && "Completed"}
        </span>
      </div>
      
      <div className="card-body">
        <h3 className="event-title">{event.title}</h3>
        
        <div className="event-meta">
          <div className="meta-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12.667 2.667H3.333C2.597 2.667 2 3.264 2 4v9.333c0 .737.597 1.334 1.333 1.334h9.334c.736 0 1.333-.597 1.333-1.334V4c0-.736-.597-1.333-1.333-1.333zM2 6.667h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>{date}</span>
          </div>
          <div className="meta-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 14A6 6 0 1 0 8 2a6 6 0 0 0 0 12zM8 4.667V8l2 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>{time}</span>
          </div>
        </div>

        <div className="event-location">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 8.667A1.333 1.333 0 1 0 8 6a1.333 1.333 0 0 0 0 2.667z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M8 2C5.791 2 4 3.791 4 6c0 3 4 8 4 8s4-5 4-8c0-2.209-1.791-4-4-4z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>{event.location}</span>
        </div>
      </div>
      
      <div className="card-footer">
        <span className="view-link">View Details →</span>
      </div>
    </div>
  );
}