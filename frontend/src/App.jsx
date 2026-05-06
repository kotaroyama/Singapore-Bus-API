import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [submittedStopCode, setsubmittedStopCode] = useState(null);
  const [data, setData] = useState(null);
  const url = `ws://localhost:8000/ws/bus/${submittedStopCode}`;

  useEffect(() => {
    if (!submittedStopCode) return; // No WebSocket yet

    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
      setLoading(false);
      setData(JSON.parse(event.data));
    };

    ws.onerror = () => {
      console.error("WebSocket error");
      setLoading(false);
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

  function clearInfo(event) {
    setData(null); // Clear any existing arrival info
  }

  return (
    <>
      <h1>Bus Arrival Infomation System</h1>
      <p>Refreshes every 10 seconds</p>
      <form onSubmit={handleSubmit}>
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Bus Stop Code"
        />
        <button type="submit">Send</button>
      </form>

      {loading && <p>loading...</p>}

      <section>
        {data && (
          <>
            <h2>{data.description}</h2>
            <h3>{data.stop_code}</h3>
            <ul>
              {data.next_arrivals.map((bus) => (
                <li key={bus.service}>
                  {bus.service} in {bus.minutes} mins
                </li>
              ))}
            </ul>
            <button onClick={clearInfo}>Clear</button>
          </>
        )}
      </section>
    </>
  )


}

export default App
