"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { toast } from "@/components/Toast";

type Props = {
  onClose: () => void;
};

export default function CreateEventModal({ onClose }: Props) {
  const router = useRouter();

  const [form, setForm] = useState({
    title: "",
    description: "",
    location: "",
    start_time: "",
    end_time: "",
  });
  const [loading, setLoading] = useState(false);

  async function handleCreate() {
    // Validation
    if (!form.title.trim()) {
      toast.error("Event title is required");
      return;
    }
    if (!form.start_time || !form.end_time) {
      toast.error("Start and end times are required");
      return;
    }
    
    const startDate = new Date(form.start_time);
    const endDate = new Date(form.end_time);
    
    if (endDate <= startDate) {
      toast.error("End time must be after start time");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...form,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
      };
      
      await api.post("/events", payload);
      toast.success("Event created successfully");
      router.refresh();
      onClose();
    } catch (error: any) {
      console.error("Failed to create event:", error);
      toast.error(error.message || "Failed to create event");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal large" onClick={(e) => e.stopPropagation()}>
        <h2>Create New Event</h2>

        <input
          placeholder="Event Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />

        <textarea
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />

        <input
          placeholder="Location"
          value={form.location}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
        />

        <label>Start Time</label>
        <input
          type="datetime-local"
          value={form.start_time}
          onChange={(e) => setForm({ ...form, start_time: e.target.value })}
        />

        <label>End Time</label>
        <input
          type="datetime-local"
          value={form.end_time}
          onChange={(e) => setForm({ ...form, end_time: e.target.value })}
        />

        <div className="modal-actions">
          <button onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button
            className="primary"
            onClick={handleCreate}
            disabled={loading || !form.title || !form.start_time || !form.end_time}
          >
            {loading ? "Creating..." : "Create Event"}
          </button>
        </div>
      </div>
    </div>
  );
}