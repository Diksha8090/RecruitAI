import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HiOutlineArrowLeft, HiOutlineCode, HiOutlineExternalLink,
  HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineShieldCheck,
  HiOutlineStar, HiOutlineChatAlt2, HiOutlineSparkles, HiOutlineLightningBolt
} from 'react-icons/hi';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import toast from 'react-hot-toast';
import Topbar from '../components/Topbar';
import { resumeAPI, analysisAPI, jobAPI, chatAPI } from '../services';

function ScoreRing({ value, size = 80, color = '#00D4AA', label }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(value || 0, 0), 100) / 100;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#21262D" strokeWidth={8} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={8}
          strokeDasharray={circ} strokeDashoffset={circ * (1 - pct)}
          strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s ease' }} />
      </svg>
      <p className="text-xl font-bold text-white" style={{ marginTop: -size * 0.6 - 8, lineHeight: 1 }}>{Math.round(value || 0)}</p>
      {label && <p className="text-xs text-gray-500 mt-1 text-center">{label}</p>}
    </div>
  );
}

function ProgressBar({ label, value, color = '#00D4AA' }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-gray-400">{label}</span>
        <span className="font-medium text-white">{Math.round(value || 0)}%</span>
      </div>
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${value || 0}%` }}
          transition={{ duration: 0.8, delay: 0.2 }}
          style={{ background: color }}
        />
      </div>
    </div>
  );
}

function CriteriaRow({ label, decision }) {
  if (!decision) return null;
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-dark-500 last:border-0">
      <div className={`mt-0.5 flex-shrink-0 ${decision.met ? 'text-emerald-400' : 'text-red-400'}`}>
        {decision.met ? <HiOutlineCheckCircle className="text-lg" /> : <HiOutlineXCircle className="text-lg" />}
      </div>
      <div>
        <p className="text-sm font-medium text-white capitalize">{label}</p>
        <p className="text-xs text-gray-500 mt-0.5">{decision.reason}</p>
      </div>
    </div>
  );
}

function ChatWidget({ resumeId }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! Ask me anything about this candidate — their skills, experience, fit for the role, or anything else.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', content: input };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await chatAPI.candidateChat(resumeId, [...messages, userMsg].filter(m => m.role !== 'assistant' || messages.indexOf(m) > 0));
      setMessages(m => [...m, { role: 'assistant', content: res.data.reply }]);
    } catch {
      setMessages(m => [...m, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card flex flex-col h-80">
      <div className="flex items-center gap-2 mb-3 pb-3 border-b border-dark-500">
        <HiOutlineChatAlt2 className="text-teal" />
        <p className="font-semibold text-white text-sm">Ask AI about this candidate</p>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] text-sm rounded-xl px-3.5 py-2.5 ${
              m.role === 'user'
                ? 'bg-teal text-dark-900 font-medium'
                : 'bg-dark-600 text-gray-300'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-1.5 px-3.5 py-2.5">
            {[0, 1, 2].map(i => (
              <div key={i} className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
            ))}
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask about skills, experience..." className="input text-sm py-2 flex-1" />
        <button onClick={send} disabled={loading || !input.trim()} className="btn-primary px-4 py-2">Send</button>
      </div>
    </div>
  );
}

export default function CandidateDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    Promise.all([resumeAPI.getById(id), jobAPI.getAll()])
      .then(([r, j]) => {
        setResume(r.data.resume);
        const analyses = r.data.resume?.analyses || [];
        if (analyses.length > 0) setAnalysis(analyses[0]);
        const jList = j.data.job_postings || [];
        setJobs(jList);
        if (jList.length > 0) setSelectedJob(String(jList[0].id));
      })
      .catch(() => toast.error('Failed to load candidate'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAnalyze = async () => {
    if (!selectedJob) return toast.error('Select a job first');
    setAnalyzing(true);
    try {
      const res = await analysisAPI.analyze({ resume_id: Number(id), job_posting_id: Number(selectedJob), force_reanalyze: true });
      setAnalysis(res.data.analysis);
      toast.success('Analysis complete!');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Candidate Details" />
        <div className="flex-1 p-6 space-y-4">
          {[...Array(4)].map((_, i) => <div key={i} className="card h-32 animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Not Found" />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-400 mb-4">Candidate not found</p>
            <button onClick={() => navigate('/candidates')} className="btn-primary">Back to Candidates</button>
          </div>
        </div>
      </div>
    );
  }

  const radarData = analysis ? [
    { subject: 'Skills', value: analysis.skills_match || 0 },
    { subject: 'Experience', value: analysis.experience_match || 0 },
    { subject: 'Education', value: analysis.education_match || 0 },
    { subject: 'GitHub', value: analysis.github_score || 0 },
    { subject: 'Overall', value: analysis.match_score || 0 },
  ] : [];

  const biasData = analysis?.bias_data || {};
  const githubData = analysis?.github_data || {};
  const criteriaData = analysis?.criteria_decisions || {};

  return (
    <div className="flex flex-col h-full">
      <Topbar title={resume.candidate_name || 'Candidate Details'} subtitle="Full AI analysis & profile" />

      <div className="flex-1 p-6 overflow-y-auto space-y-5">
        {/* Header card */}
        <div className="card">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/candidates')} className="w-9 h-9 flex items-center justify-center rounded-lg bg-dark-600 text-gray-400 hover:text-white transition-all">
                <HiOutlineArrowLeft />
              </button>
              <div className="w-14 h-14 bg-gradient-to-br from-teal to-brand-blue rounded-xl flex items-center justify-center">
                <span className="text-dark-900 font-bold text-xl">{(resume.candidate_name || '?')[0].toUpperCase()}</span>
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{resume.candidate_name || 'Unknown'}</h2>
                <p className="text-gray-500 text-sm">{resume.email}</p>
                {resume.phone && <p className="text-gray-500 text-xs">{resume.phone}</p>}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <select className="input text-sm py-2 w-48" value={selectedJob} onChange={e => setSelectedJob(e.target.value)}>
                {jobs.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
              </select>
              <motion.button whileTap={{ scale: 0.97 }} onClick={handleAnalyze} disabled={analyzing} className="btn-primary">
                {analyzing ? (
                  <><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg> Analyzing...</>
                ) : <><HiOutlineSparkles /> Analyze</>}
              </motion.button>
            </div>
          </div>
        </div>

        {analysis ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left column */}
            <div className="space-y-5">
              {/* Score rings */}
              <div className="card">
                <h3 className="font-semibold text-white mb-4">AI Scores</h3>
                <div className="grid grid-cols-2 gap-6 justify-items-center">
                  <div className="text-center">
                    <ScoreRing value={analysis.match_score} color="#00D4AA" />
                    <p className="text-xs text-gray-500 mt-2">Match Score</p>
                  </div>
                  <div className="text-center">
                    <ScoreRing value={(analysis.resume_rating || 0) * 10} color="#F59E0B" />
                    <p className="text-xs text-gray-500 mt-2">Rating {analysis.resume_rating}/10</p>
                  </div>
                  {analysis.github_score > 0 && (
                    <div className="text-center col-span-2">
                      <ScoreRing value={analysis.github_score} color="#8B5CF6" size={70} />
                      <p className="text-xs text-gray-500 mt-2">GitHub Score</p>
                    </div>
                  )}
                </div>
                <div className="mt-4 pt-4 border-t border-dark-500 text-center">
                  {analysis.category === 'Highly Qualified' && <span className="badge-high text-sm px-4">Highly Qualified</span>}
                  {analysis.category === 'Qualified' && <span className="badge-medium text-sm px-4">Qualified</span>}
                  {analysis.category === 'Not a Fit' && <span className="badge-low text-sm px-4">Not a Fit</span>}
                </div>
              </div>

              {/* Skills */}
              {analysis.skills_found?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-3">Skills Found</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.skills_found.map(s => (
                      <span key={s} className="bg-teal/10 border border-teal/30 text-teal text-xs px-2.5 py-1 rounded-full">{s}</span>
                    ))}
                  </div>
                  {analysis.skills_gap?.length > 0 && (
                    <>
                      <p className="text-xs font-medium text-gray-500 mt-3 mb-2">Skills Gap</p>
                      <div className="flex flex-wrap gap-1.5">
                        {analysis.skills_gap.map(s => (
                          <span key={s} className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs px-2.5 py-1 rounded-full">{s}</span>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Bias */}
              {biasData.bias_score !== undefined && (
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white flex items-center gap-2"><HiOutlineShieldCheck className="text-brand-purple" /> Bias Analysis</h3>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      biasData.overall_risk === 'Low' ? 'bg-emerald-500/20 text-emerald-400' :
                      biasData.overall_risk === 'Medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'
                    }`}>{biasData.overall_risk} Risk</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    {Object.entries(biasData.categories || {}).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between">
                        <span className="text-gray-400 capitalize">{key.replace('_bias', '').replace('_', ' ')}</span>
                        <span className={val.detected ? 'text-red-400' : 'text-emerald-400'}>{val.detected ? 'Detected' : 'Clear'}</span>
                      </div>
                    ))}
                  </div>
                  {biasData.recommendations?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-dark-500 space-y-1.5">
                      {biasData.recommendations.map((r, i) => (
                        <p key={i} className="text-xs text-gray-500">• {r}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Middle column */}
            <div className="space-y-5">
              {/* Summary */}
              <div className="card">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2"><HiOutlineSparkles className="text-teal" /> AI Summary</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{analysis.summary}</p>
              </div>

              {/* Score breakdown */}
              <div className="card">
                <h3 className="font-semibold text-white mb-4">Score Breakdown</h3>
                <div className="space-y-3">
                  <ProgressBar label="Skills Match" value={analysis.skills_match} color="#00D4AA" />
                  <ProgressBar label="Experience" value={analysis.experience_match} color="#F59E0B" />
                  <ProgressBar label="Education" value={analysis.education_match} color="#8B5CF6" />
                  {analysis.github_score > 0 && <ProgressBar label="GitHub" value={analysis.github_score} color="#3B82F6" />}
                </div>
              </div>

              {/* Strengths + Weaknesses */}
              <div className="card">
                <h3 className="font-semibold text-white mb-3">Strengths</h3>
                <ul className="space-y-2 mb-4">
                  {(analysis.strengths || []).map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <HiOutlineCheckCircle className="text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-300">{s}</span>
                    </li>
                  ))}
                </ul>
                <h3 className="font-semibold text-white mb-3">Weaknesses</h3>
                <ul className="space-y-2">
                  {(analysis.weaknesses || []).map((w, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <HiOutlineXCircle className="text-red-400 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-300">{w}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Criteria decisions */}
              {Object.keys(criteriaData).length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2"><HiOutlineLightningBolt className="text-brand-orange" /> Criteria Decisions</h3>
                  {Object.entries(criteriaData).map(([key, val]) => (
                    <CriteriaRow key={key} label={key} decision={val} />
                  ))}
                </div>
              )}
            </div>

            {/* Right column */}
            <div className="space-y-5">
              {/* Radar chart */}
              <div className="card">
                <h3 className="font-semibold text-white mb-4">Profile Radar</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#30363D" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#8B949E', fontSize: 11 }} />
                    <Radar dataKey="value" stroke="#00D4AA" fill="#00D4AA" fillOpacity={0.15} />
                    <Tooltip contentStyle={{ background: '#1C2333', border: '1px solid #30363D', borderRadius: 8, color: '#fff' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* GitHub */}
              {githubData.username && !githubData.error && (
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white flex items-center gap-2"><HiOutlineCode className="text-brand-purple" /> GitHub</h3>
                    <a href={githubData.url} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-teal hover:underline flex items-center gap-1">
                      {githubData.username} <HiOutlineExternalLink />
                    </a>
                  </div>
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {[
                      { label: 'Repos', value: githubData.public_repos },
                      { label: 'Stars', value: githubData.total_stars },
                      { label: 'Followers', value: githubData.followers },
                    ].map(({ label, value }) => (
                      <div key={label} className="text-center bg-dark-600 rounded-lg p-2">
                        <p className="text-lg font-bold text-white">{value}</p>
                        <p className="text-xs text-gray-500">{label}</p>
                      </div>
                    ))}
                  </div>
                  {githubData.languages && Object.keys(githubData.languages).length > 0 && (
                    <>
                      <p className="text-xs text-gray-500 mb-2">Languages</p>
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(githubData.languages).slice(0, 6).map(([lang, pct]) => (
                          <span key={lang} className="bg-brand-purple/10 border border-brand-purple/30 text-brand-purple text-xs px-2 py-0.5 rounded-full">
                            {lang} {pct}%
                          </span>
                        ))}
                      </div>
                    </>
                  )}
                  {githubData.top_repos?.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-gray-500">Top Repositories</p>
                      {githubData.top_repos.slice(0, 3).map(repo => (
                        <a key={repo.name} href={repo.url} target="_blank" rel="noopener noreferrer"
                          className="flex items-center justify-between p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-all">
                          <div>
                            <p className="text-xs font-medium text-white">{repo.name}</p>
                            {repo.description && <p className="text-xs text-gray-500 truncate max-w-[140px]">{repo.description}</p>}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <HiOutlineStar className="text-brand-orange" /> {repo.stars}
                          </div>
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Recommendations */}
              {analysis.recommendations?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-3">Recommendations</h3>
                  <ul className="space-y-2">
                    {analysis.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-teal font-bold flex-shrink-0">{i + 1}.</span>
                        <span className="text-gray-400">{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Chat */}
              <ChatWidget resumeId={id} />
            </div>
          </div>
        ) : (
          <div className="card text-center py-16">
            <HiOutlineSparkles className="text-5xl text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg font-medium mb-2">No analysis yet</p>
            <p className="text-sm text-gray-600 mb-6">Select a job and click Analyze to get AI insights</p>
            <button onClick={handleAnalyze} disabled={analyzing || !selectedJob} className="btn-primary mx-auto">
              <HiOutlineSparkles /> Run AI Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
