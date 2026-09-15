import { FormEvent, useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
type Job = { id: string; status: "queued" | "generating" | "rendering" | "completed" | "failed"; topic: string; error?: string; video_url?: string };
const subjects = ["General", "Mathematics", "Computer Science", "Physics", "Chemistry", "Biology", "Economics", "History"];
export default function App() {
    const [topic, setTopic] = useState(""); const [subject, setSubject] = useState("General"); const [quality, setQuality] = useState("Medium"); const [voice, setVoice] = useState("teaching_assistant"); const [voiceover, setVoiceover] = useState(true); const [job, setJob] = useState<Job | null>(null); const [feedback, setFeedback] = useState(""); const [requestError, setRequestError] = useState("");
    const working = !!job && ["queued", "generating", "rendering"].includes(job.status);
    async function api<T>(path: string, options?: RequestInit): Promise<T> {
        let response: Response;
        try { response = await fetch(`${API}${path}`, options); }
        catch { throw new Error(`Cannot reach the API at ${API}. Confirm the FastAPI server is running.`); }
        if (!response.ok) {
            const body = await response.json().catch(() => null);
            throw new Error(body?.detail ?? `API request failed (${response.status}).`);
        }
        return response.json() as Promise<T>;
    }
    useEffect(() => { if (!working || !job) return; const timer = setInterval(() => { api<Job>(`/api/lessons/${job.id}`).then(setJob).catch(error => setRequestError(error.message)) }, 2000); return () => clearInterval(timer) }, [job?.id, working]);
    async function create(e: FormEvent) { e.preventDefault(); setRequestError(""); try { setJob(await api<Job>("/api/lessons", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ topic, subject, quality, voice_preset: voice, use_voiceover: voiceover }) })); } catch (error) { setRequestError(error instanceof Error ? error.message : "Unable to create lesson."); } }
    async function regenerate() { if (!job || !feedback.trim()) return; setRequestError(""); try { setJob(await api<Job>(`/api/lessons/${job.id}/feedback`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ feedback }) })); setFeedback(""); } catch (error) { setRequestError(error instanceof Error ? error.message : "Unable to regenerate lesson."); } }
    return <main><header><small>ONLYSTUDIES</small><h1>Make difficult ideas<br />feel visual.</h1><p>Generate animated lessons with a clear explanation, analogy, and worked example.</p></header><section><form onSubmit={create}><label>What should we explain?<input required minLength={2} value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g. Newton's third law" /></label><div className="grid"><label>Subject<select value={subject} onChange={e => setSubject(e.target.value)}>{subjects.map(x => <option key={x}>{x}</option>)}</select></label><label>Quality<select value={quality} onChange={e => setQuality(e.target.value)}>{["Low", "Medium", "High"].map(x => <option key={x}>{x}</option>)}</select></label><label>Voice<select disabled={!voiceover} value={voice} onChange={e => setVoice(e.target.value)}>{["teaching_assistant", "professor", "enthusiastic", "calm", "neutral"].map(x => <option key={x}>{x.replace("_", " ")}</option>)}</select></label></div><label className="toggle"><input type="checkbox" checked={voiceover} onChange={e => setVoiceover(e.target.checked)} />Include voiceover</label><button disabled={working}>{working ? "Creating lesson…" : "Generate lesson"}</button></form>{requestError && <pre>{requestError}</pre>}</section>{job && <section><strong className={job.status}>{job.status === "completed" ? "Lesson ready" : `Status: ${job.status}`}</strong>{job.error && <pre>{job.error}</pre>}{job.status === "completed" && <><video controls src={`${API}${job.video_url}`} /><a href={`${API}${job.video_url}`}>Download MP4</a><label>Improve this lesson<textarea value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="For example: slow down the worked example." /></label><button onClick={regenerate}>Regenerate with feedback</button></>}</section>}</main>
}
