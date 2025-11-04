import { useEffect, useState } from "react";
import { subscribeToSimulationEvents } from "@/api/events";
import type { SimulationEvent } from "@/api/events";

interface Notification {
  id: string;
  message: string;
  type: "info" | "success" | "error";
}

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    const unsubscribe = subscribeToSimulationEvents((event: SimulationEvent) => {
      let message = "";
      let type: Notification["type"] = "info";

      switch (event.type) {
        case "simulation.started":
          message = `Simulation ${event.job_id} started`;
          break;
        case "simulation.progress":
          message = `Progress ${event.progress}%`;
          break;
        case "simulation.completed":
          message = `Simulation ${event.job_id} completed ✅`;
          type = "success";
          break;
        case "error":
          message = `Error: ${event.message}`;
          type = "error";
          break;
        default:
          message = JSON.stringify(event);
      }

      setNotifications((prev) => [
        { id: Date.now().toString(), message, type },
        ...prev.slice(0, 4),
      ]);
    });

    return () => unsubscribe.close();
  }, []);

  return (
    <div className="fixed top-4 right-4 space-y-2 z-50">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`rounded-xl px-4 py-2 shadow-md text-white ${
            n.type === "success"
              ? "bg-green-500"
              : n.type === "error"
              ? "bg-red-500"
              : "bg-blue-500"
          }`}
        >
          {n.message}
        </div>
      ))}
    </div>
  );
}
