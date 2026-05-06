import { useEffect, useRef, useState } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [submittedStopCode, setsubmittedStopCode] = useState(null);
  const [data, setData] = useState(null);

  const wsRef = useRef(null);

  const url = `ws://localhost:8000/ws/bus/${submittedStopCode}`;

  useEffect(() => {
    if (!submittedStopCode) return; // No WebSocket yet

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      setData(JSON.parse(event.data));
      setLoading(false);
    };

    ws.onerror = () => {
      console.error("WebSocket error");
      setLoading(false);
    }

    ws.onclose = () => {
      console.log("WebSocket closed");
    }

    return () => ws.close();
  }, [submittedStopCode]);

  function handleSubmit(event) {
    event.preventDefault();
    if (!input) return;

    setData(null);
    setLoading(true);
    setsubmittedStopCode(input.trim());
    setInput("");
  }

  function handleClear(event) {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setData(null); // Clear any existing arrival info
    setsubmittedStopCode(null);
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900">
      <div className="mx-auto max-w-md space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            SG Bus Arrival Infomation
          </h1>
          <p className="text-sm text-slate-500">
            Refreshes every 10 seconds
          </p>
        </header>
        <form className="flex gap-2" onSubmit={handleSubmit}>
          <input 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Bus Stop Code"
            className="min-w-0 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-base shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="submit"
            className="rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white shadow-sm active:scale-95"
          >
            Send
          </button>
        </form>

        {loading && <p>loading...</p>}

        {data && (
          <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
            {loading && <p>loading...</p>}
            <div className="mb-4">
              <h2 className="text-2xl font-bold">{data.description}</h2>
              <h3 className="mt-1 text-sm font-medium text-slate-500">{data.stop_code}</h3>
            </div>
            <ul className="space-y-3">
              {data.next_arrivals.map((bus) => (
                <li
                  key={bus.service}
                  className="flex items-center justify-between rounded-xl bg-slate-100 px-4 py-3"
                >
                  <span className="text-lg font-bold">{bus.service}</span>
                  <span className="text-slate-600">in {bus.minutes} min</span>
                </li>
              ))}
            </ul>
            <button
              onClick={handleClear}
              className="mt-5 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 font-semibold text-slate-700 active:scale-95"
            >
                Clear
            </button>
          </section>
        )}
      </div>
    </main>
  )
}

export default App
