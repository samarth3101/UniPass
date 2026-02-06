"use client";

import { useState } from "react";
import CreateEventModal from "./create-event-modal";
import EventModal from "./event-modal";
import EventCard from "./event-card";

import "./events.scss";

type Event = {
  id: number;
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
};

type Props = {
  events: Event[];
  onRefresh: () => void;
};

export default function EventsClient({ events, onRefresh }: Props) {
  const [showCreate, setShowCreate] = useState(false);
  const [selected, setSelected] = useState<Event | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "upcoming" | "past" | "live">("all");

  const now = new Date();
  
  const filteredEvents = events.filter((event) => {
    const matchesSearch = event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         event.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (!matchesSearch) return false;
    
    if (filterStatus === "all") return true;
    
    const eventStart = new Date(event.start_time);
    const eventEnd = new Date(event.end_time);
    
    if (filterStatus === "live") return now >= eventStart && now <= eventEnd;
    if (filterStatus === "upcoming") return now < eventStart;
    if (filterStatus === "past") return eventEnd < now;
    
    return true;
  });

  return (
    <div className="events-page">
      <div className="events-header">
        <div className="header-content">
          <h1>Events</h1>
          <p className="subtitle">Manage all university events</p>
        </div>
        <button className="create-btn" onClick={() => setShowCreate(true)}>
          <span className="btn-icon">+</span>
          Create Event
        </button>
      </div>

      <div className="events-controls">
        <div className="search-box">
          <svg className="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM18 18l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <input
            type="text"
            placeholder="Search events by title or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-tabs">
          <button 
            className={`filter-tab ${filterStatus === "all" ? "active" : ""}`}
            onClick={() => setFilterStatus("all")}
          >
            All Events
          </button>
          <button 
            className={`filter-tab ${filterStatus === "upcoming" ? "active" : ""}`}
            onClick={() => setFilterStatus("upcoming")}
          >
            Upcoming
          </button>
          <button 
            className={`filter-tab ${filterStatus === "past" ? "active" : ""}`}
            onClick={() => setFilterStatus("past")}
          >
            Past
          </button>
          <button 
            className={`filter-tab ${filterStatus === "live" ? "active" : ""}`}
            onClick={() => setFilterStatus("live")}
          >
            Live
          </button>
        </div>
      </div>

      {filteredEvents.length > 0 ? (
        <div className="events-grid">
          {filteredEvents.map((e) => (
            <EventCard
              key={e.id}
              event={e}
              onClick={() => setSelected(e)}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <h3>No events found</h3>
          <p>
            {searchQuery || filterStatus !== "all"
              ? "Try adjusting your search or filters"
              : "Create your first event to get started"}
          </p>
          {!searchQuery && filterStatus === "all" && (
            <button className="empty-action" onClick={() => setShowCreate(true)}>
              Create Event
            </button>
          )}
        </div>
      )}

      {showCreate && (
        <CreateEventModal 
          onClose={() => {
            setShowCreate(false);
            onRefresh();
          }} 
        />
      )}

      {selected && (
        <EventModal
          event={selected}
          onClose={() => {
            setSelected(null);
            onRefresh();
          }}
        />
      )}
    </div>
  );
}