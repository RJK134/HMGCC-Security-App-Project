/** Notification bell icon with unread count and dropdown list. */

import { Bell, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../../stores/appStore";

interface Notification {
  id: string;
  message: string;
  topic: string;
  document_id: string;
  document_name: string;
  relevance_score: number;
  read: boolean;
}

export function NotificationBell() {
  const { currentProjectId } = useAppStore();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const fetchNotifications = useCallback(async () => {
    if (!currentProjectId) return;
    try {
      const res = await fetch(
        `/api/v1/notifications?project_id=${currentProjectId}`,
      );
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications ?? []);
      }
    } catch {
      /* ignore */
    }
  }, [currentProjectId]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60_000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Close on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const unread = notifications.filter((n) => !n.read).length;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        title="Notifications"
      >
        <Bell size={18} />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[9px] rounded-full flex items-center justify-center">
            {unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 w-80 bg-sra-card border border-sra-border rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          <div className="flex items-center justify-between px-3 py-2 border-b border-sra-border">
            <span className="text-xs font-semibold">Notifications</span>
            <button onClick={() => setOpen(false)}>
              <X size={12} />
            </button>
          </div>
          {notifications.length === 0 ? (
            <p className="px-3 py-4 text-xs text-sra-muted text-center">No notifications.</p>
          ) : (
            notifications.map((n) => (
              <button
                key={n.id}
                onClick={() => {
                  navigate(`/library/${n.document_id}`);
                  setOpen(false);
                }}
                className="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 dark:hover:bg-gray-800/50 border-b border-sra-border"
              >
                <p className="font-medium">{n.message}</p>
                <p className="text-sra-muted text-[10px] mt-0.5">
                  Topic: {n.topic} | Score: {(n.relevance_score * 100).toFixed(0)}%
                </p>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
