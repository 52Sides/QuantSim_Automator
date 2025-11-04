export type SimulationEvent =
  | { type: "simulation.started"; job_id: string }
  | { type: "simulation.progress"; job_id: string; progress: number }
  | { type: "simulation.completed"; job_id: string; result_id: number }
  | { type: "error"; message: string };

type EventCallback = (event: SimulationEvent) => void;

/**
 * Подключение к WebSocket /ws/simulations и подписка на события.
 * Возвращает объект с методами close() и reconnect().
 */
export function subscribeToSimulationEvents(onEvent: EventCallback) {
  const WS_URL =
    import.meta.env.VITE_API_URL?.replace(/^http/, "ws") +
    "/ws/simulations";

  let socket = new WebSocket(WS_URL);

  socket.onopen = () => console.log("🔌 WebSocket connected");
  socket.onmessage = (msg) => {
    try {
      const event = JSON.parse(msg.data);
      onEvent(event);
    } catch (e) {
      console.error("Invalid WS message:", e);
    }
  };
  socket.onclose = () => {
    console.warn("WebSocket closed, reconnecting in 3s...");
    setTimeout(() => subscribeToSimulationEvents(onEvent), 3000);
  };

  return {
    close: () => socket.close(),
  };
}
